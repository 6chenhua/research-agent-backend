"""
CRUD 层模块
提供数据库的基本 CRUD (Create, Read, Update, Delete) 操作

架构设计：
使用 Repository Pattern，通过构造函数注入 AsyncSession
Service 层通过依赖注入获取 Repository 实例

使用示例:
```python
from app.crud import UserRepository
from app.api.dependencies.services import get_auth_service

# 在 FastAPI 路由中使用依赖注入
@router.post("/register")
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register(request)
```
"""
# Base Repository
from app.crud.base import BaseRepository

# Repository 类
from app.crud.user import UserRepository
from app.crud.session import SessionRepository
from app.crud.message import MessageRepository
from app.crud.paper import PaperRepository

__all__ = [
    # Base
    "BaseRepository",
    # Repositories
    "UserRepository",
    "SessionRepository", 
    "MessageRepository",
    "PaperRepository",
]
