"""
AI Research Agent Backend
基于Graphiti的个性化科研助手系统
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import api_router
from app.core.database import init_db, close_db
from app.core.redis_client import close_redis_client
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库连接，关闭时清理资源
    """
    # 启动时
    print("🚀 应用启动中...")
    # 注意：生产环境不要自动创建表，应使用Alembic迁移
    # await init_db()
    print("✅ 应用启动成功")
    
    yield
    
    # 关闭时
    print("🛑 应用关闭中...")
    await close_db()
    await close_redis_client()
    print("✅ 应用已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## AI Research Agent Backend
    
    基于Graphiti知识图谱的个性化科研助手系统后端API。
    
    ### 主要功能
    - 🔐 用户认证与授权
    - 📥 论文上传与解析
    - 🧠 知识图谱管理
    - 💬 智能问答对话
    - 👤 用户画像构建
    - 🔍 智能搜索与推荐
    - 📊 数据可视化
    
    ### 认证方式
    大部分API需要JWT Token认证，请先注册/登录获取Token。
    
    在请求Header中添加：
    ```
    Authorization: Bearer <your_access_token>
    ```
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api")


@app.get(
    "/",
    summary="健康检查",
    description="返回API状态信息",
    tags=["系统"]
)
def root():
    """健康检查端点"""
    return {
        "message": "AI Research Agent Backend is running",
        "version": settings.APP_VERSION,
        "status": "healthy",
        "docs": "/docs"
    }


@app.get(
    "/health",
    summary="健康检查",
    description="详细的健康状态检查",
    tags=["系统"]
)
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app_name": settings.APP_NAME,
        "database": "connected",  # TODO: 实际检查数据库连接
        "redis": "connected"  # TODO: 实际检查Redis连接
    }
