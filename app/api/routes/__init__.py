"""Main API router that aggregates all feature modules.

路由结构：
- /api/auth/* - 认证相关
- /api/user/* - 用户资料
- /api/v1/graph/* - 图谱模块（REQ-GRAPH-1~4）
- /api/chat/* - 聊天模块
- /api/papers/* - 论文模块
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .chat import router as chat_router
from .graph import router as graph_router
from .papers import router as papers_router
from .user import router as user_router

api_router = APIRouter()

# 认证路由（auth router已经包含/auth前缀）
api_router.include_router(auth_router)

# 用户资料路由（user router已经包含/user前缀）
api_router.include_router(user_router)

# 图谱模块路由（PRD要求使用/v1/graph前缀）
api_router.include_router(graph_router, prefix="/v1/graph", tags=["图谱模块"])

# 其他功能路由
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(papers_router, prefix="/papers", tags=["Papers"])
