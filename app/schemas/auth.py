"""
认证相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ==================== 注册相关 ====================

class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "张三",
                "email": "zhangsan@example.com",
                "password": "SecurePass123!"
            }
        }


class RegisterResponse(BaseModel):
    """用户注册响应"""
    user: 'UserInfo'
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # 秒


# ==================== 登录相关 ====================

class LoginRequest(BaseModel):
    """用户登录请求"""
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "zhangsan@example.com",
                "password": "SecurePass123!"
            }
        }


class LoginResponse(BaseModel):
    """用户登录响应"""
    user: 'UserInfo'
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # 秒


# ==================== Token刷新 ====================

class RefreshTokenRequest(BaseModel):
    """Token刷新请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class RefreshTokenResponse(BaseModel):
    """Token刷新响应"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int  # 秒


# ==================== 密码修改 ====================

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")


class ChangePasswordResponse(BaseModel):
    """修改密码响应"""
    message: str = "密码修改成功"


# ==================== 用户信息 ====================

class UserInfo(BaseModel):
    """用户基本信息"""
    user_id: str
    username: str
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Pydantic v2替代orm_mode
        json_schema_extra = {
            "example": {
                "user_id": "u_1234567890_abc123",
                "username": "张三",
                "email": "zhangsan@example.com",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-15T10:30:00Z",
                "last_login": "2024-01-20T14:30:00Z"
            }
        }


class UserMeResponse(UserInfo):
    """当前用户信息响应（扩展版）"""
    reading_count: Optional[int] = 0
    chat_count: Optional[int] = 0


# ==================== Token Payload ====================

class TokenPayload(BaseModel):
    """JWT Token payload"""
    sub: str  # user_id
    email: str
    exp: int  # expiration time
    iat: int  # issued at time
    type: Optional[str] = "access"  # access or refresh


# ==================== 通用响应 ====================

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "操作成功"
            }
        }

