"""
聊天服务
根据PRD_研究与聊天模块.md设计
提供消息发送、历史记录查询等功能

图谱架构：
- 公共领域图谱：domain:{domain}（所有用户共享的论文知识）
- 用户私有笔记：user:{user_id}:notes（用户主动添加的消息/笔记）
"""
import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import uuid4

from app.models.db_models import MessageRole
from app.core.graphiti_enhanced import get_enhanced_graphiti
from app.integrations.llm_client import LLMClient
from app.crud.session import SessionRepository
from app.crud.message import MessageRepository
from app.crud.paper import PaperRepository
from app.utils.group_id import get_search_group_ids
from app.services.profile_service import ProfileService

logger = logging.getLogger(__name__)


class ChatService:
    """
    聊天服务
    
    使用 Repository Pattern，通过构造函数注入所需的 Repository
    
    功能：
    - 发送消息并获取 AI 回复
    - 根据 session domains 从公共图谱检索相关知识
    - 解析论文并用 LLM 提取相关内容作为上下文
    - 用户画像个性化（调整回复风格）
    
    注意：消息不会自动添加到图谱，用户可通过 add-to-notes 主动添加。
    """

    def __init__(
        self,
        session_repo: SessionRepository,
        message_repo: MessageRepository,
        paper_repo: PaperRepository,
        profile_service: Optional[ProfileService] = None
    ):
        """
        初始化聊天服务
        
        Args:
            session_repo: 会话数据访问层
            message_repo: 消息数据访问层
            paper_repo: 论文数据访问层
            profile_service: 用户画像服务（用于个性化）
        """
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.paper_repo = paper_repo
        self.profile_service = profile_service
        self.llm_client = LLMClient()

    async def send_message(
        self,
        session_id: str,
        message: str,
        user_id: str,
        attached_papers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        发送消息 - REQ-CHAT-3
        核心处理流程：
        1. 验证session
        2. 保存用户消息
        3. 异步添加用户消息到图谱
        4. 生成context（来自图谱或论文）
        5. LLM生成回复
        6. 保存Agent消息
        7. 返回响应
        
        Args:
            session_id: 会话ID
            message: 用户消息
            user_id: 用户ID
            attached_papers: 附带的论文ID列表
            
        Returns:
            包含用户消息、Agent消息和状态的响应
        """
        attached_papers = attached_papers or []
        
        # 1. 验证session存在且属于该用户
        research_session = await self.session_repo.get_by_id_and_user(session_id, user_id)
        if not research_session:
            raise ValueError("SESSION_NOT_FOUND")
        
        # 2. 获取会话的domains
        domains = SessionRepository.parse_domains(research_session.domains)
        
        now = datetime.now(timezone.utc)
        
        # 3. 保存用户消息到MySQL
        user_msg_id = str(uuid4())
        await self.message_repo.create_message(
            message_id=user_msg_id,
            session_id=session_id,
            role=MessageRole.USER,
            content=message,
            attached_papers=attached_papers if attached_papers else None,
            created_at=now
        )
        
        # 4. 生成context
        if attached_papers:
            # 分支A：论文context（解析论文并提取相关内容）
            context_string, context_data = await self._generate_paper_context(
                attached_papers, message, user_id
            )
        else:
            # 分支B：图谱context
            context_string, context_data = await self._generate_graph_context(
                user_id, message, domains
            )
        
        # 5. 获取最近的历史消息
        recent_messages = await self.message_repo.get_recent(session_id, limit=10)
        history = MessageRepository.to_history_format(recent_messages)
        
        # 6. 获取用户画像（用于个性化）
        user_profile = None
        if self.profile_service:
            user_profile = await self.profile_service.get_user_profile(user_id)
        
        # 7. LLM生成回复（带用户画像）
        agent_response = await self.llm_client.chat_with_context(
            query=message,
            context=context_string,
            history=history,
            user_profile=user_profile
        )
        
        # 8. 异步更新用户画像（不阻塞响应）
        if self.profile_service:
            asyncio.create_task(
                self.profile_service.update_from_message(user_id, message, domains)
            )
        
        # 9. 保存Agent消息到MySQL
        agent_msg_id = str(uuid4())
        agent_now = datetime.now(timezone.utc)
        await self.message_repo.create_message(
            message_id=agent_msg_id,
            session_id=session_id,
            role=MessageRole.AGENT,
            content=agent_response,
            context_string=context_string,
            context_data=context_data,
            created_at=agent_now
        )
        
        # 9. 更新会话统计
        await self.session_repo.update_stats(session_id)
        
        logger.info(
            f"Chat message processed: user_msg={user_msg_id}, "
            f"agent_msg={agent_msg_id}, session={session_id}"
        )
        
        # 10. 返回响应
        return {
            "user_message": {
                "message_id": user_msg_id,
                "role": "user",
                "content": message,
                "attached_papers": attached_papers,
                "created_at": now.isoformat() + "Z"
            },
            "agent_message": {
                "message_id": agent_msg_id,
                "role": "agent",
                "content": agent_response,
                "context_string": context_string,
                "context_data": context_data,
                "created_at": agent_now.isoformat() + "Z"
            },
            "status": {
                "graph_updated": True,
                "papers_parsed": attached_papers,
                "community_updated": True
            }
        }

    async def _generate_graph_context(
        self,
        user_id: str,
        query: str,
        domains: List[str]
    ) -> tuple:
        """
        从图谱中检索生成context
        
        使用简化的 group_id 方案：
        - 公共领域图谱：domain:{domain}（所有用户共享）
        - 用户私有笔记：user:{user_id}:notes（可选）
        
        Args:
            user_id: 用户ID
            query: 用户查询
            domains: 研究领域列表（如 ["AI", "ML"]）
            
        Returns:
            (context_string, context_data) 元组
        """
        try:
            graphiti = await get_enhanced_graphiti()
            
            start_time = time.time()
            
            # 根据 domains 构建 group_ids（公共领域 + 用户笔记）
            group_ids = get_search_group_ids(
                user_id=user_id,
                domains=domains,
                include_user_notes=True
            )
            
            logger.info(
                f"🔍 Searching with group_ids: domains={domains} -> "
                f"group_ids={group_ids}"
            )
            
            # 使用Graphiti的search方法，传入 group_ids
            search_results = await graphiti.search(
                query=query,
                user_id=user_id,
                group_ids=group_ids,  # 按 domain 的 group_ids 过滤
                limit=10
            )
            
            search_time_ms = int((time.time() - start_time) * 1000)
            
            # 格式化context_string
            context_string = self._format_search_results_to_string(search_results, domains)
            
            # 构建context_data
            context_data = {
                "source": "graph",
                "domains_filtered": domains if domains else [],
                "group_ids_searched": group_ids,
                "search_results": [
                    {
                        "type": getattr(result, 'node_type', 'entity') if hasattr(result, 'node_type') else 'entity',
                        "uuid": getattr(result, 'uuid', str(uuid4())),
                        "name": getattr(result, 'name', 'Unknown'),
                        "snippet": str(getattr(result, 'fact', ''))[:200] if hasattr(result, 'fact') else '',
                        "relevance_score": getattr(result, 'score', 0.0) if hasattr(result, 'score') else 0.0,
                        "source": "Your research notes"
                    }
                    for result in search_results[:5]
                ] if search_results else [],
                "search_stats": {
                    "total_searched": len(search_results) if search_results else 0,
                    "total_returned": min(5, len(search_results)) if search_results else 0,
                    "search_time_ms": search_time_ms,
                    "group_ids_count": len(group_ids)
                }
            }
            
            return context_string, context_data
            
        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            return "", {
                "source": "graph",
                "domains_filtered": domains if domains else [],
                "group_ids_searched": [],
                "search_results": [],
                "search_stats": {
                    "total_searched": 0,
                    "total_returned": 0,
                    "search_time_ms": 0,
                    "group_ids_count": 0
                }
            }

    async def _generate_paper_context(
        self,
        paper_ids: List[str],
        query: str,
        user_id: str
    ) -> tuple:
        """
        从论文中生成context
        
        流程：
        1. 获取论文记录
        2. 如果论文未解析，则解析（检查重复）
        3. 使用 LLM 从解析内容中提取与用户消息相关的内容
        4. 异步将新解析的论文添加到公共图谱
        
        Args:
            paper_ids: 论文ID列表
            query: 用户查询
            user_id: 用户ID
            
        Returns:
            (context_string, context_data) 元组
        """
        from app.services.pdf_parser import PDFParser
        from app.models.db_models import PaperStatus
        
        start_time = time.time()
        papers_to_add_to_graph = []  # 新解析的论文，需要添加到公共图谱
        
        try:
            # 1. 获取论文记录
            papers = await self.paper_repo.get_by_ids(paper_ids, user_id)
            
            if not papers:
                return "", {
                    "source": "paper",
                    "search_results": [],
                    "search_stats": {
                        "total_searched": 0,
                        "total_returned": 0,
                        "search_time_ms": 0
                    }
                }
            
            context_parts = []
            search_results = []
            pdf_parser = PDFParser()
            
            for paper in papers:
                try:
                    parsed_content = paper.parsed_content
                    was_newly_parsed = False
                    
                    # 2. 如果论文未解析，则解析
                    if not parsed_content or paper.status != PaperStatus.PARSED:
                        parsed_content = await self._parse_paper_with_dedup(
                            paper, pdf_parser
                        )
                        was_newly_parsed = True
                    elif isinstance(parsed_content, str):
                        parsed_content = json.loads(parsed_content)
                    
                    if not parsed_content:
                        logger.warning(f"No parsed content for paper: {paper.id}")
                        continue
                    
                    # 标记新解析的论文，稍后添加到公共图谱
                    if was_newly_parsed and not paper.added_to_graph:
                        papers_to_add_to_graph.append(paper.id)
                    
                    # 3. 使用 LLM 提取与查询相关的内容
                    relevant_content = await self._extract_relevant_content(
                        parsed_content, query, paper.filename
                    )
                    
                    if relevant_content:
                        context_parts.append(relevant_content)
                        
                        search_results.append({
                            "type": "paper",
                            "uuid": paper.id,
                            "name": paper.filename,
                            "title": parsed_content.get("title", paper.filename),
                            "snippet": relevant_content[:300],
                            "relevance_score": 1.0,
                            "source": f"Paper: {paper.filename}"
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to process paper {paper.id}: {e}")
                    continue
            
            search_time_ms = int((time.time() - start_time) * 1000)
            
            if context_parts:
                context_string = "根据您附带的论文，找到以下相关信息：\n\n" + "\n\n---\n\n".join(context_parts)
            else:
                context_string = ""
            
            context_data = {
                "source": "paper",
                "search_results": search_results,
                "search_stats": {
                    "total_searched": len(papers),
                    "total_returned": len(search_results),
                    "search_time_ms": search_time_ms
                }
            }
            
            # 4. 异步将新解析的论文添加到公共图谱（不阻塞响应）
            if papers_to_add_to_graph:
                for paper_id in papers_to_add_to_graph:
                    asyncio.create_task(
                        self._add_paper_to_graph_async(paper_id, user_id)
                    )
            
            return context_string, context_data
            
        except Exception as e:
            logger.error(f"Paper context generation failed: {e}")
            return "", {
                "source": "paper",
                "search_results": [],
                "search_stats": {
                    "total_searched": 0,
                    "total_returned": 0,
                    "search_time_ms": 0
                }
            }

    async def _parse_paper_with_dedup(self, paper, pdf_parser) -> Optional[Dict]:
        """
        解析论文并检查重复
        
        流程：
        1. 解析第一页获取标题
        2. 检查数据库中是否已存在相同标题的论文
        3. 如果存在，使用已有的解析结果
        4. 如果不存在，继续解析完整论文
        
        Args:
            paper: 论文记录
            pdf_parser: PDF 解析器
            
        Returns:
            解析后的内容字典
        """
        from app.models.db_models import PaperStatus
        import os
        
        try:
            # 检查文件是否存在
            if not paper.file_path or not os.path.exists(paper.file_path):
                logger.error(f"Paper file not found: {paper.file_path}")
                return None
            
            # 读取文件
            with open(paper.file_path, 'rb') as f:
                file_bytes = f.read()
            
            # 解析论文
            logger.info(f"Parsing paper: {paper.filename}")
            parsed_content = await pdf_parser.parse(file_bytes, paper.filename)
            
            if not parsed_content:
                return None
            
            title = parsed_content.get("title", "")
            
            # 检查是否有重复（通过标题）
            if title:
                existing = await self.paper_repo.find_by_title(title)
                if existing and existing.id != paper.id and existing.parsed_content:
                    logger.info(f"Found duplicate paper by title: {title}")
                    # 使用已有的解析结果
                    parsed_content = existing.parsed_content
                    if isinstance(parsed_content, str):
                        parsed_content = json.loads(parsed_content)
            
            # 更新论文记录
            paper.parsed_content = parsed_content
            paper.status = PaperStatus.PARSED
            await self.paper_repo.update(paper)
            
            return parsed_content
            
        except Exception as e:
            logger.error(f"Failed to parse paper: {e}")
            paper.status = PaperStatus.FAILED
            paper.parse_error = str(e)
            await self.paper_repo.update(paper)
            return None

    async def _extract_relevant_content(
        self,
        parsed_content: Dict,
        query: str,
        filename: str
    ) -> str:
        """
        使用 LLM 从论文内容中提取与查询相关的内容
        
        Args:
            parsed_content: 解析后的论文内容
            query: 用户查询
            filename: 文件名
            
        Returns:
            与查询相关的内容摘要
        """
        try:
            title = parsed_content.get("title", filename)
            abstract = parsed_content.get("abstract", "")
            sections = parsed_content.get("sections", [])
            
            # 构建论文内容摘要（限制长度）
            paper_summary = f"标题: {title}\n\n摘要: {abstract}\n\n"
            
            for section in sections[:6]:  # 取前6个章节
                heading = section.get("heading", section.get("title", ""))
                content = section.get("content", "")[:800]
                paper_summary += f"## {heading}\n{content}\n\n"
            
            # 限制总长度
            if len(paper_summary) > 6000:
                paper_summary = paper_summary[:6000] + "..."
            
            # 使用 LLM 提取相关内容
            prompt = f"""请从以下论文内容中提取与用户问题最相关的信息。

用户问题：{query}

论文内容：
{paper_summary}

请提取并总结与用户问题最相关的内容（不超过800字）。如果论文内容与问题不太相关，请简要说明论文的主要内容。
只返回提取的内容，不要添加额外说明。"""

            relevant_content = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            return f"**{title}**\n\n{relevant_content}"
            
        except Exception as e:
            logger.error(f"Failed to extract relevant content: {e}")
            # 降级：返回摘要
            abstract = parsed_content.get("abstract", "")
            title = parsed_content.get("title", filename)
            return f"**{title}**\n\n{abstract[:500]}" if abstract else ""

    async def _add_paper_to_graph_async(
        self,
        paper_id: str,
        user_id: str
    ) -> None:
        """
        异步将论文添加到公共图谱（后台任务）
        
        调用 IngestService.add_paper_to_graph 将论文添加到公共图谱。
        
        Args:
            paper_id: 论文ID
            user_id: 用户ID
        """
        try:
            from app.services.ingest_service import IngestService
            
            ingest_service = IngestService(paper_repo=self.paper_repo)
            
            result = await ingest_service.add_paper_to_graph(
                paper_id=paper_id,
                user_id=user_id
            )
            
            logger.info(
                f"✅ Paper {paper_id} auto-added to public graph | "
                f"domains={result.get('domains')} | "
                f"episodes={result.get('episodes_added')}"
            )
            
        except Exception as e:
            logger.error(f"Failed to auto-add paper {paper_id} to graph: {e}")
            # 不抛出异常，允许主流程继续

    def _format_search_results_to_string(
        self, 
        results, 
        domains: Optional[List[str]] = None
    ) -> str:
        """
        格式化检索结果为context字符串
        
        Args:
            results: 搜索结果列表
            domains: 过滤的研究领域列表
            
        Returns:
            格式化的context字符串
        """
        if not results:
            return ""
        
        # 构建开头，说明检索范围
        if domains:
            domain_str = ", ".join(domains)
            context = f"根据您在 {domain_str} 领域的知识图谱检索，找到以下相关信息：\n\n"
        else:
            context = "根据您的知识图谱检索，找到以下相关信息：\n\n"
        
        for i, result in enumerate(results[:5], 1):
            name = getattr(result, 'name', 'Unknown')
            node_type = getattr(result, 'node_type', 'entity') if hasattr(result, 'node_type') else 'entity'
            fact = str(getattr(result, 'fact', ''))[:200] if hasattr(result, 'fact') else ''
            source = getattr(result, 'source', 'Your research notes') if hasattr(result, 'source') else 'Your research notes'
            
            context += f"{i}. {name} ({node_type})\n"
            context += f"   {fact}...\n"
            context += f"   (来源：{source})\n\n"
        
        return context

    async def get_history(
        self,
        session_id: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        order: str = "asc"
    ) -> Dict[str, Any]:
        """
        获取聊天历史 - REQ-CHAT-4
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            limit: 每页消息数
            offset: 偏移量
            order: 排序方式 (asc/desc)
            
        Returns:
            聊天历史数据
        """
        # 1. 验证session存在且属于该用户
        research_session = await self.session_repo.get_by_id_and_user(session_id, user_id)
        if not research_session:
            raise ValueError("SESSION_NOT_FOUND")
        
        # 2. 查询会话信息
        domains = SessionRepository.parse_domains(research_session.domains)
        
        session_info = {
            "title": research_session.title,
            "domains": domains,
            "created_at": research_session.created_at.isoformat() + "Z" if research_session.created_at else None
        }
        
        # 3. 查询消息
        messages, total = await self.message_repo.get_by_session(
            session_id=session_id,
            limit=limit,
            offset=offset,
            order=order
        )
        
        # 4. 格式化消息
        message_list = [MessageRepository.format_message(msg) for msg in messages]
        
        return {
            "session_id": session_id,
            "session_info": session_info,
            "messages": message_list,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }
