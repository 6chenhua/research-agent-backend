"""
Pytest配置和共享fixtures
支持 Repository Pattern 的依赖注入测试
"""
import sys
from unittest.mock import MagicMock, AsyncMock

# Mock tiktoken和deepdoc相关模块，避免网络请求和导入错误
# 必须在导入main之前执行
sys.modules['tiktoken'] = MagicMock()
sys.modules['tiktoken.registry'] = MagicMock()
sys.modules['tiktoken_ext'] = MagicMock()
sys.modules['tiktoken_ext.openai_public'] = MagicMock()
sys.modules['tiktoken.load'] = MagicMock()

import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

from app.core.database import Base, get_session
from app.core.config import settings
from app.core.redis_client import close_redis_client
from main import app


# 测试数据库URL
TEST_DATABASE_URL = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/test_research_agent"


@pytest.fixture(scope="function")
def event_loop() -> Generator:
    """创建事件循环（每个测试独立）"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试HTTP客户端"""
    
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    # httpx 0.24+ 需要使用 ASGITransport
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()
    
    # 清理 Redis 连接，避免事件循环问题
    await close_redis_client()


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(client: AsyncClient) -> AsyncGenerator[tuple[AsyncClient, str, str], None]:
    """
    创建已认证的测试客户端
    
    返回: (client, access_token, user_id)
    """
    # 注册测试用户
    register_response = await client.post(
        "/api/auth/register",
        json={
            "username": "testuser_auth",
            "password": "TestPass123"
        }
    )
    user_id = register_response.json()["user_id"]
    
    # 登录获取token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": "testuser_auth",
            "password": "TestPass123"
        }
    )
    access_token = login_response.json()["access_token"]
    
    yield client, access_token, user_id


def auth_header(token: str) -> dict:
    """生成认证头"""
    return {"Authorization": f"Bearer {token}"}
