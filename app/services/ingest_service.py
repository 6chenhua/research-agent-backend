"""
论文摄入服务
负责解析PDF论文并将内容添加到知识图谱

使用统一的实体类型和关系类型：
- 实体类型：Paper, Method, Dataset, Task, Metric, Author, Institution, Concept
- 关系类型：PROPOSES, EVALUATES_ON, SOLVES, IMPROVES_OVER, CITES, 等
- 直接使用 entities.py 和 relations.py 中的规范定义
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from fastapi import UploadFile, HTTPException
import os

from app.core.graphiti_enhanced import enhanced_graphiti
from app.services.pdf_parser import PDFParser
from app.crud.paper import PaperRepository
from graphiti_core.nodes import EpisodeType
from app.utils.entity_types import get_entity_types, get_relation_types
from app.core.config import settings
from app.models.db_models import Paper, PaperStatus

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
    - ✅ 使用 Repository Pattern
    """

    def __init__(self, paper_repo: Optional[PaperRepository] = None):
        """
        初始化论文摄入服务
        
        Args:
            paper_repo: 论文数据访问层（可选）
        """
        self.parser = PDFParser()
        self.graph = enhanced_graphiti  # ← 使用增强版全局单例
        self.paper_repo = paper_repo

    async def upload_paper(
        self,
        file: UploadFile,
        user_id: str
    ) -> Dict:
        """
        上传论文PDF（只保存，不解析）
        
        Args:
            file: 上传的PDF文件
            user_id: 用户ID
            
        Returns:
            包含 paper_id, filename, file_size, status 的字典
            
        Raises:
            HTTPException: 文件格式或大小无效
        """

        
        # 验证文件格式
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # 读取文件并验证大小
        file_bytes = await file.read()
        max_size = 50 * 1024 * 1024  # 50MB
        
        if len(file_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({len(file_bytes) / 1024 / 1024:.1f}MB) exceeds 50MB limit"
            )
        
        # 生成唯一文件名和保存路径
        paper_id = f"paper_{uuid.uuid4().hex[:12]}"
        safe_filename = f"{paper_id}_{file.filename}"
        
        # 确保上传目录存在
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, safe_filename)
        
        # 保存文件到磁盘
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
        
        logger.info(f"📄 File saved: {file_path}")
        
        # 创建数据库记录
        if not self.paper_repo:
            raise HTTPException(status_code=500, detail="Paper repository not available")
        
        paper = Paper(
            id=paper_id,
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(file_bytes),
            status=PaperStatus.UPLOADED,
            domains=None,
            parsed_content=None,
            created_at=datetime.utcnow()
        )
        
        await self.paper_repo.create(paper)
        
        logger.info(f"✅ Paper uploaded: {paper_id} ({file.filename})")
        
        return {
            "paper_id": paper_id,
            "filename": file.filename,
            "file_size": len(file_bytes),
            "status": "uploaded",
            "message": "Paper uploaded successfully. It will be parsed when used in chat."
        }
    
    def _build_episode_content(
        self,
        paper_id: str,
        title: str,
        section: Dict,
        section_idx: int,
        domain: str = "General"
    ) -> str:
        """
        构建Episode内容
        
        将章节内容格式化为适合Graphiti处理的文本。
        
        设计原则：
        1. 不按 section 类型区分实体类型，让 LLM 根据内容自动判断
        2. Section 标题作为上下文提示，帮助 LLM 理解内容性质
        3. 包含 domain 信息以帮助 LLM 更准确地提取领域实体
        
        Args:
            paper_id: 论文ID
            title: 论文标题
            section: 章节数据
            section_idx: 章节索引
            domain: 论文所属领域
            
        Returns:
            格式化的 episode 内容
        """
        heading = section.get('heading', f'Section {section_idx + 1}')
        content = section.get('content', '')
        
        # 标准化 section 类型描述（帮助 LLM 理解上下文）
        section_context = self._get_section_context_hint(heading)
        
        # 构建结构化的Episode内容
        # 这个格式设计是为了让 Graphiti 的 LLM 更好地理解上下文
        episode_text = f"""
[Research Paper Context]
Domain: {domain}
Paper: {title}
Section: {heading}
{section_context}

[Content]
{content}
""".strip()
        
        return episode_text
    
    def _get_section_context_hint(self, heading: str) -> str:
        """
        根据 section 标题生成上下文提示
        
        这不是用来区分实体类型的，而是给 LLM 一个提示，
        帮助它理解当前内容的性质。
        
        Args:
            heading: section 标题
            
        Returns:
            上下文提示字符串
        """
        heading_lower = heading.lower()
        
        # 定义 section 类型和对应的上下文提示
        section_hints = {
            # 摘要类
            ("abstract",): "This section provides a high-level summary of the paper's contributions and findings.",
            
            # 引言类
            ("introduction", "intro"): "This section introduces the problem, motivation, and overview of the approach.",
            
            # 相关工作类
            ("related work", "background", "literature", "prior work", "previous work"): 
                "This section discusses existing methods and compares them to the proposed approach.",
            
            # 方法类
            ("method", "approach", "methodology", "proposed", "framework", "architecture", "model", "algorithm"):
                "This section describes the proposed method, model, or algorithm in detail.",
            
            # 实验类
            ("experiment", "evaluation", "result", "empirical", "analysis"):
                "This section presents experimental setup, results, and analysis.",
            
            # 讨论类
            ("discussion", "limitation", "future work", "conclusion"):
                "This section discusses findings, limitations, and future directions.",
            
            # 实现类
            ("implementation", "setup", "configuration", "training"):
                "This section describes implementation details and experimental setup.",
        }
        
        # 匹配 section 类型
        for keywords, hint in section_hints.items():
            if any(kw in heading_lower for kw in keywords):
                return f"Context: {hint}"
        
        # 默认提示
        return "Context: General content from the paper."

    async def add_paper_to_graph(
        self,
        paper_id: str,
        user_id: str
    ) -> Dict:
        """
        将已解析的论文添加到知识图谱
        
        这是用户触发的操作，流程：
        1. 从数据库获取论文信息（必须已解析）
        2. 使用 LLM 分析 abstract 识别 domains
        3. 为每个 domain 构建 group_id 并添加到图谱
        4. 使用统一的实体类型和关系类型
        5. 更新数据库状态
        
        Args:
            paper_id: 论文ID
            user_id: 用户ID
            
        Returns:
            包含 domains, episodes_added, status 等信息的字典
            
        Raises:
            HTTPException: 论文不存在或未解析
        """
        from app.services.domain_analyzer import DomainAnalyzer
        from app.utils.group_id import get_paper_ingest_group_ids
        
        # Step 1: 获取论文信息
        if not self.paper_repo:
            raise HTTPException(status_code=500, detail="Paper repository not available")
        
        paper = await self.paper_repo.get_by_id(paper_id)
        
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        if paper.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if paper.status != PaperStatus.PARSED:
            raise HTTPException(
                status_code=400, 
                detail=f"Paper must be parsed first. Current status: {paper.status}"
            )
        
        if paper.added_to_graph:
            raise HTTPException(
                status_code=400, 
                detail="Paper already added to graph"
            )
        
        # Step 2: 获取解析内容
        parsed_content = paper.parsed_content
        if not parsed_content:
            raise HTTPException(status_code=400, detail="Paper has no parsed content")
        
        abstract = parsed_content.get('abstract', '')
        title = parsed_content.get('title', paper.filename)
        sections = parsed_content.get('sections', [])
        
        if not abstract and not sections:
            raise HTTPException(status_code=400, detail="Paper has no content to add")
        
        # Step 3: 使用 LLM 分析 domains
        logger.info(f"Analyzing domains for paper: {paper_id}")
        domain_analyzer = DomainAnalyzer()
        domains = await domain_analyzer.analyze_domains(abstract, title)
        
        logger.info(f"Identified domains: {domains}")
        
        # Step 4: 获取统一的实体类型和关系类型
        # 直接使用 entities.py 和 relations.py 中的规范定义
        entity_types = get_entity_types()
        relation_types = get_relation_types()
        
        # Step 5: 添加到公共领域图谱
        # 所有论文进入公共图谱（domain:{domain}），实现知识共享
        all_episode_ids = []
        group_ids = get_paper_ingest_group_ids(domains)
        
        logger.info(f"Adding paper to public graph: group_ids={group_ids}")
        
        for group_id in group_ids:
            domain = group_id.replace("domain:", "").upper()
            
            # 添加每个 section
            for idx, section in enumerate(sections):
                try:
                    episode_content = self._build_episode_content(
                        paper_id=paper_id,
                        title=title,
                        section=section,
                        section_idx=idx,
                        domain=domain
                    )
                    
                    result = await self.graph.add_episode(
                        episode_body=episode_content,
                        user_id=user_id,  # 记录上传者，但数据进入公共图谱
                        group_id=group_id,
                        name=f"{paper_id}_{domain}_section_{idx+1}",
                        source=EpisodeType.text,
                        source_description=f"[{domain}] {title}",
                        reference_time=datetime.utcnow(),
                        entity_types=entity_types,
                        edge_types=relation_types,
                        timeout=300.0
                    )
                    
                    if result:
                        all_episode_ids.append(str(result) if result else f"{paper_id}_{domain}_{idx}")
                        
                except Exception as e:
                    logger.error(f"Failed to add section {idx} for domain {domain}: {e}")
                    # 继续处理其他 section
        
        # Step 6: 更新数据库状态
        try:
            paper.added_to_graph = True
            paper.domains = domains
            paper.graph_episode_ids = all_episode_ids
            paper.added_to_graph_at = datetime.utcnow()
            
            await self.paper_repo.update(paper)
            
            logger.info(f"✅ Paper {paper_id} added to graph with domains: {domains}")
            
        except Exception as e:
            logger.error(f"Failed to update paper status: {e}")
        
        return {
            "paper_id": paper_id,
            "title": title,
            "domains": domains,
            "sections_count": len(sections),
            "episodes_added": len(all_episode_ids),
            "added_to_graph": True,
            "status": "success"
        }
