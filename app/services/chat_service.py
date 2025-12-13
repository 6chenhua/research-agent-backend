"""
聊天服务
根据PRD_研究与聊天模块.md设计
提供消息发送、历史记录查询等功能
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
from graphiti_core.nodes import EpisodeType

logger = logging.getLogger(__name__)


class ChatService:
    """
    聊天服务
    
    使用 Repository Pattern，通过构造函数注入所需的 Repository
    """

    def __init__(
        self,
        session_repo: SessionRepository,
        message_repo: MessageRepository,
        paper_repo: PaperRepository
    ):
        """
        初始化聊天服务
        
        Args:
            session_repo: 会话数据访问层
            message_repo: 消息数据访问层
            paper_repo: 论文数据访问层
        """
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.paper_repo = paper_repo
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
        
        # 4. 异步将用户消息添加到图谱（不阻塞响应）
        asyncio.create_task(
            self._add_user_message_to_graph(user_id, message, session_id)
        )
        
        # 5. 生成context
        if attached_papers:
            # 分支A：论文context
            context_string, context_data = await self._generate_paper_context(
                attached_papers, message, user_id
            )
        else:
            # 分支B：图谱context
            context_string, context_data = await self._generate_graph_context(
                user_id, message, domains
            )
        
        # 6. 获取最近的历史消息
        recent_messages = await self.message_repo.get_recent(session_id, limit=10)
        history = MessageRepository.to_history_format(recent_messages)
        
        # 7. LLM生成回复
        agent_response = await self.llm_client.chat_with_context(
            query=message,
            context=context_string,
            history=history
        )
        
        # 8. 保存Agent消息到MySQL
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

    async def _add_user_message_to_graph(
        self,
        user_id: str,
        message: str,
        session_id: str
    ):
        """
        将用户消息添加到图谱（异步后台任务）
        
        Args:
            user_id: 用户ID
            message: 用户消息
            session_id: 会话ID
        """
        try:
            graphiti = await get_enhanced_graphiti()
            
            # 使用message格式添加到图谱
            episode_body = f"User: {message}"
            
            await graphiti.add_episode(
                episode_body=episode_body,
                user_id=user_id,
                group_id=user_id,  # 使用user_id作为命名空间
                name=f"user_query_{session_id}_{int(time.time())}",
                source=EpisodeType.message,
                source_description=f"User query in research session {session_id}",

            )
            
            logger.info(f"User message added to graph for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to add message to graph: {e}")
            # 不抛出异常，允许聊天继续

    async def _generate_graph_context(
        self,
        user_id: str,
        query: str,
        domains: List[str]
    ) -> tuple:
        """
        从图谱中检索生成context
        
        Args:
            user_id: 用户ID
            query: 用户查询
            domains: 研究领域
            
        Returns:
            (context_string, context_data) 元组
        """
        try:
            graphiti = await get_enhanced_graphiti()
            
            start_time = time.time()
            
            # 使用Graphiti的search方法
            search_results = await graphiti.search(
                query=query,
                user_id=user_id,
                group_id=user_id,  # 指定用户命名空间
                limit=10
            )
            
            search_time_ms = int((time.time() - start_time) * 1000)
            
            # 格式化context_string
            context_string = self._format_search_results_to_string(search_results)
            
            # 构建context_data
            context_data = {
                "source": "graph",
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
                    "search_time_ms": search_time_ms
                }
            }
            
            return context_string, context_data
            
        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            return "", {
                "source": "graph",
                "search_results": [],
                "search_stats": {
                    "total_searched": 0,
                    "total_returned": 0,
                    "search_time_ms": 0
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
        
        Args:
            paper_ids: 论文ID列表
            query: 用户查询
            user_id: 用户ID
            
        Returns:
            (context_string, context_data) 元组
        """
        try:
            # 查询论文信息
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
            
            # 提取论文内容作为context
            context_parts = []
            search_results = []
            
            for paper in papers:
                # 获取解析后的内容
                parsed_content = paper.parsed_content
                if isinstance(parsed_content, str):
                    parsed_content = json.loads(parsed_content)
                
                if parsed_content:
                    # 提取sections作为context
                    sections = parsed_content.get("sections", [])
                    paper_context = f"论文: {paper.filename}\n"
                    
                    for section in sections[:5]:  # 取前5个section
                        section_title = section.get("title", "")
                        section_content = section.get("content", "")[:500]
                        paper_context += f"\n## {section_title}\n{section_content}...\n"
                    
                    context_parts.append(paper_context)
                    
                    search_results.append({
                        "type": "paper",
                        "uuid": paper.id,
                        "name": paper.filename,
                        "snippet": paper_context[:200],
                        "relevance_score": 1.0,
                        "source": f"Paper: {paper.filename}"
                    })
            
            context_string = "根据您附带的论文，找到以下相关信息：\n\n" + "\n".join(context_parts)
            
            context_data = {
                "source": "paper",
                "search_results": search_results,
                "search_stats": {
                    "total_searched": len(papers),
                    "total_returned": len(papers),
                    "search_time_ms": 0
                }
            }
            
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

    def _format_search_results_to_string(self, results) -> str:
        """
        格式化检索结果为context字符串
        
        Args:
            results: 搜索结果列表
            
        Returns:
            格式化的context字符串
        """
        if not results:
            return ""
        
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
