"""
用户资料API路由
提供用户资料、用户画像、研究会话历史等接口
"""
from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_user_service
from app.services.user_service import UserService
from app.schemas.user import (
    UserProfileResponse,
    UpdateProfileRequest,
    UpdateProfileResponse
)
from app.models.db_models import User

router = APIRouter(prefix="/user", tags=["用户资料"])


# ==================== 用户资料 ====================

@router.get(
    "/profile",
    response_model=UserProfileResponse,
    summary="获取用户资料",
    description="获取当前登录用户的个人信息和统计数据"
)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UserProfileResponse:
    """
    获取用户资料 (REQ-USER-1)
    
    返回用户基本信息和统计数据。
    """
    return await user_service.get_profile(current_user)


@router.put(
    "/profile",
    response_model=UpdateProfileResponse,
    summary="更新用户资料",
    description="更新当前登录用户的个人信息"
)
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UpdateProfileResponse:
    """
    更新用户资料 (REQ-USER-2)
    """
    return await user_service.update_profile(current_user, request)
