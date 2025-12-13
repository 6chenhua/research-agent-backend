"""
研究会话服务
根据PRD_研究与聊天模块.md设计
提供研究会话的创建、查询等功能
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from app.models.db_models import ResearchSession
from app.core.graphiti_enhanced import get_enhanced_graphiti
from app.crud.session import SessionRepository

logger = logging.getLogger(__name__)


class ResearchService:
    """
    研究会话服务
    
    使用 Repository Pattern，通过构造函数注入 SessionRepository
    """
    
    def __init__(self, session_repo: SessionRepository):
        """
        初始化研究会话服务
        
        Args:
            session_repo: 会话数据访问层
        """
        self.session_repo = session_repo

    async def create_session(
            self,
            user_id: str,
            domains: List[str],
            title: Optional[str] = None,
            description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建研究会话 - REQ-CHAT-1
        
        Args:
            user_id: 用户ID
            domains: 研究领域列表
            title: 会话标题（可选，默认生成）
            description: 会话描述（可选）
            
        Returns:
            创建的会话信息
        """
        # 1. 验证domains
        if not domains or len(domains) == 0:
            raise ValueError("At least one domain required")

        # 2. 生成默认标题
        if not title:
            title = f"{domains[0]}研究 - {datetime.now().strftime('%Y%m%d')}"

        # 3. 生成session_id
        session_id = str(uuid4())

        # 4. 创建会话记录
        research_session = await self.session_repo.create_session(
            session_id=session_id,
            user_id=user_id,
            title=title,
            domains=domains,
            description=description
        )

        # 5. 异步触发社区构建（不阻塞响应）
        asyncio.create_task(self._build_communities(user_id))

        logger.info(f"Research session created: {session_id} for user {user_id}")

        return {
            "session_id": session_id,
            "title": title,
            "domains": domains,
            "created_at": research_session.created_at.isoformat() + "Z",
            "message": "Research session created successfully",
            "community_build_triggered": True
        }

    async def _build_communities(self, user_id: str):
        """
        异步构建社区（后台任务，不阻塞主流程）
        
        Args:
            user_id: 用户ID（用于命名空间隔离）
        """
        try:
            graphiti = await get_enhanced_graphiti()
            # 尝试传入用户ID作为group_ids进行命名空间隔离
            await graphiti.build_communities(group_ids=[user_id])
            logger.info(f"Community build completed for user {user_id}")
        except Exception as e:
            # 社区构建失败不影响主流程
            logger.warning(f"Community build failed for user {user_id}: {e}")

    async def list_sessions(
            self,
            user_id: str,
            limit: int = 20,
            offset: int = 0,
            sort: str = "created_desc"
    ) -> Dict[str, Any]:
        """
        获取研究会话列表 - REQ-CHAT-2
        
        Args:
            user_id: 用户ID
            limit: 每页数量
            offset: 偏移量
            sort: 排序方式
            
        Returns:
            会话列表和分页信息
        """
        # 获取会话列表和总数
        sessions, total = await self.session_repo.list_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
            sort=sort
        )

        # 格式化会话列表
        session_list = []
        for rs in sessions:
            domains = SessionRepository.parse_domains(rs.domains)
            session_list.append({
                "session_id": rs.id,
                "title": rs.title,
                "domains": domains,
                "message_count": rs.message_count or 0,
                "last_message_at": rs.last_message_at.isoformat() + "Z" if rs.last_message_at else None,
                "created_at": rs.created_at.isoformat() + "Z" if rs.created_at else None
            })

        return {
            "sessions": session_list,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }

    async def get_session(
            self,
            session_id: str,
            user_id: str
    ) -> Optional[ResearchSession]:
        """
        获取单个研究会话
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            
        Returns:
            会话对象或None
        """
        return await self.session_repo.get_by_id_and_user(
            session_id=session_id,
            user_id=user_id
        )

    async def update_session_stats(self, session_id: str):
        """
        更新会话统计信息（消息数量、最后消息时间）
        
        Args:
            session_id: 会话ID
        """
        await self.session_repo.update_stats(session_id=session_id)
