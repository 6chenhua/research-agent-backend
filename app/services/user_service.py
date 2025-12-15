"""
用户服务

处理用户资料的获取和更新业务逻辑，包括统计数据聚合。
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import HTTPException, status

from app.crud.user import UserRepository
from app.crud.session import SessionRepository
from app.crud.message import MessageRepository
from app.crud.paper import PaperRepository
from app.models.db_models import User
from app.schemas.user import (
    UserProfileResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
    GraphStats,
    ResearchStats,
    PaperStats
)

logger = logging.getLogger(__name__)


class UserService:
    """
    用户服务
    
    提供用户资料的获取、更新和统计聚合功能。
    """
    
    def __init__(
        self,
        user_repo: UserRepository,
        session_repo: SessionRepository,
        message_repo: MessageRepository,
        paper_repo: PaperRepository
    ):
        """
        初始化服务
        
        Args:
            user_repo: 用户 Repository
            session_repo: 会话 Repository
            message_repo: 消息 Repository
            paper_repo: 论文 Repository
        """
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.paper_repo = paper_repo
    
    async def get_profile(self, user: User) -> UserProfileResponse:
        """
        获取用户资料和统计数据
        
        Args:
            user: 当前用户对象
            
        Returns:
            用户资料响应
        """
        user_id = user.user_id
        
        # 1. 研究统计
        total_sessions = await self.session_repo.count_by_user(user_id)
        total_messages = await self.message_repo.count_by_user(user_id)
        
        research_stats = ResearchStats(
            total_sessions=total_sessions,
            total_messages=total_messages,
            domains=[]  # TODO: 从会话中聚合
        )
        
        # 2. 论文统计
        paper_stats_data = await self.paper_repo.get_stats_by_user(user_id)
        paper_stats = PaperStats(
            total_uploaded=paper_stats_data["total_uploaded"],
            total_parsed=paper_stats_data["total_parsed"],
            added_to_graph=paper_stats_data["added_to_graph"]
        )
        
        # 3. 图谱统计（TODO: 从 Neo4j 查询）
        graph_stats = GraphStats(
            total_entities=0,
            total_episodes=0,
            total_edges=0
        )
        
        # 4. 组装响应
        return UserProfileResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat() + "Z" if user.created_at else None,
            last_login_at=user.last_login_at.isoformat() + "Z" if user.last_login_at else None,
            research_stats=research_stats,
            paper_stats=paper_stats,
            graph_stats=graph_stats
        )
    
    async def update_profile(
        self,
        user: User,
        request: UpdateProfileRequest
    ) -> UpdateProfileResponse:
        """
        更新用户资料
        
        Args:
            user: 当前用户对象
            request: 更新请求
            
        Returns:
            更新结果响应
            
        Raises:
            HTTPException: 如果邮箱已被占用
        """
        # 1. 如果需要更新邮箱，检查唯一性
        if request.email is not None:
            existing = await self.user_repo.get_by_email(request.email)
            if existing and existing.user_id != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use"
                )
            user.email = request.email
        
        # 2. 更新偏好设置
        if request.preferences is not None:
            current_preferences = user.preferences or {}
            current_preferences.update(request.preferences.model_dump(exclude_unset=True))
            user.preferences = current_preferences
        
        # 3. 保存更新
        updated_user = await self.user_repo.update(user)
        
        return UpdateProfileResponse(
            message="Profile updated successfully",
            user_id=updated_user.user_id,
            username=updated_user.username,
            email=updated_user.email,
            preferences=updated_user.preferences,
            updated_at=datetime.utcnow().isoformat() + "Z"
        )

