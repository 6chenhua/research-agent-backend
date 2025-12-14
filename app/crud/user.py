"""
用户 Repository
处理 users 表的所有数据库操作
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import User
from app.crud.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    用户数据访问层
    
    使用示例（在 Service 中）:
    ```python
    class AuthService:
        def __init__(self, user_repo: UserRepository):
            self.user_repo = user_repo
        
        async def login(self, username: str, password: str):
            user = await self.user_repo.get_by_username(username)
            ...
    ```
    
    使用示例（在 Route 中通过依赖注入）:
    ```python
    @router.get("/users/{user_id}")
    async def get_user(
        user_id: str,
        auth_service: AuthService = Depends(get_auth_service)
    ):
        ...
    ```
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名查询用户
        
        Args:
            username: 用户名
            
        Returns:
            用户对象或 None
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        根据用户ID查询用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象或 None
        """
        result = await self.session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self,
        user_id: str,
        username: str,
        password_hash: str,
        email: Optional[str] = None
    ) -> User:
        """
        创建新用户
        
        Args:
            user_id: 用户ID
            username: 用户名
            password_hash: 密码哈希
            email: 邮箱（可选）
            
        Returns:
            创建的用户对象
        """
        new_user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash
        )
        return await self.create(new_user)
    
    async def update_last_login(self, user: User) -> User:
        """
        更新用户最后登录时间
        
        Args:
            user: 用户对象
            
        Returns:
            更新后的用户对象
        """
        user.last_login_at = datetime.utcnow()
        return await self.update(user)
    
    async def update_password(self, user: User, new_password_hash: str) -> User:
        """
        更新用户密码
        
        Args:
            user: 用户对象
            new_password_hash: 新密码哈希
            
        Returns:
            更新后的用户对象
        """
        user.password_hash = new_password_hash
        return await self.update(user)
    
    async def exists_by_username(self, username: str) -> bool:
        """
        检查用户名是否已存在
        
        Args:
            username: 用户名
            
        Returns:
            是否存在
        """
        user = await self.get_by_username(username)
        return user is not None
    
    async def get_preferences(self, user_id: str) -> Optional[dict]:
        """
        获取用户偏好设置
        
        Args:
            user_id: 用户ID
            
        Returns:
            偏好设置字典，如果用户不存在返回 None
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        return user.preferences or {}
    
    async def update_preferences(
        self, 
        user_id: str, 
        preferences: dict,
        merge: bool = True
    ) -> Optional[User]:
        """
        更新用户偏好设置
        
        Args:
            user_id: 用户ID
            preferences: 偏好设置字典
            merge: 是否合并现有设置（True）或完全替换（False）
            
        Returns:
            更新后的用户对象，如果用户不存在返回 None
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        if merge and user.preferences:
            # 合并现有设置
            merged = user.preferences.copy()
            merged.update(preferences)
            user.preferences = merged
        else:
            # 完全替换
            user.preferences = preferences
        
        return await self.update(user)
    
    async def update_profile_field(
        self,
        user_id: str,
        field: str,
        value
    ) -> Optional[User]:
        """
        更新用户画像的单个字段
        
        Args:
            user_id: 用户ID
            field: 字段名（如 'research_interests', 'expertise_level'）
            value: 字段值
            
        Returns:
            更新后的用户对象
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        preferences = user.preferences or {}
        preferences[field] = value
        user.preferences = preferences
        
        return await self.update(user)