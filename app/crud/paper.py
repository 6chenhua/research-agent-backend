"""
论文 Repository
处理 papers 表的所有数据库操作
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, NamedTuple
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Paper, PaperStatus
from app.crud.base import BaseRepository


class PaperRepository(BaseRepository[Paper]):
    """
    论文数据访问层
    
    使用示例:
    ```python
    paper_repo = PaperRepository(db_session)
    paper = await paper_repo.get_by_id(paper_id)
    ```
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Paper)
    
    async def get_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        根据ID查询论文
        
        Args:
            paper_id: 论文ID
            
        Returns:
            论文对象或 None
        """
        result = await self.session.execute(
            select(Paper).where(Paper.id == paper_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ids(
        self,
        paper_ids: List[str],
        user_id: str
    ) -> List[Paper]:
        """
        根据ID列表查询论文（带用户过滤）
        
        Args:
            paper_ids: 论文ID列表
            user_id: 用户ID
            
        Returns:
            论文列表
        """
        query = (
            select(Paper)
            .where(
                Paper.id.in_(paper_ids),
                Paper.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_user(
        self,
        user_id: str,
        status: Optional[PaperStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Paper]:
        """
        获取用户的论文列表
        
        Args:
            user_id: 用户ID
            status: 论文状态筛选（可选）
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            论文列表
        """
        query = select(Paper).where(Paper.user_id == user_id)
        
        if status:
            query = query.where(Paper.status == status)
            
        query = (
            query
            .order_by(Paper.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_parsed_content(
        self,
        paper_id: str,
        parsed_content: Dict[str, Any],
        status: PaperStatus = PaperStatus.PARSED
    ) -> Optional[Paper]:
        """
        更新论文解析内容
        
        Args:
            paper_id: 论文ID
            parsed_content: 解析后的内容
            status: 解析状态
            
        Returns:
            更新后的论文对象或 None
        """
        paper = await self.get_by_id(paper_id)
        
        if paper:
            paper.parsed_content = parsed_content
            paper.status = status
            paper.parsed_at = datetime.utcnow()
            await self.session.flush()
            
        return paper
    
    async def update_graph_status(
        self,
        paper_id: str,
        added_to_graph: bool = True,
        episode_ids: Optional[List[str]] = None
    ) -> Optional[Paper]:
        """
        更新论文的图谱状态
        
        Args:
            paper_id: 论文ID
            added_to_graph: 是否已添加到图谱
            episode_ids: Episode ID列表
            
        Returns:
            更新后的论文对象或 None
        """
        paper = await self.get_by_id(paper_id)
        
        if paper:
            paper.added_to_graph = added_to_graph
            paper.graph_episode_ids = episode_ids
            paper.added_to_graph_at = datetime.utcnow() if added_to_graph else None
            await self.session.flush()
            
        return paper
    
    async def update_status(
        self,
        paper_id: str,
        status: PaperStatus,
        error: Optional[str] = None
    ) -> Optional[Paper]:
        """
        更新论文解析状态
        
        Args:
            paper_id: 论文ID
            status: 解析状态
            error: 错误信息（如果失败）
            
        Returns:
            更新后的论文对象或 None
        """
        paper = await self.get_by_id(paper_id)
        
        if paper:
            paper.status = status
            if error:
                paper.parse_error = error
            await self.session.flush()
            
        return paper
    
    async def find_by_title(self, title: str) -> Optional[Paper]:
        """通过论文标题查找（用于去重检测）"""
        query = (
            select(Paper)
            .where(
                Paper.status == PaperStatus.PARSED,
                func.json_unquote(
                    func.json_extract(Paper.parsed_content, '$.title')
                ) == title
            )
            .limit(1)
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_stats_by_user(self, user_id: str) -> Dict[str, int]:
        """
        获取用户的论文统计数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计数据字典，包含:
            - total_uploaded: 已上传论文数量
            - total_parsed: 已解析论文数量
            - added_to_graph: 已添加到图谱的论文数量
        """
        query = select(
            func.count(Paper.id).label("total_uploaded"),
            func.sum(
                case((Paper.status == PaperStatus.PARSED, 1), else_=0)
            ).label("total_parsed"),
            func.sum(
                case((Paper.added_to_graph == True, 1), else_=0)
            ).label("added_to_graph")
        ).where(Paper.user_id == user_id)
        
        result = await self.session.execute(query)
        row = result.one()
        
        return {
            "total_uploaded": row.total_uploaded or 0,
            "total_parsed": int(row.total_parsed or 0),
            "added_to_graph": int(row.added_to_graph or 0)
        }