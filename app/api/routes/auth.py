"""
认证API路由
根据PRD_认证模块.md设计
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
    LogoutResponse
)
from app.models.db_models import User

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="REQ-AUTH-1: 新用户通过用户名和密码注册账号"
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    用户注册
    
    - **username**: 用户名（3-50字符，仅支持字母数字下划线）
    - **password**: 密码（最少8字符，需包含大小写字母和数字）
    - **email**: 邮箱地址（可选）
    
    返回：
    - **user_id**: 用户UUID
    - **username**: 用户名
    - **created_at**: 创建时间
    - **message**: 响应消息
    """
    auth_service = AuthService()
    return await auth_service.register(request, session)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="用户登录",
    description="REQ-AUTH-2: 用户通过用户名和密码登录"
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    
    返回：
    - **access_token**: 访问令牌（30分钟有效）
    - **refresh_token**: 刷新令牌（7天有效）
    - **token_type**: 令牌类型（bearer）
    - **expires_in**: 有效期（秒）
    - **user**: 用户信息
    
    注意：
    - 同一用户名15分钟内最多尝试5次
    - 超过限制将返回429错误
    """
    auth_service = AuthService()
    return await auth_service.login(request, session)


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="刷新Token",
    description="REQ-AUTH-3: 使用refresh_token获取新的access_token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    
    返回：
    - **access_token**: 新的访问令牌
    - **token_type**: 令牌类型（bearer）
    - **expires_in**: 有效期（秒）
    
    使用场景：
    - 前端检测到access_token即将过期（过期前5分钟）
    - 前端收到401响应且错误为TOKEN_EXPIRED时
    """
    auth_service = AuthService()
    return await auth_service.refresh_token(request, session)


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    summary="修改密码",
    description="REQ-AUTH-4: 已登录用户修改自己的密码"
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    修改密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码（最少8字符，需包含大小写字母和数字）
    
    需要在Header中提供有效的访问令牌：
    ```
    Authorization: Bearer <access_token>
    ```
    
    返回：
    - **message**: 响应消息
    - **require_relogin**: 是否需要重新登录
    """
    auth_service = AuthService()
    return await auth_service.change_password(current_user, request, session)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="用户登出",
    description="REQ-AUTH-5: 用户登出系统，将当前Token加入黑名单"
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    用户登出
    
    将当前Token加入黑名单，防止被继续使用。
    
    需要在Header中提供有效的访问令牌：
    ```
    Authorization: Bearer <access_token>
    ```
    
    返回：
    - **message**: 响应消息
    """
    token = credentials.credentials
    auth_service = AuthService()
    return await auth_service.logout(token)
