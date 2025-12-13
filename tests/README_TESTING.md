# 测试指南

## 测试结构

```
tests/
├── conftest.py              # Pytest 配置和共享 fixtures
├── test_auth.py             # 认证模块测试（注册、登录、Token等）
├── test_research.py         # 研究会话模块测试（创建、列表）
├── test_chat.py             # 聊天模块测试（发送消息、历史记录）
├── test_crud_repository.py  # CRUD Repository 层单元测试
├── test_integration.py      # 端到端集成测试
├── test_graph.py            # 图谱模块测试（如果有）
└── test_user.py             # 用户模块测试（如果有）
```

## 运行测试

### 前置条件

1. 确保测试数据库已创建：
```sql
CREATE DATABASE test_research_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 确保 Redis 服务运行中

3. 安装测试依赖：
```bash
pip install -r tests/requirements-test.txt
```

### 运行所有测试

```bash
# 方式一：使用脚本
python scripts/run_tests.py

# 方式二：直接使用 pytest
python -m pytest tests/ -v
```

### 运行特定模块测试

```bash
# 认证模块
python scripts/run_tests.py auth
# 或
python -m pytest tests/test_auth.py -v

# 研究会话模块
python scripts/run_tests.py research

# 聊天模块
python scripts/run_tests.py chat

# CRUD 层
python scripts/run_tests.py crud

# 集成测试
python scripts/run_tests.py integration
```

### 运行带覆盖率的测试

```bash
python scripts/run_tests.py --coverage

# 或
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v
```

覆盖率报告会生成在 `htmlcov/` 目录下。

### 运行单个测试

```bash
# 运行特定测试类
python -m pytest tests/test_auth.py::TestUserRegistration -v

# 运行特定测试方法
python -m pytest tests/test_auth.py::TestUserRegistration::test_register_success -v
```

## 测试覆盖的功能

### 认证模块 (test_auth.py)

| 测试类 | 覆盖功能 |
|-------|---------|
| TestUserRegistration | 用户注册成功、重复用户名、无效输入等 |
| TestUserLogin | 登录成功、错误密码、不存在用户等 |
| TestTokenRefresh | Token刷新、无效Token等 |
| TestUserLogout | 登出、Token黑名单 |
| TestChangePassword | 修改密码、错误旧密码等 |

### 研究会话模块 (test_research.py)

| 测试类 | 覆盖功能 |
|-------|---------|
| TestCreateResearchSession | 创建会话、默认标题、域名验证、权限 |
| TestListResearchSessions | 列表查询、分页、排序、数据隔离 |

### 聊天模块 (test_chat.py)

| 测试类 | 覆盖功能 |
|-------|---------|
| TestSendMessage | 发送消息、空消息、无效会话、附件论文 |
| TestChatHistory | 获取历史、分页、排序、权限 |

### CRUD Repository 层 (test_crud_repository.py)

| 测试类 | 覆盖功能 |
|-------|---------|
| TestUserRepository | 用户CRUD操作 |
| TestSessionRepository | 会话CRUD操作 |
| TestMessageRepository | 消息CRUD操作 |
| TestPaperRepository | 论文CRUD操作 |

### 集成测试 (test_integration.py)

| 测试类 | 覆盖功能 |
|-------|---------|
| TestFullUserJourney | 完整用户流程（注册→登录→研究→登出） |
| TestErrorHandling | 错误处理、无效Token、请求格式 |
| TestDataIsolation | 用户数据隔离 |

## Mock 策略

测试中对以下外部服务进行了 Mock：

- **LLMClient**: Mock AI 回复，避免实际调用 LLM API
- **Graphiti**: Mock 图谱操作，避免需要 Neo4j 连接
- **Redis**: 使用真实 Redis 或 Mock（根据环境）

## 常见问题

### 1. 数据库连接失败

确保:
- MySQL 服务运行中
- 测试数据库 `test_research_agent` 已创建
- 环境变量配置正确

### 2. Redis 连接失败

确保:
- Redis 服务运行中
- Redis 连接配置正确

### 3. Import 错误

确保:
- 在项目根目录运行测试
- 已安装所有依赖: `pip install -r requirements.txt -r tests/requirements-test.txt`

### 4. 异步测试问题

如果遇到事件循环相关错误，检查:
- pytest-asyncio 版本兼容性
- conftest.py 中的 event_loop fixture 配置
