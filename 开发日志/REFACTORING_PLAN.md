# 📋 目录结构重构计划

## 🎯 目标

将混乱的 `models/` 和 `schemas/` 目录重新组织为标准的FastAPI项目结构。

---

## 📂 当前结构（问题）

```
app/
├── models/                    ← 混合了ORM模型和Pydantic模型 ❌
│   ├── db_models.py          ← SQLAlchemy模型 ✓
│   ├── auth_models.py        ← Pydantic模型 ✗（应该在schemas）
│   ├── chat_models.py        ← Pydantic模型 ✗
│   ├── paper_models.py       ← Pydantic模型 ✗
│   ├── user_models.py        ← Pydantic模型 ✗
│   ├── graph_models.py       ← Pydantic模型 ✗
│   ├── history_models.py     ← Pydantic模型 ✗
│   ├── community_models.py   ← Pydantic模型 ✗
│   └── recommendation_models.py ← Pydantic模型 ✗
│
└── schemas/                   ← 只有图谱相关schema
    ├── entities.py           ← 图谱实体 ✓
    ├── relations.py          ← 图谱关系 ✓
    └── validators.py         ← 验证器 ✓
```

**问题**:
1. **概念混淆**: models目录混合了两种不同用途的模型
2. **不符合标准**: 违反FastAPI最佳实践
3. **维护困难**: 新人容易搞混SQLAlchemy和Pydantic模型

---

## 📂 目标结构（正确）

```
app/
├── models/                    ← 只放SQLAlchemy ORM模型（数据库表）
│   ├── __init__.py
│   └── db_models.py          ← 所有数据库表模型
│       ├── User
│       ├── UserProfile
│       ├── ChatHistory
│       ├── ReadingHistory
│       ├── PaperMetadata
│       ├── TaskStatus
│       └── UserFeedback
│
└── schemas/                   ← 只放Pydantic模型（API请求响应）
    ├── __init__.py
    ├── auth.py               ← 认证相关（重命名自auth_models.py）
    ├── chat.py               ← 聊天相关（重命名自chat_models.py）
    ├── paper.py              ← 论文相关（重命名自paper_models.py）
    ├── user.py               ← 用户相关（重命名自user_models.py）
    ├── history.py            ← 历史记录相关（重命名自history_models.py）
    ├── graph.py              ← 图谱查询相关（重命名自graph_models.py）
    ├── community.py          ← 社区相关（重命名自community_models.py）
    ├── recommendation.py     ← 推荐相关（重命名自recommendation_models.py）
    ├── entities.py           ← 图谱实体schema（保持不变）
    ├── relations.py          ← 图谱关系schema（保持不变）
    └── validators.py         ← 验证器（保持不变）
```

---

## 🔄 迁移步骤

### Step 1: 移动Pydantic模型到schemas

```bash
# 重命名并移动
mv app/models/auth_models.py      app/schemas/auth.py
mv app/models/chat_models.py      app/schemas/chat.py
mv app/models/paper_models.py     app/schemas/paper.py
mv app/models/user_models.py      app/schemas/user.py
mv app/models/history_models.py   app/schemas/history.py
mv app/models/graph_models.py     app/schemas/graph.py
mv app/models/community_models.py app/schemas/community.py
mv app/models/recommendation_models.py app/schemas/recommendation.py
```

### Step 2: 更新 `app/models/__init__.py`

```python
"""
数据库模型模块
只包含SQLAlchemy ORM模型
"""
from app.models.db_models import (
    # 用户相关
    User,
    UserProfile,
    
    # 聊天和历史
    ChatHistory,
    ReadingHistory,
    
    # 论文
    PaperMetadata,
    
    # 任务和反馈
    TaskStatus,
    UserFeedback,
    
    # 枚举
    UserRole,
    ExpertiseLevel,
)

__all__ = [
    "User",
    "UserProfile",
    "ChatHistory",
    "ReadingHistory",
    "PaperMetadata",
    "TaskStatus",
    "UserFeedback",
    "UserRole",
    "ExpertiseLevel",
]
```

### Step 3: 更新 `app/schemas/__init__.py`

```python
"""
Pydantic模型模块
用于API请求和响应的数据验证
"""

# 认证相关
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    UserInfo,
    TokenPayload,
)

# 聊天相关
from app.schemas.chat import (
    # ChatRequest, ChatResponse等
)

# 论文相关
from app.schemas.paper import (
    # PaperUploadRequest, PaperResponse等
)

# 用户相关
from app.schemas.user import (
    # UserProfileResponse等
)

# 图谱相关
from app.schemas.entities import (
    PaperEntity,
    MethodEntity,
    DatasetEntity,
    # ... 其他实体
)

from app.schemas.relations import (
    RelationType,
    # ... 其他关系
)

__all__ = [
    # Auth
    "RegisterRequest",
    "RegisterResponse",
    "LoginRequest",
    "LoginResponse",
    # ... 其他
]
```

### Step 4: 批量更新导入语句

需要更新所有引用了这些模型的文件：

**示例1: `app/api/routes/auth.py`**

```python
# 旧的导入 ❌
from app.models.auth_models import RegisterRequest, LoginRequest

# 新的导入 ✅
from app.schemas.auth import RegisterRequest, LoginRequest
```

**示例2: `app/services/auth_service.py`**

```python
# 数据库模型
from app.models import User  # ✓ 保持不变

# API schema
from app.schemas.auth import RegisterRequest, LoginResponse  # ✓ 新路径
```

**需要更新的文件**:
- `app/api/routes/*.py` (所有路由文件)
- `app/services/*.py` (所有服务文件)
- `app/api/dependencies/*.py` (依赖注入)
- 其他引用了models中Pydantic模型的地方

### Step 5: 清理models目录

删除已迁移的文件：
```bash
rm app/models/auth_models.py
rm app/models/chat_models.py
# ... 删除其他已迁移的文件
```

保留：
```
app/models/
├── __init__.py
└── db_models.py    ← 只保留这一个文件
```

---

## 🔍 查找所有需要更新的导入

```bash
# 查找所有导入auth_models的地方
grep -r "from app.models.auth_models" app/

# 查找所有导入models中Pydantic模型的地方
grep -r "from app.models" app/ | grep -v "db_models"
```

---

## ✅ 验收标准

重构完成后：

- [ ] `app/models/` 目录只包含 `db_models.py`
- [ ] `app/schemas/` 目录包含所有Pydantic模型
- [ ] 所有导入语句已更新
- [ ] 代码可以正常运行
- [ ] 测试全部通过
- [ ] 没有未使用的导入警告

---

## 📝 重构后的导入规范

### ✅ 正确的导入方式

```python
# 导入数据库模型（ORM）
from app.models import User, ChatHistory, PaperMetadata

# 导入API schema（Pydantic）
from app.schemas.auth import RegisterRequest, LoginResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.paper import PaperUploadRequest

# 导入图谱schema
from app.schemas.entities import PaperEntity, MethodEntity
from app.schemas.relations import RelationType
```

### ❌ 错误的导入方式

```python
# 不要从models导入Pydantic模型
from app.models.auth_models import RegisterRequest  # ❌

# 不要从schemas导入ORM模型
from app.schemas import User  # ❌
```

---

## 📌 注意事项

1. **枚举类型**: `UserRole`, `ExpertiseLevel` 定义在 `db_models.py` 中，因为它们被SQLAlchemy使用
2. **关系引用**: SQLAlchemy的 `relationship` 保持不变，不受此重构影响
3. **Alembic迁移**: 数据库迁移不受影响，因为ORM模型位置没变
4. **向后兼容**: 可以在 `app/models/__init__.py` 中添加临时的导入别名，便于逐步迁移

---

## 🚀 执行时机

**建议**: 
- **现在执行**: 项目处于早期阶段，重构成本低
- **一次性完成**: 避免长期维护两套结构
- **周末进行**: 减少对日常开发的影响

**工作量估计**: 2-3小时
- 移动文件: 10分钟
- 更新导入: 1-2小时（取决于引用数量）
- 测试验证: 30-60分钟

---

## 📚 参考资料

- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [SQLAlchemy vs Pydantic](https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-pydantic-models)
- [Python项目结构最佳实践](https://docs.python-guide.org/writing/structure/)

---

**创建日期**: 2025-12-10  
**优先级**: P1（高优先级，影响代码质量和可维护性）  
**负责人**: 项目架构负责人

