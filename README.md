# 🎓 AI Research Agent Backend

基于Graphiti知识图谱的个性化科研助手系统后端

---

## 📖 项目简介

AI Research Agent 是一个基于知识图谱的智能科研助手系统，帮助研究人员：
- 📥 管理和解析学术论文
- 🧠 构建个性化知识图谱
- 💬 智能问答和文献检索
- 👤 自动构建用户研究画像
- 🔍 智能推荐相关文献

---

## 🏗️ 技术栈

### 后端框架
- **FastAPI** - 现代Python Web框架
- **SQLAlchemy** - 异步ORM
- **Alembic** - 数据库迁移

### 数据库
- **MySQL 8.0** - 关系型数据库（用户、历史记录）
- **Neo4j 5.14** - 图数据库（知识图谱）
- **Redis 7** - 缓存和Token黑名单

### 核心技术
- **Graphiti** - 知识图谱管理
- **JWT** - 用户认证
- **bcrypt** - 密码加密
- **Celery** - 异步任务队列
- **OpenAI** - LLM支持

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- Docker Desktop
- MySQL 8.0+
- Git

### 2. 克隆项目

```bash
git clone <repository_url>
cd graduationProject
```

### 3. 配置环境

```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env，填写实际配置
# 重点配置：
# - MYSQL_PASSWORD（MySQL密码）
# - SECRET_KEY（JWT密钥，至少32字符）
# - OPENAI_API_KEY（OpenAI API密钥）
```

### 4. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 5. 启动Docker服务

```bash
# 启动MySQL、Redis、Neo4j
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 6. 创建数据库

**方式一：使用SQL脚本（推荐）**
```bash
mysql -u root -p < scripts/create_database.sql
```

**方式二：使用Alembic迁移**
```bash
alembic upgrade head
```

详细说明见：[scripts/执行SQL脚本指南.md](scripts/执行SQL脚本指南.md)

### 7. 启动应用

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 访问文档

启动成功后访问：

| 服务 | URL | 说明 |
|-----|-----|------|
| **API文档（Swagger）** | http://localhost:8000/docs | 交互式API测试 |
| **API文档（Redoc）** | http://localhost:8000/redoc | 可打印文档 |
| **健康检查** | http://localhost:8000/health | 服务状态 |
| **Neo4j浏览器** | http://localhost:7474 | 图数据库管理 |

---

## 🔐 测试账号

数据库创建后会自动插入3个测试用户：

| 邮箱 | 密码 | 角色 |
|-----|-----|------|
| test1@example.com | Test1234! | 学生 |
| researcher@example.com | Test1234! | 研究员 |
| teacher@example.com | Test1234! | 教师 |

---

## 🗂️ 项目结构

```
graduationProject/
├── app/                          # 应用代码
│   ├── api/                      # API路由
│   │   ├── dependencies/         # 依赖注入
│   │   │   └── auth.py          # JWT认证中间件
│   │   └── routes/              # API端点
│   │       ├── auth.py          # 认证API（注册/登录）
│   │       ├── chat.py          # 聊天API
│   │       ├── graph.py         # 图谱API
│   │       └── papers.py        # 论文管理API
│   ├── core/                    # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库连接
│   │   ├── security.py         # 安全工具（JWT/密码）
│   │   └── redis_client.py     # Redis客户端
│   ├── models/                  # 数据模型
│   │   ├── db_models.py        # SQLAlchemy模型
│   │   ├── auth_models.py      # 认证请求/响应模型
│   │   └── ...
│   └── services/               # 业务逻辑
│       ├── auth_service.py     # 认证服务
│       ├── agent_service.py    # AI Agent服务
│       └── ...
├── alembic/                     # 数据库迁移
│   ├── versions/               # 迁移脚本
│   │   └── 001_initial_tables.py
│   └── env.py                  # Alembic配置
├── scripts/                     # 工具脚本
│   ├── create_database.sql     # 数据库创建脚本 ⭐
│   ├── init_alembic.sh/.bat   # Alembic初始化
│   ├── start_dev.sh/.bat      # 开发环境启动
│   └── 执行SQL脚本指南.md      # SQL执行说明
├── main.py                      # 应用入口
├── requirements.txt             # Python依赖
├── docker-compose.yml           # Docker配置
├── alembic.ini                  # Alembic配置
├── env.example                  # 环境变量模板
├── 快速开始.md                  # 快速开始指南 ⭐
├── 使用Alembic迁移指南.md       # Alembic使用说明
├── PRD_产品需求文档.md          # 产品需求文档
└── 开发任务分配表.md            # 开发任务分工

⭐ = 重要文件
```

---

## 📊 数据库表结构

系统包含7个主要数据表：

| 表名 | 说明 | 行数估计 |
|-----|------|---------|
| `users` | 用户基本信息 | 10K-100K |
| `user_profiles` | 用户画像 | 10K-100K |
| `chat_history` | 聊天记录 | 100K-1M |
| `reading_history` | 阅读历史 | 100K-1M |
| `paper_metadata` | 论文元数据缓存 | 10K-100K |
| `task_status` | 异步任务状态 | 10K-100K |
| `user_feedback` | 用户反馈 | 1K-10K |

---

## 🔧 开发指南

### 运行测试

```bash
pytest tests/
```

### 数据库迁移

```bash
# 创建新的迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1

# 查看历史
alembic history
```

### 代码格式化

```bash
# 使用black格式化
black app/

# 使用isort整理导入
isort app/
```

---

## 📖 API文档

### 认证模块 (Module H)

#### 1. 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "张三",
  "email": "zhangsan@example.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "user_role": "student"
}
```

#### 2. 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "zhangsan@example.com",
  "password": "SecurePass123!"
}
```

响应：
```json
{
  "user": {
    "user_id": "u_1234567890_abc",
    "username": "张三",
    "email": "zhangsan@example.com",
    "user_role": "student"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### 3. 获取当前用户信息
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### 4. 刷新Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 5. 用户登出
```http
POST /api/auth/logout
Authorization: Bearer <access_token>
```

#### 6. 修改密码
```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!",
  "confirm_new_password": "NewPass456!"
}
```

---

## 🔒 安全特性

- ✅ JWT Token认证（1小时过期）
- ✅ Refresh Token（7天过期）
- ✅ 密码bcrypt加密（cost=12）
- ✅ 密码强度验证（≥8位，含大小写+数字+特殊字符）
- ✅ 登录失败锁定（3次失败锁定5分钟）
- ✅ Token黑名单（Redis）
- ✅ CORS配置
- ✅ SQL注入防护（参数化查询）

---

## 📝 开发状态

### ✅ 已完成

- [x] 项目架构设计
- [x] 数据库模型定义
- [x] 用户认证模块（Module H）
  - [x] 用户注册
  - [x] 用户登录
  - [x] Token刷新
  - [x] 用户登出
  - [x] 获取用户信息
  - [x] 修改密码
  - [x] JWT中间件
- [x] 数据库迁移配置（Alembic）
- [x] Docker环境配置
- [x] API文档（Swagger）

### 🚧 进行中

- [ ] 论文管理模块（Module A）
- [ ] 知识图谱模块（Module B）
- [ ] 智能问答模块（Module C）

### 📅 待开发

- [ ] 用户画像模块（Module D）
- [ ] 搜索推荐模块（Module E）
- [ ] 社区管理模块（Module F）
- [ ] 可视化模块（Module G）

详见：[开发任务分配表.md](开发任务分配表.md)

---

## 🐛 已知问题

暂无

---

## 📚 相关文档

| 文档 | 说明 |
|-----|------|
| [快速开始.md](快速开始.md) | 快速开始指南 |
| [PRD_产品需求文档.md](PRD_产品需求文档.md) | 完整产品需求 |
| [开发任务分配表.md](开发任务分配表.md) | 开发任务分工 |
| [使用Alembic迁移指南.md](使用Alembic迁移指南.md) | 数据库迁移指南 |
| [scripts/执行SQL脚本指南.md](scripts/执行SQL脚本指南.md) | SQL脚本执行说明 |

---

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

MIT License

---

## 📧 联系方式

项目负责人：[项目经理]

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Graphiti](https://github.com/getzep/graphiti)
- [Neo4j](https://neo4j.com/)

---

**最后更新**: 2025-12-09  
**版本**: v1.2

