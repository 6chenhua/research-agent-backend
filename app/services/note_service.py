"""
笔记服务

负责将消息添加到用户私有笔记图谱 (user:{user_id}:notes)
"""
import logging
import time
from typing import Dict, Any, Optional

from app.core.graphiti_enhanced import get_enhanced_graphiti
from app.crud.message import MessageRepository
from app.crud.session import SessionRepository
from app.utils.group_id import get_notes_ingest_group_id
from app.schemas.note_entities import get_note_entity_types, get_note_edge_types
from graphiti_core.nodes import EpisodeType

logger = logging.getLogger(__name__)


class NoteService:
    """
    笔记服务
    
    处理将消息添加到用户私有笔记图谱的逻辑。
    """
    
    def __init__(
        self,
        message_repo: MessageRepository,
        session_repo: SessionRepository
    ):
        """
        初始化服务
        
        Args:
            message_repo: 消息数据访问层
            session_repo: 会话数据访问层
        """
        self.message_repo = message_repo
        self.session_repo = session_repo
    
    async def add_message_to_notes(
        self,
        message_id: str,
        user_id: str,
        extra_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        将消息添加到用户私有笔记图谱
        
        Args:
            message_id: 消息ID
            user_id: 用户ID
            extra_note: 用户额外添加的笔记
            
        Returns:
            包含 message_id, status, episode_name 的字典
            
        Raises:
            ValueError: 消息不存在或无权访问
        """
        # 1. 获取消息
        message = await self.message_repo.get_by_id(message_id)
        if not message:
            raise ValueError("MESSAGE_NOT_FOUND")
        
        # 2. 验证权限（通过 session）
        session = await self.session_repo.get_by_id(message.session_id)
        if not session or session.user_id != user_id:
            raise ValueError("ACCESS_DENIED")
        
        # 3. 构建 episode 内容
        role_label = "You" if message.role.value == "user" else "Agent"
        episode_body = f"{role_label}: {message.content}"
        
        if extra_note:
            episode_body += f"\n\n用户笔记: {extra_note}"
        
        # 4. 添加到私有笔记图谱
        graphiti = await get_enhanced_graphiti()
        group_id = get_notes_ingest_group_id(user_id)
        episode_name = f"note_{message_id}_{int(time.time())}"
        
        await graphiti.add_episode(
            episode_body=episode_body,
            user_id=user_id,
            group_id=group_id,
            name=episode_name,
            source=EpisodeType.message,
            source_description=f"User note from session {message.session_id}",
            entity_types=get_note_entity_types(),
            edge_types=get_note_edge_types(),
            timeout=60.0
        )
        
        logger.info(f"✅ Message {message_id} added to notes for user {user_id}")
        
        return {
            "message_id": message_id,
            "status": "success",
            "episode_name": episode_name
        }

