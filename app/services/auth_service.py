"""
认证服务
处理用户注册、登录、Token管理等业务逻辑
"""
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.db_models import User, UserProfile
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    UserInfo, MessageResponse
)
from app.core.security import (
    hash_password, verify_password, validate_password_strength,
    create_access_token, create_refresh_token, decode_token,
    generate_user_id, get_token_remaining_time
)
from app.core.redis_client import (
    add_token_to_blacklist,
    increment_failed_login,
    reset_failed_login,
    get_failed_login_count
)
from app.core.config import settings


class AuthService:
    """认证服务类"""
    
    MAX_FAILED_ATTEMPTS = 3  # 最大失败次数
    LOCK_DURATION = 300  # 锁定时长（秒）
    
    async def register(
        self, 
        request: RegisterRequest, 
        session: AsyncSession
    ) -> RegisterResponse:
        """
        用户注册
        
        Args:
            request: 注册请求
            session: 数据库会话
            
        Returns:
            注册响应（包含用户信息和Token）
            
        Raises:
            HTTPException: 注册失败
        """
        # 1. 验证密码强度
        is_valid, error_msg = validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # 2. 检查邮箱是否已存在
        result = await session.execute(
            select(User).where(User.email == request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )
        
        # 3. 创建用户
        user_id = generate_user_id()
        password_hash = hash_password(request.password)
        
        new_user = User(
            user_id=user_id,
            username=request.username,
            email=request.email,
            password_hash=password_hash,
            is_active=True,
            is_verified=False  # 邮箱未验证
        )
        
        session.add(new_user)
        
        # 4. 创建用户画像
        user_profile = UserProfile(
            user_id=user_id
        )
        session.add(user_profile)
        
        await session.commit()
        await session.refresh(new_user)
        
        # 5. 生成Token
        access_token = create_access_token({
            "sub": user_id,
            "email": request.email
        })
        
        refresh_token = create_refresh_token({
            "sub": user_id,
            "email": request.email
        })
        
        # 6. 返回响应
        return RegisterResponse(
            user=UserInfo.model_validate(new_user),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def login(
        self, 
        request: LoginRequest, 
        session: AsyncSession
    ) -> LoginResponse:
        """
        用户登录
        
        Args:
            request: 登录请求
            session: 数据库会话
            
        Returns:
            登录响应（包含用户信息和Token）
            
        Raises:
            HTTPException: 登录失败
        """
        # 1. 检查账户是否被锁定
        failed_count = await get_failed_login_count(request.email)
        if failed_count >= self.MAX_FAILED_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"登录失败次数过多，账户已锁定{self.LOCK_DURATION}秒"
            )
        
        # 2. 查询用户
        result = await session.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # 增加失败次数
            await increment_failed_login(request.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        # 3. 验证密码
        if not verify_password(request.password, user.password_hash):
            # 增加失败次数
            await increment_failed_login(request.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        # 4. 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用"
            )
        
        # 5. 重置失败次数
        await reset_failed_login(request.email)
        
        # 6. 更新最后登录时间
        user.last_login = datetime.utcnow()
        await session.commit()
        await session.refresh(user)
        
        # 7. 生成Token
        access_token = create_access_token({
            "sub": user.user_id,
            "email": user.email
        })
        
        refresh_token = create_refresh_token({
            "sub": user.user_id,
            "email": user.email
        })
        
        # 8. 返回响应
        return LoginResponse(
            user=UserInfo.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_token(
        self, 
        request: RefreshTokenRequest
    ) -> RefreshTokenResponse:
        """
        刷新访问令牌
        
        Args:
            request: 刷新Token请求
            
        Returns:
            新的访问令牌
            
        Raises:
            HTTPException: 刷新失败
        """
        # 1. 解码refresh token
        payload = decode_token(request.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        # 2. 验证token类型
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token类型错误"
            )
        
        # 3. 生成新的access token
        access_token = create_access_token({
            "sub": payload["sub"],
            "email": payload["email"]
        })
        
        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def logout(
        self, 
        token: str
    ) -> MessageResponse:
        """
        用户登出
        将token加入黑名单
        
        Args:
            token: 访问令牌
            
        Returns:
            消息响应
        """
        # 获取token剩余时间
        remaining_time = get_token_remaining_time(token)
        if remaining_time and remaining_time > 0:
            # 加入黑名单
            await add_token_to_blacklist(token, remaining_time)
        
        return MessageResponse(message="登出成功")
    
    async def change_password(
        self,
        user: User,
        request: ChangePasswordRequest,
        session: AsyncSession
    ) -> ChangePasswordResponse:
        """
        修改密码
        
        Args:
            user: 当前用户
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
        
        # 2. 验证新密码强度
        is_valid, error_msg = validate_password_strength(request.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # 3. 更新密码
        user.password_hash = hash_password(request.new_password)
        await session.commit()
        
        return ChangePasswordResponse()

