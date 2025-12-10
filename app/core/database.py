"""
数据库配置和连接管理
使用异步SQLAlchemy
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
from app.core.config import settings

# 构建异步数据库URL
# 格式: mysql+asyncmy://user:password@host:port/database?charset=utf8mb4
DATABASE_URL = (
    f"mysql+asyncmy://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}"
    f"/{settings.MYSQL_DATABASE}?charset=utf8mb4"
)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # 开发环境输出SQL日志
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 允许连接池最大的连接数
    pool_timeout=30,  # 获得连接超时时间（秒）
    pool_recycle=3600,  # 连接回收时间（1小时）
    pool_pre_ping=True,  # 连接前预检查，确保连接有效
    # 对于异步引擎，建议使用NullPool或默认连接池
)

# 创建异步Session工厂
AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=True,  # 查询前自动flush
    expire_on_commit=False,  # commit后不立即过期对象
)

# 创建Base类
Base = declarative_base()


# 依赖注入：获取数据库会话
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI依赖注入函数
    自动管理session的生命周期
    
    使用示例:
    @router.get("/users")
    async def get_users(session: AsyncSession = Depends(get_session)):
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 初始化数据库
async def init_db():
    """
    初始化数据库（创建所有表）
    仅用于开发环境，生产环境使用Alembic迁移
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 关闭数据库连接
async def close_db():
    """
    关闭数据库引擎
    在应用关闭时调用
    """
    await engine.dispose()

