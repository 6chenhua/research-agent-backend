"""
认证相关的依赖注入
提供JWT认证中间件
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_session
from app.core.security import decode_token
from app.core.redis_client import is_token_blacklisted
from app.models.db_models import User
from app.schemas.auth import TokenPayload

# HTTP Bearer认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    JWT认证依赖
    验证Token并返回当前用户对象
    
    Args:
        credentials: HTTP Bearer凭证
        session: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 认证失败
    """
    token = credentials.credentials
    
    # 1. 检查Token是否在黑名单中
    if await is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已被撤销",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 解码Token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. 验证Token类型（必须是access token）
    token_type = payload.get("type", "access")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token类型",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 4. 获取user_id
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token中缺少用户信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 5. 从数据库查询用户
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 6. 检查用户状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前激活的用户
    （额外的依赖层，可用于添加更多验证）
    
    Args:
        current_user: 当前用户
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户未激活"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取邮箱已验证的用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 邮箱未验证
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="请先验证邮箱"
        )
    return current_user


# ==================== 可选认证 ====================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """
    可选的JWT认证
    如果提供了Token则验证，否则返回None
    用于可选登录的API
    
    Args:
        credentials: HTTP Bearer凭证（可选）
        session: 数据库会话
        
    Returns:
        当前用户对象或None
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, session)
    except HTTPException:
        return None
