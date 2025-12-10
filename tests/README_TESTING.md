# 测试指南

## 测试数据库说明

### 为什么需要专门的测试数据库？

1. **数据安全** - 测试会频繁清空、重建数据，避免影响开发数据
2. **测试独立** - 每个测试从干净状态开始，互不影响
3. **可重复性** - 测试结果可预测，可随时重新运行
4. **并发运行** - 支持多个测试并发执行

### 数据库隔离

```
生产环境:  research_agent        (生产数据，绝不触碰)
开发环境:  research_agent        (开发数据)
测试环境:  test_research_agent   (测试专用，会被清空)
```

## 快速开始

### 1. 创建测试数据库

```bash
# 方法一: 使用 Python 脚本（推荐）
python scripts/setup_test_environment.py

# 方法二: 使用 SQL 脚本
mysql -u root -p < scripts/create_test_database.sql
```

### 2. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_auth.py -v

# 运行特定测试类
pytest tests/test_auth.py::TestUserRegistration -v

# 运行特定测试方法
pytest tests/test_auth.py::TestUserRegistration::test_register_success -v

# 带覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

### 3. 测试数据库清理（可选）

```bash
# 清理测试数据库
python scripts/cleanup_test_database.py
```

## 测试工作原理

### 测试流程

```
1. 创建测试数据库 (test_research_agent)
   └─> 只需创建一次

2. 运行测试
   ├─> 每个测试开始前
   │   ├─> 创建所有表
   │   └─> 获得干净的数据库会话
   │
   ├─> 执行测试
   │   └─> 在测试数据库中进行操作
   │
   └─> 测试结束后
       └─> 删除所有表（清理）

3. 重复步骤 2 进行下一个测试
```

### Fixtures 说明

在 `tests/conftest.py` 中定义了三个关键 fixtures:

1. **test_engine** - 测试数据库引擎
   - 创建/删除表结构
   - 作用域: function（每个测试独立）

2. **test_session** - 测试数据库会话
   - 提供数据库事务
   - 作用域: function

3. **client** - HTTP 测试客户端
   - 模拟 API 请求
   - 自动注入测试数据库会话

## 测试最佳实践

### 1. 测试隔离

```python
@pytest.mark.asyncio
async def test_something(client: AsyncClient, test_session: AsyncSession):
    # ✓ 每个测试都有独立的数据库会话
    # ✓ 测试之间互不影响
    pass
```

### 2. 测试数据准备

```python
@pytest.mark.asyncio
async def test_with_existing_user(client: AsyncClient):
    # 在测试中创建必要的数据
    await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # 继续测试...
```

### 3. 断言验证

```python
# ✓ 验证响应状态码
assert response.status_code == 201

# ✓ 验证响应数据
data = response.json()
assert "user" in data
assert data["user"]["email"] == "test@example.com"

# ✓ 验证数据库状态
result = await test_session.execute(
    select(User).where(User.email == "test@example.com")
)
user = result.scalar_one_or_none()
assert user is not None
```

## 常见问题

### Q: 测试失败后数据库会保留数据吗？

A: 不会。每个测试结束后，无论成功或失败，都会清理数据库表。

### Q: 可以并发运行测试吗？

A: 当前配置使用 function scope，适合顺序运行。如需并发，需要调整配置。

### Q: 测试会影响开发数据库吗？

A: 不会。测试使用独立的 `test_research_agent` 数据库。

### Q: 如何查看测试数据库的内容？

A: 可以在测试中添加断点，或使用 MySQL 客户端查看：
```bash
mysql -u root -p test_research_agent
```

### Q: 测试数据库需要运行迁移吗？

A: 不需要。测试使用 SQLAlchemy 的 `Base.metadata.create_all()` 直接创建表结构，确保与模型定义一致。

## 配置文件

### conftest.py
```python
# 测试数据库 URL
TEST_DATABASE_URL = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/test_research_agent"
```

## 环境变量

测试使用与开发相同的环境变量（从 `.env` 文件读取），但数据库名称不同：

```
开发: MYSQL_DATABASE=research_agent
测试: test_research_agent (硬编码在测试配置中)
```

## 测试覆盖率

```bash
# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 查看报告
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

## 持续集成 (CI)

在 CI 环境中，确保：
1. 安装测试依赖: `pip install -r tests/requirements-test.txt`
2. 设置环境变量
3. 创建测试数据库
4. 运行测试

## 相关文件

- `tests/conftest.py` - Pytest 配置和 fixtures
- `tests/test_auth.py` - 认证模块测试
- `tests/requirements-test.txt` - 测试依赖
- `scripts/setup_test_environment.py` - 测试环境设置脚本
- `scripts/create_test_database.sql` - 测试数据库 SQL 脚本

