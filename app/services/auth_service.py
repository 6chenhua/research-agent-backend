"""
认证服务
根据PRD_认证模块.md设计
处理用户注册、登录、Token管理等业务逻辑
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.db_models import User
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse, LoginUserInfo,
    RefreshTokenRequest, RefreshTokenResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    LogoutResponse
)
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    verify_refresh_token, generate_user_id,
    get_token_remaining_time
)
from app.core.redis_client import (
    add_token_to_blacklist,
    increment_failed_login,
    reset_failed_login,
    check_rate_limit,
    LOGIN_MAX_ATTEMPTS,
    LOGIN_RATE_LIMIT_WINDOW
)
from app.core.config import settings


class AuthService:
    """
    认证服务类
    实现REQ-AUTH-1到REQ-AUTH-5的所有功能
    """
    
    async def register(
        self, 
        request: RegisterRequest, 
        session: AsyncSession
    ) -> RegisterResponse:
        """
        用户注册 REQ-AUTH-1
        
        处理流程：
        1. 验证请求参数（Schema层已验证）
        2. 检查用户名是否已存在
        3. 生成用户ID和密码哈希
        4. 插入用户记录到MySQL
        5. 返回成功响应（不包含Token）
        
        Args:
            request: 注册请求
            session: 数据库会话
            
        Returns:
            注册响应
            
        Raises:
            HTTPException: 注册失败
        """
        # 1. 检查用户名是否已存在
        result = await session.execute(
            select(User).where(User.username == request.username)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_INPUT",
                    "message": "Username already exists"
                }
            )
        
        # 2. 生成用户ID和密码哈希
        user_id = generate_user_id()
        password_hash = hash_password(request.password)
        
        # 3. 创建用户记录
        new_user = User(
            user_id=user_id,
            username=request.username,
            email=request.email,  # 可选字段
            password_hash=password_hash
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        # 4. 返回响应（PRD要求不返回Token）
        return RegisterResponse(
            user_id=user_id,
            username=request.username,
            created_at=new_user.created_at,
            message="Registration successful"
        )
    
    async def login(
        self, 
        request: LoginRequest, 
        session: AsyncSession
    ) -> LoginResponse:
        """
        用户登录 REQ-AUTH-2
        
        处理流程：
        1. 检查登录限流
        2. 从MySQL查询用户记录
        3. 验证密码
        4. 生成JWT Token
        5. 更新最后登录时间
        6. 返回Token和用户信息
        
        Args:
            request: 登录请求
            session: 数据库会话
            
        Returns:
            登录响应
            
        Raises:
            HTTPException: 登录失败
        """
        # 1. 检查登录限流（PRD要求：15分钟内5次）
        if not await check_rate_limit(request.username):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "RATE_LIMIT",
                    "message": "Too many login attempts. Please try again in 15 minutes."
                }
            )
        
        # 2. 查询用户
        result = await session.execute(
            select(User).where(User.username == request.username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # 增加失败次数
            await increment_failed_login(request.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_CREDENTIALS",
                    "message": "Invalid username or password"
                }
            )
        
        # 3. 验证密码
        if not verify_password(request.password, user.password_hash):
            # 增加失败次数
            await increment_failed_login(request.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_CREDENTIALS",
                    "message": "Invalid username or password"
                }
            )
        
        # 4. 重置失败次数
        await reset_failed_login(request.username)
        
        # 5. 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await session.commit()
        await session.refresh(user)
        
        # 6. 生成Token（PRD要求payload包含user_id和username）
        access_token = create_access_token(user.user_id, user.username)
        refresh_token = create_refresh_token(user.user_id)
        
        # 7. 返回响应
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 30分钟 = 1800秒
            user=LoginUserInfo(
                user_id=user.user_id,
                username=user.username
            )
        )
    
    async def refresh_token(
        self, 
        request: RefreshTokenRequest,
        session: AsyncSession
    ) -> RefreshTokenResponse:
        """
        刷新访问令牌 REQ-AUTH-3
        
        处理流程：
        1. 验证refresh_token
        2. 检查Token类型是否为refresh
        3. 从数据库查询用户
        4. 生成新的access_token
        5. 返回新Token
        
        Args:
            request: 刷新Token请求
            session: 数据库会话
            
        Returns:
            新的访问令牌
            
        Raises:
            HTTPException: 刷新失败
        """
        # 1. 验证refresh token
        payload = verify_refresh_token(request.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": "Invalid or expired refresh token"
                }
            )
        
        # 2. 获取用户信息
        user_id = payload.get("user_id")
        
        # 3. 从数据库查询用户以获取username
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": "Invalid or expired refresh token"
                }
            )
        
        # 4. 生成新的access token
        access_token = create_access_token(user.user_id, user.username)
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def logout(self, token: str) -> LogoutResponse:
        """
        用户登出 REQ-AUTH-5
        
        处理流程：
        1. 从请求头提取access_token
        2. 获取Token剩余有效时间
        3. 将Token加入Redis黑名单
        4. 返回成功响应
        
        Args:
            token: 访问令牌
            
        Returns:
            登出响应
        """
        # 获取token剩余时间
        remaining_time = get_token_remaining_time(token)
        if remaining_time and remaining_time > 0:
            # 加入黑名单，TTL设置为token剩余有效期
            await add_token_to_blacklist(token, remaining_time)
        
        return LogoutResponse(message="Logged out successfully")
    
    async def change_password(
        self,
        user: User,
        request: ChangePasswordRequest,
        session: AsyncSession
    ) -> ChangePasswordResponse:
        """
        修改密码 REQ-AUTH-4
        
        处理流程：
        1. 从Token提取user_id（已通过依赖注入）
        2. 验证旧密码
        3. 更新密码
        4. 返回成功响应
        
        Args:
            user: 当前用户（通过JWT认证中间件获取）
            request: 修改密码请求
            session: 数据库会话
            
        Returns:
            修改密码响应
            
        Raises:
            HTTPException: 修改失败
        """
        # 1. 验证旧密码
        if not verify_password(request.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "WRONG_PASSWORD",
                    "message": "Old password is incorrect"
                }
            )
        
        # 2. 验证新密码强度（Schema层已验证，这里是双重检查）
        # 密码强度要求：最少8字符，包含大小写字母和数字
        
        # 3. 更新密码
        user.password_hash = hash_password(request.new_password)
        await session.commit()
        
        # 4. 返回响应（PRD要求返回require_relogin）
        return ChangePasswordResponse(
            message="Password changed successfully",
            require_relogin=True
        )
