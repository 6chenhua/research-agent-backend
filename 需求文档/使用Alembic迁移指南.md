# 📚 Alembic数据库迁移使用指南

## 🎯 快速开始

### 1. 安装依赖

```bash
pip install sqlalchemy alembic asyncmy pymysql
```

### 2. 配置环境变量

在`.env`文件中配置MySQL连接：

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=research_agent
```

### 3. 初始化并执行迁移

**Windows**:
```bash
scripts\init_alembic.bat
```

**Linux/Mac**:
```bash
chmod +x scripts/init_alembic.sh
./scripts/init_alembic.sh
```

**或手动执行**:
```bash
# 执行迁移到最新版本
alembic upgrade head

# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

---

## 📋 常用Alembic命令

### 查看迁移状态

```bash
# 查看当前数据库版本
alembic current

# 查看迁移历史
alembic history

# 查看详细历史（包含注释）
alembic history --verbose
```

### 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision>

# 升级N个版本
alembic upgrade +2

# 回滚到上一个版本
alembic downgrade -1

# 回滚到基础版本（删除所有表）
alembic downgrade base
```

### 创建迁移脚本

```bash
# 手动创建迁移脚本
alembic revision -m "description of changes"

# 自动生成迁移脚本（检测模型变化）
alembic revision --autogenerate -m "add new columns"
```

---

## 🔧 使用异步SQLAlchemy

### 1. 导入数据库连接

```python
from app.core.database import get_session, AsyncSession
from app.models.db_models import User, ChatHistory
from sqlalchemy import select
from fastapi import Depends
```

### 2. 在API中使用

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session

router = APIRouter()

@router.get("/users")
async def get_users(session: AsyncSession = Depends(get_session)):
    """获取所有用户"""
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users

@router.get("/users/{user_id}")
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    """获取单个用户"""
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    return user

@router.post("/users")
async def create_user(
    user_data: dict, 
    session: AsyncSession = Depends(get_session)
):
    """创建用户"""
    user = User(**user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

### 3. 复杂查询示例

```python
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

# 1. 基本查询
async def get_active_users(session: AsyncSession):
    result = await session.execute(
        select(User).where(User.is_active == True)
    )
    return result.scalars().all()

# 2. 关联查询（加载关系）
async def get_user_with_profile(user_id: str, session: AsyncSession):
    result = await session.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.user_id == user_id)
    )
    return result.scalar_one_or_none()

# 3. 聚合查询
async def get_user_stats(user_id: str, session: AsyncSession):
    result = await session.execute(
        select(func.count(ChatHistory.id))
        .where(ChatHistory.user_id == user_id)
    )
    chat_count = result.scalar()
    return {"chat_count": chat_count}

# 4. 分页查询
async def get_chat_history_paginated(
    user_id: str, 
    page: int, 
    page_size: int,
    session: AsyncSession
):
    offset = (page - 1) * page_size
    result = await session.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.timestamp.desc())
        .limit(page_size)
        .offset(offset)
    )
    return result.scalars().all()

# 5. 更新操作
async def update_user(user_id: str, updates: dict, session: AsyncSession):
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        for key, value in updates.items():
            setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
    return user

# 6. 删除操作
async def delete_user(user_id: str, session: AsyncSession):
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        await session.delete(user)
        await session.commit()
        return True
    return False
```

---

## 📊 数据库表结构

### 已创建的表

1. **users** - 用户表
2. **user_profiles** - 用户画像表
3. **chat_history** - 聊天历史表
4. **reading_history** - 阅读历史表
5. **paper_metadata** - 论文元数据表
6. **task_status** - 任务状态表
7. **user_feedback** - 用户反馈表

### 查看表结构

```bash
# 连接MySQL
mysql -u root -p

# 选择数据库
USE research_agent;

# 查看所有表
SHOW TABLES;

# 查看表结构
DESCRIBE users;
DESCRIBE user_profiles;
```

---

## 🔄 开发工作流

### 1. 修改模型

在`app/models/db_models.py`中修改模型：

```python
class User(Base):
    __tablename__ = "users"
    
    # 新增字段
    phone = Column(String(20), nullable=True, comment="手机号")
```

### 2. 生成迁移脚本

```bash
alembic revision --autogenerate -m "add phone to users"
```

### 3. 检查生成的迁移脚本

打开`alembic/versions/xxx_add_phone_to_users.py`，检查：
- `upgrade()`函数是否正确
- `downgrade()`函数是否正确

### 4. 执行迁移

```bash
alembic upgrade head
```

### 5. 验证

```bash
# 查看当前版本
alembic current

# 连接数据库验证
mysql -u root -p
USE research_agent;
DESCRIBE users;
```

---

## ⚠️ 注意事项

### 1. 迁移脚本管理

- ✅ 迁移脚本必须提交到Git
- ✅ 团队成员按顺序执行迁移
- ✅ 生产环境谨慎执行迁移
- ❌ 不要手动修改数据库结构

### 2. 自动生成迁移

`--autogenerate`会检测：
- ✅ 表的添加和删除
- ✅ 列的添加和删除
- ✅ 列类型的修改
- ❌ 可能检测不到：列名修改、约束变更

需要手动检查生成的脚本！

### 3. 生产环境最佳实践

```bash
# 1. 备份数据库
mysqldump -u root -p research_agent > backup.sql

# 2. 在测试环境测试迁移
alembic upgrade head

# 3. 确认无误后在生产环境执行
alembic upgrade head

# 4. 如果出错，立即回滚
alembic downgrade -1
```

### 4. 异步操作注意事项

```python
# ✅ 正确：使用await
result = await session.execute(select(User))
users = result.scalars().all()

# ❌ 错误：忘记await
result = session.execute(select(User))  # 返回coroutine对象

# ✅ 正确：commit后refresh
await session.commit()
await session.refresh(user)

# ❌ 错误：不commit直接返回
session.add(user)
return user  # 数据未保存
```

---

## 🐛 常见问题

### 1. 迁移失败

```bash
# 查看当前状态
alembic current

# 如果显示错误，尝试回滚
alembic downgrade -1

# 重新执行
alembic upgrade head
```

### 2. 数据库连接失败

检查`.env`配置：
- MySQL是否启动
- 用户名密码是否正确
- 数据库是否已创建

### 3. 模型修改未检测到

```bash
# 确保模型已导入到alembic/env.py
from app.models.db_models import *

# 重新生成迁移
alembic revision --autogenerate -m "changes"
```

---

## 📚 参考资源

- [Alembic官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI数据库教程](https://fastapi.tiangolo.com/tutorial/sql-databases/)

---

**创建时间**: 2025-12-09  
**更新时间**: 2025-12-09

