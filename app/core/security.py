"""
安全工具模块
根据PRD_认证模块.md设计
提供密码加密、JWT Token生成等功能
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# 密码加密上下文（使用bcrypt，cost=12）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


# ==================== 密码处理 ====================

def hash_password(password: str) -> str:
    """
    使用bcrypt加密密码
    
    Args:
        password: 明文密码
        
    Returns:
        加密后的密码哈希
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配
    
    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码哈希
        
    Returns:
        是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    验证密码强度
    
    根据PRD要求：
    - 长度 >= 8位
    - 必须包含大写字母
    - 必须包含小写字母
    - 必须包含数字
    
    Args:
        password: 待验证的密码
        
    Returns:
        (是否合格, 错误信息)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters and contain uppercase, lowercase, and numbers"
    
    if not any(c.isupper() for c in password):
        return False, "Password must be at least 8 characters and contain uppercase, lowercase, and numbers"
    
    if not any(c.islower() for c in password):
        return False, "Password must be at least 8 characters and contain uppercase, lowercase, and numbers"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must be at least 8 characters and contain uppercase, lowercase, and numbers"
    
    return True, ""


# ==================== JWT Token ====================

def create_access_token(user_id: str, username: str) -> str:
    """
    创建访问令牌（access_token）
    有效期30分钟
    
    Args:
        user_id: 用户ID
        username: 用户名
        
    Returns:
        JWT token字符串
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """
    创建刷新令牌（refresh_token）
    有效期7天
    
    Args:
        user_id: 用户ID
        
    Returns:
        JWT refresh token字符串
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "user_id": user_id,
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码JWT token
    
    Args:
        token: JWT token字符串
        
    Returns:
        解码后的payload，如果失败返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证并解码refresh token
    
    Args:
        token: refresh token字符串
        
    Returns:
        解码后的payload，验证失败返回None
    """
    payload = decode_token(token)
    if not payload:
        return None
    
    # 检查Token类型
    if payload.get("type") != "refresh":
        return None
    
    # 检查过期时间
    exp = payload.get("exp")
    if not exp or datetime.utcnow() > datetime.fromtimestamp(exp):
        return None
    
    return payload


def get_token_remaining_time(token: str) -> Optional[int]:
    """
    获取token剩余有效时间（秒）
    
    Args:
        token: JWT token字符串
        
    Returns:
        剩余秒数，如果token无效返回None
    """
    payload = decode_token(token)
    if not payload or "exp" not in payload:
        return None
    
    exp = payload["exp"]
    now = datetime.utcnow().timestamp()
    remaining = int(exp - now)
    
    return remaining if remaining > 0 else 0


# ==================== 用户ID生成 ====================

def generate_user_id() -> str:
    """
    生成唯一的用户ID
    使用UUID4格式
    
    Returns:
        UUID字符串
    """
    return str(uuid.uuid4())


# ==================== 会话ID生成 ====================

def generate_session_id() -> str:
    """
    生成会话ID
    
    Returns:
        会话ID字符串
    """
    return f"session_{uuid.uuid4().hex}"


# ==================== 工具函数 ====================

def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    从Authorization header中提取token
    
    Args:
        authorization: Authorization header值，格式为 "Bearer <token>"
        
    Returns:
        token字符串，如果格式不正确返回None
    """
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]
