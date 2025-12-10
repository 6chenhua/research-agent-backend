# 🚀 用户认证模块快速启动指南

## 📋 前置条件

1. **Python 3.10+** 已安装
2. **MySQL 8.0+** 已安装并运行
3. **Redis** 已安装并运行
4. **环境变量** 已配置（`.env`文件）

## 🔧 环境配置

### 1. 创建`.env`文件

```bash
# 复制示例配置
cp env.example .env
```

### 2. 配置环境变量

编辑`.env`文件，设置以下关键配置：

```env
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=research_agent

# Redis配置
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT配置
SECRET_KEY=your_secret_key_here_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. 安装依赖

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装测试依赖（可选）
pip install -r tests/requirements-test.txt
```

## 🗄️ 数据库初始化

### 方法1: 使用Alembic迁移（推荐）

```bash
# 1. 创建数据库
mysql -u root -p
CREATE DATABASE research_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE test_research_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 2. 执行迁移
alembic upgrade head

# 3. 查看迁移状态
alembic current
```

### 方法2: 使用初始化脚本

```bash
# 运行初始化脚本
python scripts/init_db.py
```

## 🚀 启动应用

### 开发模式

```bash
# 使用uvicorn启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或使用run.py
python run.py
```

### 生产模式

```bash
# 使用gunicorn + uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📖 访问API文档

启动应用后，访问以下URL：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 测试认证功能

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

### 2. 用户注册

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "测试用户",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

**响应示例**:
```json
{
  "user": {
    "user_id": "u_1702345678901_abc123",
    "username": "测试用户",
    "email": "test@example.com",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-12-10T10:30:00Z",
    "last_login": null
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 3. 用户登录

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### 4. 获取用户信息

```bash
# 使用注册/登录返回的access_token
export TOKEN="your_access_token_here"

curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. 修改密码

```bash
curl -X POST "http://localhost:8000/api/auth/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "TestPass123!",
    "new_password": "NewPass456!"
  }'
```

### 6. 刷新Token

```bash
# 使用refresh_token
export REFRESH_TOKEN="your_refresh_token_here"

curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

### 7. 登出

```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer $TOKEN"
```

## 🧪 运行单元测试

```bash
# 运行所有认证测试
pytest tests/test_auth.py -v

# 运行特定测试类
pytest tests/test_auth.py::TestUserRegistration -v

# 生成覆盖率报告
pytest tests/test_auth.py --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 🔍 验证功能

### ✅ 检查清单

- [ ] 应用成功启动
- [ ] 数据库连接正常
- [ ] Redis连接正常
- [ ] 用户注册成功
- [ ] 用户登录成功
- [ ] Token刷新成功
- [ ] 获取用户信息成功
- [ ] 修改密码成功
- [ ] 用户登出成功
- [ ] JWT认证中间件正常工作
- [ ] 密码加密正确（bcrypt, cost=12）
- [ ] Token黑名单机制正常
- [ ] 登录失败锁定机制正常

### 🔐 安全验证

```bash
# 1. 验证密码强度要求
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@example.com",
    "password": "weak"
  }'
# 预期: 400 Bad Request，提示密码不符合要求

# 2. 验证邮箱唯一性
# 注册两次相同邮箱
# 预期: 第二次返回400 Bad Request

# 3. 验证登录失败锁定
# 连续3次错误密码登录
# 预期: 第4次返回429 Too Many Requests

# 4. 验证Token黑名单
# 登出后使用相同Token访问/api/auth/me
# 预期: 401 Unauthorized
```

## 🐛 故障排查

### 问题1: 数据库连接失败

```bash
# 检查MySQL是否运行
mysql -u root -p -e "SELECT 1"

# 检查数据库是否存在
mysql -u root -p -e "SHOW DATABASES LIKE 'research_agent'"

# 检查.env配置是否正确
cat .env | grep MYSQL
```

### 问题2: Redis连接失败

```bash
# 检查Redis是否运行
redis-cli ping
# 预期输出: PONG

# 检查Redis配置
cat .env | grep REDIS
```

### 问题3: Alembic迁移失败

```bash
# 查看当前迁移状态
alembic current

# 查看迁移历史
alembic history

# 回滚到上一版本
alembic downgrade -1

# 重新升级
alembic upgrade head
```

### 问题4: 测试失败

```bash
# 确保测试数据库存在
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS test_research_agent"

# 清理测试数据
mysql -u root -p test_research_agent -e "DROP TABLE IF EXISTS users, user_profiles, chat_history, reading_history, paper_metadata, task_status, user_feedback"

# 重新运行测试
pytest tests/test_auth.py -v
```

## 📊 性能监控

### 查看API响应时间

在Swagger UI (http://localhost:8000/docs) 中测试各个端点，观察响应时间：

- 注册: < 1秒
- 登录: < 500ms
- Token刷新: < 200ms
- 获取用户信息: < 200ms
- JWT认证中间件: < 50ms

### 查看Redis缓存

```bash
# 连接Redis
redis-cli

# 查看所有键
KEYS *

# 查看黑名单Token
KEYS blacklist:*

# 查看登录失败计数
KEYS failed_login:*

# 查看某个键的值
GET blacklist:your_token_here

# 查看键的TTL
TTL blacklist:your_token_here
```

## 📝 下一步

认证模块已完成，可以继续开发其他模块：

1. **Module B**: 知识图谱模块
2. **Module A**: 论文管理模块
3. **Module C**: 智能问答模块
4. **Module E**: 搜索推荐模块
5. **Module F**: 社区管理模块
6. **Module G**: 图谱可视化模块

## 📞 获取帮助

- **API文档**: http://localhost:8000/docs
- **开发文档**: `app/api/routes/README_AUTH.md`
- **任务分配表**: `开发任务分配表.md`
- **PRD文档**: `PRD_产品需求文档.md`

---

**祝开发顺利！** 🚀

