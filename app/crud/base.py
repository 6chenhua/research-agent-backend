"""
CRUD 基类
实现 Repository Pattern，提供通用的 CRUD 操作
"""
from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

# 泛型类型变量
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    通用 Repository 基类
    
    使用示例:
    ```python
    class UserRepository(BaseRepository[User]):
        def __init__(self, session: AsyncSession):
            super().__init__(session, User)
        
        async def get_by_username(self, username: str) -> Optional[User]:
            return await self.get_by_field("username", username)
    ```
    """
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        """
        初始化 Repository
        
        Args:
            session: 数据库会话（由依赖注入提供）
            model: SQLAlchemy 模型类
        """
        self.session = session
        self.model = model
    
    async def get(self, id: Any) -> Optional[ModelType]:
        """根据主键获取单条记录"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_field(
        self, 
        field: str, 
        value: Any
    ) -> Optional[ModelType]:
        """根据字段值获取单条记录"""
        column = getattr(self.model, field)
        result = await self.session.execute(
            select(self.model).where(column == value)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """获取所有记录（分页）"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, obj: ModelType) -> ModelType:
        """创建记录"""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj
    
    async def update(self, obj: ModelType) -> ModelType:
        """更新记录"""
        await self.session.flush()
        await self.session.refresh(obj)
        return obj
    
    async def delete(self, obj: ModelType) -> None:
        """删除记录"""
        await self.session.delete(obj)
        await self.session.flush()
    
    async def count(self) -> int:
        """统计记录数"""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
    
    async def exists(self, id: Any) -> bool:
        """检查记录是否存在"""
        obj = await self.get(id)
        return obj is not None

