"""
AI Research Agent Backend
基于Graphiti的个性化科研助手系统
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routes import api_router
from app.core.database import init_db, close_db
from app.core.redis_client import close_redis_client
from app.core.config import settings
from app.core.graphiti_enhanced import enhanced_graphiti

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库连接和Graphiti客户端，关闭时清理资源
    """
    # ==================== 启动阶段 ====================
    logger.info("🚀 应用启动中...")
    
    try:
        # 1. 初始化数据库（生产环境使用Alembic迁移）
        # await init_db()
        
        # 2. 初始化增强版 Graphiti 客户端
        logger.info("📊 初始化 Graphiti 客户端...")
        await enhanced_graphiti.initialize()
        logger.info("✅ Graphiti 客户端初始化成功")
        
        logger.info("✅ 应用启动成功")
        
    except Exception as e:
        logger.error(f"❌ 应用启动失败: {str(e)}")
        raise
    
    yield  # 应用运行
    
    # ==================== 关闭阶段 ====================
    logger.info("🛑 应用关闭中...")
    
    try:
        # 打印最终统计
        metrics = enhanced_graphiti.get_metrics()
        logger.info(f"📊 Graphiti 最终统计: {metrics}")
        
        # 1. 关闭 Graphiti 客户端
        logger.info("关闭 Graphiti 客户端...")
        await enhanced_graphiti.close()
        
        # 2. 关闭数据库连接
        await close_db()
        
        # 3. 关闭 Redis 连接
        await close_redis_client()
        
        logger.info("✅ 应用已关闭")
        
    except Exception as e:
        logger.error(f"❌ 应用关闭时出错: {str(e)}")


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
    try:
        # 检查 Graphiti 状态
        graphiti_status = "ok" if enhanced_graphiti._initialized else "not_initialized"
        metrics = enhanced_graphiti.get_metrics() if enhanced_graphiti._initialized else {}
        
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "app_name": settings.APP_NAME,
            "database": "connected",  # TODO: 实际检查数据库连接
            "redis": "connected",  # TODO: 实际检查Redis连接
            "graphiti": {
                "status": graphiti_status,
                "active_requests": metrics.get("active_requests", 0),
                "total_requests": metrics.get("total_requests", 0)
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get(
    "/metrics",
    summary="系统监控指标",
    description="获取 Graphiti 客户端的性能监控指标",
    tags=["系统"]
)
async def get_metrics():
    """获取系统监控指标
    
    返回 Graphiti 客户端的详细监控数据：
    - 总请求数、成功数、失败数
    - 超时数、慢查询数
    - 活跃请求数
    - Top 10 活跃用户
    """
    try:
        if not enhanced_graphiti._initialized:
            return {
                "error": "Graphiti client not initialized"
            }
        
        metrics = enhanced_graphiti.get_metrics()
        return {
            "status": "ok",
            "metrics": metrics,
            "timestamp": None  # TODO: 添加时间戳
        }
    except Exception as e:
        logger.error(f"获取监控指标失败: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
