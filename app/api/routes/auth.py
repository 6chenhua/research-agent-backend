"""
认证API路由
提供用户注册、登录、Token管理等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.api.dependencies.auth import get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    UserMeResponse, MessageResponse
)
from app.models.db_models import User

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="注册新用户账户"
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    用户注册
    
    - **username**: 用户名（2-50字符）
    - **email**: 邮箱地址
    - **password**: 密码（≥8位，含大小写+数字+特殊字符）
    
    返回：
    - **user**: 用户信息
    - **access_token**: 访问令牌（1小时有效）
    - **refresh_token**: 刷新令牌（7天有效）
    """
    auth_service = AuthService()
    return await auth_service.register(request, session)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="用户登录",
    description="使用邮箱和密码登录"
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    用户登录
    
    - **email**: 邮箱地址
    - **password**: 密码
    
    返回：
    - **user**: 用户信息
    - **access_token**: 访问令牌
    - **refresh_token**: 刷新令牌
    
    注意：
    - 登录失败3次将锁定账户5分钟
    """
    auth_service = AuthService()
    return await auth_service.login(request, session)


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="刷新Token",
    description="使用刷新令牌获取新的访问令牌"
)
async def refresh_token(
    request: RefreshTokenRequest
):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    
    返回：
    - **access_token**: 新的访问令牌
    - **expires_in**: 有效期（秒）
    """
    auth_service = AuthService()
    return await auth_service.refresh_token(request)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="用户登出",
    description="登出并撤销当前Token"
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    用户登出
    
    将当前Token加入黑名单，使其失效。
    """
    token = credentials.credentials
    auth_service = AuthService()
    return await auth_service.logout(token)


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    获取当前用户信息
    
    需要在Header中提供有效的访问令牌：
    ```
    Authorization: Bearer <access_token>
    ```
    
    返回：
    - **user_id**: 用户ID
    - **username**: 用户名
    - **email**: 邮箱
    - **is_active**: 是否激活
    - **is_verified**: 邮箱是否验证
    - **created_at**: 创建时间
    - **last_login**: 最后登录时间
    - **reading_count**: 阅读论文数量
    - **chat_count**: 聊天次数
    """
    # 获取用户画像信息
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    
    result = await session.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.user_id == current_user.user_id)
    )
    user_with_profile = result.scalar_one()
    
    response_data = UserMeResponse.model_validate(user_with_profile)
    
    # 添加画像统计信息
    if user_with_profile.profile:
        response_data.reading_count = user_with_profile.profile.reading_count
        response_data.chat_count = user_with_profile.profile.chat_count
    
    return response_data


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    summary="修改密码",
    description="修改当前用户密码"
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    修改密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码（≥8位，含大小写+数字+特殊字符）
    
    需要在Header中提供有效的访问令牌。
    
    注意：前端应该负责密码强度验证和确认密码一致性验证。
    """
    auth_service = AuthService()
    return await auth_service.change_password(current_user, request, session)

