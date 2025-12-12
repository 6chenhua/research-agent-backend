"""
论文摄入服务
负责解析PDF论文并将内容添加到知识图谱
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.graphiti_enhanced import enhanced_graphiti
from app.services.pdf_parser import PDFParser
from app.models.db_models import Paper, PaperStatus
from graphiti_core.nodes import EpisodeType

logger = logging.getLogger(__name__)


class IngestService:
    """
    论文摄入服务（使用增强版 Graphiti 客户端）
    
    处理流程：
    1. 解析PDF文件（使用deepdoc）
    2. 提取元数据和章节
    3. 将每个章节作为Episode添加到Graphiti
    4. Graphiti自动进行实体抽取和关系构建
    5. 保存论文元数据到MySQL
    
    优化特性：
    - ✅ 使用全局单例客户端（资源高效）
    - ✅ 并发控制（每用户最多2个并发上传）
    - ✅ 超时保护（5分钟自动超时）
    - ✅ 详细日志和监控
    """

    def __init__(self, db: AsyncSession = None):
        self.parser = PDFParser()
        self.graph = enhanced_graphiti  # ← 使用增强版全局单例
        self.db = db

    async def ingest_pdf(
        self, 
        file: UploadFile, 
        user_id: str,
        group_id: Optional[str] = None
    ) -> Dict:
        """
        摄入PDF论文到知识图谱
        
        Args:
            file: 上传的PDF文件
            user_id: 用户ID
            group_id: 图谱命名空间ID，默认为用户命名空间
            
        Returns:
            包含paper_id, title, status等信息的字典
        """
        # 参数验证
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # 文件大小限制 (50MB)
        max_size = 50 * 1024 * 1024
        file_bytes = await file.read()
        if len(file_bytes) > max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds 50MB limit"
            )
        
        try:
            # Step 1: 解析PDF
            logger.info(f"Parsing PDF: {file.filename}")
            parsed_data = await self.parser.parse(file_bytes, file.filename)
            
            # Step 2: 生成paper_id
            paper_id = f"paper_{uuid.uuid4().hex[:12]}"
            
            # Step 3: 设置命名空间（用户图谱）
            if not group_id:
                group_id = f"user:{user_id}"
            
            # Step 4: 将章节内容作为Episodes添加到Graphiti（并发优化）
            logger.info(f"Adding {len(parsed_data['sections'])} sections to graph for paper: {parsed_data['title']}")
            
            # 并发添加episodes（提升性能）
            episode_results = await self._add_episodes_concurrent(
                parsed_data=parsed_data,
                paper_id=paper_id,
                user_id=user_id,
                group_id=group_id
            )
            
            # Step 5: 保存论文元数据到MySQL
            if self.db:
                await self._save_paper_metadata(
                    paper_id=paper_id,
                    parsed_data=parsed_data,
                    file_name=file.filename
                )
            
            logger.info(f"Successfully ingested paper: {paper_id}")
            
            return {
                "paper_id": paper_id,
                "title": parsed_data['title'],
                "authors": parsed_data.get('authors', []),
                "year": parsed_data.get('year'),
                "sections_count": len(parsed_data['sections']),
                "episodes_added": len(episode_results),
                "status": "success",
                "group_id": group_id
            }
            
        except Exception as e:
            logger.error(f"Ingestion failed for {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to ingest PDF: {str(e)}"
            )

    async def _add_episodes_concurrent(
        self,
        parsed_data: Dict,
        paper_id: str,
        user_id: str,
        group_id: str,
        max_concurrent: int = 3
    ) -> List:
        """
        并发添加多个episodes到Graphiti
        
        优化说明：
        - 使用asyncio.Semaphore控制并发数量
        - 避免同时发起过多请求压垮Graphiti/Neo4j
        - 保持错误处理，失败的episode不影响其他episode
        
        Args:
            parsed_data: 解析后的论文数据
            paper_id: 论文ID
            user_id: 用户ID
            group_id: 图谱命名空间
            max_concurrent: 最大并发数（默认3，可根据服务器性能调整）
            
        Returns:
            成功添加的episode结果列表
        """
        import asyncio
        
        sections = parsed_data['sections']
        semaphore = asyncio.Semaphore(max_concurrent)
        episode_results = []
        
        async def add_single_episode(idx: int, section: Dict):
            """添加单个episode（带并发控制）"""
            async with semaphore:  # 控制并发数量
                try:
                    # 构建Episode内容
                    episode_content = self._build_episode_content(
                        paper_id=paper_id,
                        title=parsed_data['title'],
                        section=section,
                        section_idx=idx
                    )
                    
                    logger.info(
                        f"  [{idx+1}/{len(sections)}] Adding section: "
                        f"{section.get('heading', 'N/A')[:30]}... "
                        f"(content: {len(episode_content)} chars)"
                    )
                    
                    # 调用Graphiti.add_episode
                    result = await self.graph.add_episode(
                        episode_body=episode_content,
                        user_id=user_id,
                        group_id=group_id,
                        name=f"{paper_id}_section_{idx+1}",
                        source=EpisodeType.text,
                        source_description=f"Section {idx+1} from paper: {parsed_data['title']}",
                        reference_time=datetime.utcnow(),
                        timeout=300.0
                    )
                    
                    logger.info(f"  ✅ [{idx+1}/{len(sections)}] Section added successfully")
                    return result
                    
                except Exception as e:
                    logger.error(
                        f"  ❌ [{idx+1}/{len(sections)}] Failed to add section: {str(e)}",
                        exc_info=True
                    )
                    return None  # 返回None表示失败
        
        # 创建所有任务
        tasks = [
            add_single_episode(idx, section)
            for idx, section in enumerate(sections)
        ]
        
        # 并发执行所有任务
        logger.info(f"🚀 Starting concurrent upload with max_concurrent={max_concurrent}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤成功的结果
        episode_results = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        success_count = len(episode_results)
        total_count = len(sections)
        logger.info(
            f"📊 Episode upload complete: {success_count}/{total_count} succeeded, "
            f"{total_count - success_count} failed"
        )
        
        return episode_results
    
    def _build_episode_content(
        self,
        paper_id: str,
        title: str,
        section: Dict,
        section_idx: int
    ) -> str:
        """
        构建Episode内容
        
        将章节内容格式化为适合Graphiti处理的文本
        """
        heading = section.get('heading', f'Section {section_idx + 1}')
        content = section.get('content', '')
        
        # 构建结构化的Episode内容
        episode_text = f"""
Paper Title: {title}
Paper ID: {paper_id}
Section: {heading}

{content}
""".strip()
        
        return episode_text

    async def _save_paper_metadata(
        self, 
        paper_id: str, 
        parsed_data: Dict,
        file_name: str
    ):
        """
        更新论文解析内容到MySQL
        """
        try:
            result = await self.db.execute(
                select(Paper).filter(Paper.id == paper_id)
            )
            paper = result.scalar_one_or_none()
            
            if paper:
                paper.parsed_content = parsed_data
                paper.status = PaperStatus.PARSED
                paper.parsed_at = datetime.utcnow()
                await self.db.commit()
                logger.info(f"Updated paper parsed content: {paper_id}")
            else:
                logger.warning(f"Paper not found for metadata update: {paper_id}")
            
        except Exception as e:
            logger.error(f"Failed to save metadata: {str(e)}")
            await self.db.rollback()
            # 不抛出异常，因为主要逻辑（图谱摄入）已完成

    async def get_paper_detail(
        self, 
        paper_id: str,
        user_id: str,
        group_id: Optional[str] = None
    ) -> Dict:
        """
        获取论文详情
        
        包含：
        1. MySQL中的元数据
        2. 图谱中的实体和关系
        3. 相关论文推荐
        
        Args:
            paper_id: 论文ID
            user_id: 用户ID
            group_id: 命名空间
            
        Returns:
            论文详情字典
        """
        if not group_id:
            group_id = f"user:{user_id}"
        
        # Step 1: 从MySQL获取论文信息
        paper = None
        if self.db:
            result = await self.db.execute(
                select(Paper).filter(Paper.id == paper_id)
            )
            paper = result.scalar_one_or_none()
        
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # 从parsed_content中提取元数据
        parsed_content = paper.parsed_content or {}
        title = parsed_content.get('title', paper.filename)
        
        # Step 2: 从图谱获取相关实体
        try:
            # 搜索与论文相关的节点
            search_results = await self.graph.search(
                query=title,
                group_id=group_id,
                limit=20
            )
            
            # 提取实体
            entities = self._extract_entities_from_search(search_results)
            
            # Step 3: 推荐相关论文（基于图谱搜索）
            related_papers = await self._find_related_papers(
                paper_id=paper_id,
                group_id=group_id,
                limit=5
            )
            
            return {
                "paper_id": paper_id,
                "title": title,
                "authors": parsed_content.get('authors', []),
                "abstract": parsed_content.get('abstract', ''),
                "year": parsed_content.get('metadata', {}).get('publication_year'),
                "venue": parsed_content.get('metadata', {}).get('conference'),
                "filename": paper.filename,
                "domain": paper.domain,
                "status": paper.status.value if paper.status else None,
                "added_to_graph": paper.added_to_graph,
                "entities": entities,
                "related_papers": related_papers,
                "created_at": paper.created_at.isoformat() if paper.created_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get paper detail: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve paper details: {str(e)}"
            )

    def _extract_entities_from_search(self, search_results: list) -> list:
        """
        从搜索结果中提取实体信息
        """
        entities = []
        for result in search_results[:10]:  # 限制返回数量
            if hasattr(result, 'node') and result.node:
                node = result.node
                entities.append({
                    "uuid": getattr(node, 'uuid', ''),
                    "name": getattr(node, 'name', ''),
                    "type": getattr(node, 'labels', ['Unknown'])[0] if hasattr(node, 'labels') else 'Unknown',
                    "summary": getattr(node, 'summary', '')
                })
        return entities

    async def _find_related_papers(
        self, 
        paper_id: str, 
        group_id: str, 
        limit: int = 5
    ) -> list:
        """
        基于图谱查找相关论文
        """
        try:
            # 使用论文ID作为查询，找到相关节点
            results = await self.graph.search(
                query=paper_id,
                group_id=group_id,
                limit=limit * 2  # 多拿一些，过滤后再返回
            )
            
            related = []
            for result in results:
                if hasattr(result, 'node') and result.node:
                    node = result.node
                    # 如果是Paper类型的节点
                    if 'Paper' in getattr(node, 'labels', []):
                        related.append({
                            "paper_id": getattr(node, 'uuid', ''),
                            "title": getattr(node, 'name', ''),
                            "relevance_score": getattr(result, 'score', 0.0)
                        })
            
            return related[:limit]
            
        except Exception as e:
            logger.warning(f"Failed to find related papers: {str(e)}")
            return []