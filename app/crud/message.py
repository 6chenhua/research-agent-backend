"""
聊天消息 Repository
处理 chat_messages 表的所有数据库操作
"""
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ChatMessage, MessageRole
from app.crud.base import BaseRepository


class MessageRepository(BaseRepository[ChatMessage]):
    """
    聊天消息数据访问层
    
    使用示例:
    ```python
    msg_repo = MessageRepository(db_session)
    messages, total = await msg_repo.get_by_session(session_id)
    ```
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ChatMessage)
    
    async def create_message(
        self,
        message_id: str,
        session_id: str,
        role: MessageRole,
        content: str,
        attached_papers: Optional[List[str]] = None,
        context_string: Optional[str] = None,
        context_data: Optional[Dict] = None,
        created_at: Optional[datetime] = None
    ) -> ChatMessage:
        """
        创建聊天消息
        
        Args:
            message_id: 消息ID
            session_id: 会话ID
            role: 消息角色 (user/agent)
            content: 消息内容
            attached_papers: 附带的论文ID列表
            context_string: context 文本
            context_data: context 数据
            created_at: 创建时间
            
        Returns:
            创建的消息对象
        """
        if created_at is None:
            created_at = datetime.now(timezone.utc)
            
        message = ChatMessage(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            attached_papers=attached_papers,
            context_string=context_string,
            context_data=context_data,
            created_at=created_at
        )
        return await self.create(message)
    
    async def get_by_session(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0,
        order: str = "asc"
    ) -> tuple[List[ChatMessage], int]:
        """
        获取会话的消息列表
        
        Args:
            session_id: 会话ID
            limit: 每页数量
            offset: 偏移量
            order: 排序方式 (asc/desc)
            
        Returns:
            (消息列表, 总数) 元组
        """
        # 排序
        order_by = ChatMessage.created_at.asc() if order == "asc" else ChatMessage.created_at.desc()
        
        # 查询消息
        messages_query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(order_by)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(messages_query)
        messages = result.scalars().all()
        
        # 查询总数
        count_query = (
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.session_id == session_id)
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        
        return list(messages), total
    
    async def get_recent(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """
        获取最近的消息（按时间正序排列）
        
        Args:
            session_id: 会话ID
            limit: 返回数量
            
        Returns:
            消息列表
        """
        query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        messages = result.scalars().all()
        # 按时间正序排列
        return list(reversed(list(messages)))
    
    @staticmethod
    def format_message(msg: ChatMessage) -> Dict[str, Any]:
        """
        格式化消息为字典
        
        Args:
            msg: 消息对象
            
        Returns:
            格式化后的消息字典
        """
        # 处理 attached_papers
        attached_papers = msg.attached_papers
        if isinstance(attached_papers, str):
            attached_papers = json.loads(attached_papers)
        
        # 处理 context_data
        context_data = msg.context_data
        if isinstance(context_data, str):
            context_data = json.loads(context_data)
        
        return {
            "message_id": msg.id,
            "role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role),
            "content": msg.content,
            "attached_papers": attached_papers,
            "context_string": msg.context_string,
            "context_data": context_data,
            "created_at": msg.created_at.isoformat() + "Z" if msg.created_at else None
        }
    
    @staticmethod
    def to_history_format(messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """
        将消息转换为历史记录格式（用于 LLM 上下文）
        
        Args:
            messages: 消息列表
            
        Returns:
            历史记录格式的消息列表
        """
        return [
            {
                "role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role),
                "content": msg.content
            }
            for msg in messages
        ]
