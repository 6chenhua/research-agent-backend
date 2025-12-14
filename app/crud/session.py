"""
研究会话 Repository
处理 research_sessions 表的所有数据库操作
"""
import json
from datetime import datetime, timezone
from typing import Optional, List, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ResearchSession, ChatMessage
from app.crud.base import BaseRepository


class SessionRepository(BaseRepository[ResearchSession]):
    """
    研究会话数据访问层
    
    使用示例:
    ```python
    session_repo = SessionRepository(db_session)
    sessions, total = await session_repo.list_by_user(user_id, limit=20)
    ```
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ResearchSession)
    
    async def get_by_id(self, session_id: str) -> Optional[ResearchSession]:
        """
        根据ID查询会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话对象或 None
        """
        result = await self.session.execute(
            select(ResearchSession).where(ResearchSession.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        title: str,
        domains: List[str],
        description: Optional[str] = None
    ) -> ResearchSession:
        """
        创建研究会话
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            title: 会话标题
            domains: 研究领域列表
            description: 会话描述（可选）
            
        Returns:
            创建的会话对象
        """
        now = datetime.now(timezone.utc)
        research_session = ResearchSession(
            id=session_id,
            user_id=user_id,
            title=title,
            domains=domains,
            description=description,
            message_count=0,
            created_at=now,
            updated_at=now
        )
        return await self.create(research_session)
    
    async def get_by_id_and_user(
        self,
        session_id: str,
        user_id: str
    ) -> Optional[ResearchSession]:
        """
        根据ID和用户ID查询会话
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            
        Returns:
            会话对象或 None
        """
        query = (
            select(ResearchSession)
            .where(
                ResearchSession.id == session_id,
                ResearchSession.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        sort: str = "created_desc"
    ) -> tuple[List[ResearchSession], int]:
        """
        获取用户的会话列表
        
        Args:
            user_id: 用户ID
            limit: 每页数量
            offset: 偏移量
            sort: 排序方式
            
        Returns:
            (会话列表, 总数) 元组
        """
        # 确定排序字段
        if sort == "updated_desc":
            order_by = ResearchSession.updated_at.desc()
        else:  # 默认 created_desc
            order_by = ResearchSession.created_at.desc()

        # 查询会话列表
        query = (
            select(ResearchSession)
            .where(ResearchSession.user_id == user_id)
            .order_by(order_by)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        sessions = result.scalars().all()

        # 查询总数
        count_query = (
            select(func.count())
            .select_from(ResearchSession)
            .where(ResearchSession.user_id == user_id)
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        return list(sessions), total
    
    async def update_stats(self, session_id: str) -> Optional[ResearchSession]:
        """
        更新会话统计信息（消息数量、最后消息时间）
        
        Args:
            session_id: 会话ID
            
        Returns:
            更新后的会话对象或 None
        """
        # 查询消息统计
        stats_query = (
            select(
                func.count(ChatMessage.id).label("message_count"),
                func.max(ChatMessage.created_at).label("last_message_at")
            )
            .where(ChatMessage.session_id == session_id)
        )
        result = await self.session.execute(stats_query)
        stats = result.one()

        # 更新会话
        session_query = select(ResearchSession).where(ResearchSession.id == session_id)
        session_result = await self.session.execute(session_query)
        research_session = session_result.scalar_one_or_none()

        if research_session:
            research_session.message_count = stats.message_count or 0
            research_session.last_message_at = stats.last_message_at
            await self.session.flush()
            
        return research_session
    
    @staticmethod
    def parse_domains(domains: Any) -> List[str]:
        """
        解析 domains 字段
        
        Args:
            domains: domains 字段值（可能是 str 或 list）
            
        Returns:
            解析后的 domains 列表
        """
        if isinstance(domains, str):
            return json.loads(domains)
        return domains if domains else []
