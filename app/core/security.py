"""
安全工具模块
提供密码加密、JWT Token生成等功能
"""
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
    
    要求：
    - 长度 >= 8位
    - 必须包含大写字母
    - 必须包含小写字母
    - 必须包含数字
    - 必须包含特殊字符
    
    Args:
        password: 待验证的密码
        
    Returns:
        (是否合格, 错误信息)
    """
    if len(password) < 8:
        return False, "密码长度至少为8位"
    
    if not any(c.isupper() for c in password):
        return False, "密码必须包含至少一个大写字母"
    
    if not any(c.islower() for c in password):
        return False, "密码必须包含至少一个小写字母"
    
    if not any(c.isdigit() for c in password):
        return False, "密码必须包含至少一个数字"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "密码必须包含至少一个特殊字符"
    
    return True, ""


# ==================== JWT Token ====================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌（access_token）
    
    Args:
        data: 要编码到token中的数据（通常包含user_id, email, role等）
        expires_delta: 过期时间增量（可选，默认使用配置中的值）
        
    Returns:
        JWT token字符串
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()  # issued at
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    创建刷新令牌（refresh_token）
    
    Args:
        data: 要编码到token中的数据
        
    Returns:
        JWT refresh token字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"  # 标记为refresh token
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


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
    
    格式: u_<timestamp>_<random>
    
    Returns:
        用户ID字符串
    """
    import uuid
    from time import time
    
    timestamp = int(time() * 1000)  # 毫秒级时间戳
    random_part = uuid.uuid4().hex[:8]
    
    return f"u_{timestamp}_{random_part}"


# ==================== 会话ID生成 ====================

def generate_session_id() -> str:
    """
    生成会话ID
    
    Returns:
        会话ID字符串
    """
    import uuid
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

