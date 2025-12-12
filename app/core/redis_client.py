"""
Redis客户端管理
用于Token黑名单、登录限流等
根据PRD_认证模块.md设计
"""
import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

# 全局Redis客户端实例
_redis_client: Optional[redis.Redis] = None

# 登录限流配置（PRD要求：15分钟内最多5次）
LOGIN_RATE_LIMIT_WINDOW = 900  # 15分钟（秒）
LOGIN_MAX_ATTEMPTS = 5  # 最大尝试次数


async def get_redis_client() -> redis.Redis:
    """
    获取Redis客户端实例（单例模式）
    
    Returns:
        Redis客户端
    """
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10
        )
    
    return _redis_client


async def close_redis_client():
    """
    关闭Redis客户端连接
    在应用关闭时调用
    """
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


# ==================== Token黑名单管理 ====================

async def add_token_to_blacklist(token: str, ttl: int):
    """
    将token添加到黑名单
    
    Args:
        token: JWT token字符串
        ttl: 过期时间（秒）
    """
    client = await get_redis_client()
    await client.setex(f"blacklist:{token}", ttl, "1")


async def is_token_blacklisted(token: str) -> bool:
    """
    检查token是否在黑名单中
    
    Args:
        token: JWT token字符串
        
    Returns:
        是否在黑名单中
    """
    client = await get_redis_client()
    result = await client.exists(f"blacklist:{token}")
    return result > 0


# ==================== 登录失败次数管理 ====================

async def increment_failed_login(username: str) -> int:
    """
    增加登录失败次数
    PRD要求：15分钟内最多5次
    
    Args:
        username: 用户名
        
    Returns:
        当前失败次数
    """
    client = await get_redis_client()
    key = f"login_attempt:{username}"
    
    # 增加计数
    count = await client.incr(key)
    
    # 设置15分钟过期（仅首次设置）
    if count == 1:
        await client.expire(key, LOGIN_RATE_LIMIT_WINDOW)
    
    return count


async def reset_failed_login(username: str):
    """
    重置登录失败次数
    
    Args:
        username: 用户名
    """
    client = await get_redis_client()
    await client.delete(f"login_attempt:{username}")


async def get_failed_login_count(username: str) -> int:
    """
    获取登录失败次数
    
    Args:
        username: 用户名
        
    Returns:
        失败次数
    """
    client = await get_redis_client()
    count = await client.get(f"login_attempt:{username}")
    return int(count) if count else 0


async def check_rate_limit(username: str) -> bool:
    """
    检查是否超过登录限制
    
    Args:
        username: 用户名
        
    Returns:
        True表示可以继续尝试，False表示已超过限制
    """
    count = await get_failed_login_count(username)
    return count < LOGIN_MAX_ATTEMPTS


# ==================== 缓存管理 ====================

async def cache_set(key: str, value: str, ttl: Optional[int] = None):
    """
    设置缓存
    
    Args:
        key: 缓存键
        value: 缓存值
        ttl: 过期时间（秒），None表示永不过期
    """
    client = await get_redis_client()
    if ttl:
        await client.setex(key, ttl, value)
    else:
        await client.set(key, value)


async def cache_get(key: str) -> Optional[str]:
    """
    获取缓存
    
    Args:
        key: 缓存键
        
    Returns:
        缓存值，不存在返回None
    """
    client = await get_redis_client()
    return await client.get(key)


async def cache_delete(key: str):
    """
    删除缓存
    
    Args:
        key: 缓存键
    """
    client = await get_redis_client()
    await client.delete(key)


async def cache_exists(key: str) -> bool:
    """
    检查缓存是否存在
    
    Args:
        key: 缓存键
        
    Returns:
        是否存在
    """
    client = await get_redis_client()
    result = await client.exists(key)
    return result > 0
