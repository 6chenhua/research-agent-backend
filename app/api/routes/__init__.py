"""Main API router that aggregates all feature modules."""
from fastapi import APIRouter
from .auth import router as auth_router
from .chat import router as chat_router
from .graph import router as graph_router
from .papers import router as papers_router

api_router = APIRouter()

# 认证路由（auth router已经包含/auth前缀）
api_router.include_router(auth_router)

# 其他功能路由
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(graph_router, prefix="/graph", tags=["Graph"])
api_router.include_router(papers_router, prefix="/papers", tags=["Papers"])
