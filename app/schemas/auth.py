"""
认证相关的Pydantic模型
根据PRD_认证模块.md设计
"""
import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


# ==================== 注册相关 ====================

class RegisterRequest(BaseModel):
    """
    用户注册请求
    REQ-AUTH-1
    """
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        description="用户名，3-50字符，仅支持字母数字下划线"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        description="密码，最少8字符，需包含大小写字母和数字"
    )
    email: Optional[EmailStr] = Field(None, description="邮箱（可选）")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式：仅支持字母数字下划线"""
        pattern = r'^[a-zA-Z0-9_]{3,50}$'
        if not re.match(pattern, v):
            raise ValueError('用户名仅支持字母、数字、下划线，长度3-50字符')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度：至少8字符，包含大小写字母和数字"""
        if len(v) < 8:
            raise ValueError('密码长度至少为8位')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "researcher001",
                "password": "Password123",
                "email": "researcher@example.com"
            }
        }


class RegisterResponse(BaseModel):
    """
    用户注册响应
    REQ-AUTH-1
    """
    user_id: str = Field(..., description="用户UUID")
    username: str = Field(..., description="用户名")
    created_at: datetime = Field(..., description="创建时间")
    message: str = Field(default="Registration successful", description="响应消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "researcher001",
                "created_at": "2025-12-11T10:00:00Z",
                "message": "Registration successful"
            }
        }


# ==================== 登录相关 ====================

class LoginRequest(BaseModel):
    """
    用户登录请求
    REQ-AUTH-2
    """
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "researcher001",
                "password": "Password123"
            }
        }


class LoginUserInfo(BaseModel):
    """登录响应中的用户信息"""
    user_id: str = Field(..., description="用户UUID")
    username: str = Field(..., description="用户名")


class LoginResponse(BaseModel):
    """
    用户登录响应
    REQ-AUTH-2
    """
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(default=1800, description="有效期（秒），30分钟")
    user: LoginUserInfo = Field(..., description="用户信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "researcher001"
                }
            }
        }


# ==================== Token刷新 ====================

class RefreshTokenRequest(BaseModel):
    """
    Token刷新请求
    REQ-AUTH-3
    """
    refresh_token: str = Field(..., description="刷新令牌")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class RefreshTokenResponse(BaseModel):
    """
    Token刷新响应
    REQ-AUTH-3
    """
    access_token: str = Field(..., description="新的访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(default=1800, description="有效期（秒）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


# ==================== 密码修改 ====================

class ChangePasswordRequest(BaseModel):
    """
    修改密码请求
    REQ-AUTH-4
    """
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码，最少8字符")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """验证新密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度至少为8位')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "Password123",
                "new_password": "NewPassword456"
            }
        }


class ChangePasswordResponse(BaseModel):
    """
    修改密码响应
    REQ-AUTH-4
    """
    message: str = Field(default="Password changed successfully", description="响应消息")
    require_relogin: bool = Field(default=True, description="是否需要重新登录")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Password changed successfully",
                "require_relogin": True
            }
        }


# ==================== 登出相关 ====================

class LogoutResponse(BaseModel):
    """
    登出响应
    REQ-AUTH-5
    """
    message: str = Field(default="Logged out successfully", description="响应消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Logged out successfully"
            }
        }


# ==================== 错误响应 ====================

class ErrorResponse(BaseModel):
    """通用错误响应"""
    error: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "INVALID_INPUT",
                "message": "Username already exists"
            }
        }


# ==================== Token Payload ====================

class TokenPayload(BaseModel):
    """JWT Token payload"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    exp: int = Field(..., description="过期时间戳")
    type: str = Field(default="access", description="Token类型：access或refresh")
