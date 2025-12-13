"""
用户资料API路由
提供用户资料的查询和更新接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.api.dependencies.auth import get_current_user
from app.services.user_profile_service import UserProfileService
from app.schemas.user import (
    UserProfileResponse,
    UpdateProfileRequest,
    UpdateProfileResponse
)
from app.models.db_models import User

router = APIRouter(prefix="/user", tags=["用户资料"])


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    summary="获取用户资料",
    description="获取当前登录用户的个人信息和统计数据，包括图谱统计、研究统计、论文统计等"
)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> UserProfileResponse:
    """
    获取用户资料 (REQ-USER-1)
    
    从JWT Token中获取user_id，返回：
    - **user_id**: 用户ID
    - **username**: 用户名
    - **email**: 邮箱
    - **created_at**: 注册时间
    - **graph_stats**: 图谱统计（实体、Episode、边数量）
    - **research_stats**: 研究统计（会话、消息数量，涉及领域）
    - **paper_stats**: 论文统计（上传、解析、添加到图谱数量）
    - **last_login_at**: 最后登录时间
    
    需要在Header中提供有效的访问令牌：
    ```
    Authorization: Bearer <access_token>
    ```
    """
    service = UserProfileService()
    return await service.get_profile(current_user.user_id, session)


@router.put(
    "/profile",
    response_model=UpdateProfileResponse,
    summary="更新用户资料",
    description="更新当前登录用户的个人信息，支持修改邮箱、偏好设置等"
)
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> UpdateProfileResponse:
    """
    更新用户资料 (REQ-USER-2)
    
    可更新的字段：
    - **email**: 新邮箱地址（可选，会验证唯一性）
    - **preferences**: 用户偏好设置（可选）
        - default_domains: 默认研究领域
        - theme: 主题 (dark / light / auto)
        - language: 语言 (zh-CN / en-US)
        - graph_settings: 图谱可视化设置
        - chat_settings: 聊天设置
        - paper_settings: 论文设置
    
    需要在Header中提供有效的访问令牌：
    ```
    Authorization: Bearer <access_token>
    ```
    
    错误响应：
    - 400: 邮箱格式错误（由Pydantic验证）
    - 409: 邮箱已被其他用户使用
    """
    service = UserProfileService()
    return await service.update_profile(current_user.user_id, request, session)

