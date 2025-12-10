# 📋 产品需求文档 (PRD)
# AI科研助手系统 v1.0

**文档版本**: v1.4 (新增交互式图谱可视化功能)  
**创建日期**: 2025-12-09  
**最后更新**: 2025-12-10  
**项目经理**: [Your Name]  
**项目代号**: ResearchAgent  
**预计交付**: 2026-02-09（2个月）

---

## 📑 目录

1. [产品概述](#1-产品概述)
2. [目标用户与场景](#2-目标用户与场景)
3. [产品目标](#3-产品目标)
4. [功能需求](#4-功能需求)
5. [数据需求](#5-数据需求)
6. [非功能需求](#6-非功能需求)
7. [技术架构](#7-技术架构)
8. [开发分工](#8-开发分工)
9. [里程碑与交付](#9-里程碑与交付)
10. [验收标准](#10-验收标准)
11. [风险管理](#11-风险管理)

---

## 1. 产品概述

### 1.1 产品定位

**AI科研助手系统**是一款基于知识图谱的智能学术研究助手，旨在通过自动化的论文解析、知识抽取和个性化推荐，帮助科研人员高效管理学术信息、发现研究机会。

### 1.2 核心价值主张

| 痛点 | 解决方案 | 价值 |
|-----|---------|------|
| 海量论文难以管理 | 自动解析PDF，构建知识图谱 | 节省80%信息整理时间 |
| 知识碎片化 | 实体关系网络，结构化知识 | 提升知识连接效率 |
| 缺乏个性化 | 用户画像，智能推荐 | 精准匹配研究兴趣 |
| 信息孤岛 | 外部搜索集成，自动扩展 | 获取最新研究进展 |

### 1.3 核心技术

- **知识图谱引擎**: Graphiti + Neo4j
- **AI Agent**: LangChain + OpenAI GPT-4
- **向量搜索**: Sentence-Transformers
- **后端框架**: FastAPI + Celery

---

## 2. 目标用户与场景

### 2.1 目标用户画像

**主要用户**：
- 研究生（硕士/博士）
- 科研工作者
- 高校教师
- 企业研发人员

**用户特征**：
- 每周阅读5-10篇论文
- 需要跟踪特定研究方向
- 需要管理大量学术资料
- 有论文对比和综述需求

### 2.2 典型使用场景

#### 场景1: 文献调研
```
用户：小李（研究生）
目标：调研视觉Transformer最新进展
流程：
1. 提问："最近视觉Transformer有哪些改进？"
2. 系统自动搜索个人图谱 + 全局图谱
3. 信息不足时自动搜索arXiv
4. 生成结构化回答，附引用来源
5. 自动更新用户画像
```

#### 场景2: 论文阅读
```
用户：小王（科研工作者）
目标：快速理解一篇新论文
流程：
1. 上传PDF文件
2. 系统自动解析：提取方法、数据集、结果
3. 构建知识图谱：论文-方法-任务关系
4. 生成摘要和创新点
5. 推荐相关论文
```

#### 场景3: 研究规划
```
用户：张教授（导师）
目标：为学生规划研究方向
流程：
1. 查看学生的用户画像
2. 查看学生阅读历史和兴趣标签
3. 系统推荐潜在研究方向
4. 对比不同方向的论文
5. 生成研究建议
```

---

## 3. 产品目标

### 3.1 业务目标

| 指标 | 目标值 | 衡量方式 |
|-----|--------|---------|
| 用户留存率 | > 70% | 月活跃用户数 |
| 平均使用时长 | > 30分钟/周 | 用户行为统计 |
| 论文解析准确率 | > 85% | 人工抽样验证 |
| 推荐精准度 | > 60% | 用户反馈 |
| 查询响应时间 | < 3秒 | API监控 |

### 3.2 技术目标

- ✅ 图谱节点数: 支持10万+
- ✅ 并发用户数: 100+
- ✅ API可用性: 99.5%
- ✅ 数据准确性: 90%+
- ✅ 系统扩展性: 模块化，易扩展

### 3.3 MVP目标（第一版本）

**核心功能**：
1. 论文PDF上传和解析
2. 基于图谱的智能问答
3. 用户个人图谱管理
4. 基础推荐功能

**排除功能**（延后到v2.0）：
- 前端UI（由前端团队负责）
- 用户权限管理
- 多语言支持
- 移动端适配
- 用户画像构建
- 阅读历史追踪
- 论文推荐
- 论文对比

---

## 4. 功能需求

### 4.1 功能模块总览

```
ResearchAgent v1.0
├── 🔐 用户认证模块
├── 📥 论文管理模块
├── 🧠 知识图谱模块
├── 💬 智能问答模块
├── 👤 用户画像模块
├── 🔍 搜索与推荐模块
└── 📊 可视化模块
```

---

### 4.2 模块H: 用户认证模块

**负责人**: @后端开发H  
**优先级**: P0（基础功能）  
**预计工期**: 1周

#### 功能需求

##### H1: 用户注册 (REQ-H1)

**需求描述**:  
用户可以通过邮箱注册账号，系统需要验证邮箱唯一性并安全存储密码。

**API端点**: `POST /api/auth/register`

**请求参数**:
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "SecurePassword123!"
}
```

**处理流程**:
```
接收注册信息
  ↓
检查邮箱唯一性
  ↓
密码加密（bcrypt, cost=12）
  ↓
写入MySQL users表
  ↓
生成JWT Token
  ↓
返回用户信息和Token
```

**说明**：邮箱格式验证、密码强度验证由前端负责，后端只做业务逻辑验证。

**响应示例**:
```json
{
  "user": {
    "user_id": "u_1234567890",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**验收标准**:
- [ ] 邮箱唯一性验证
- [ ] 密码使用bcrypt加密（cost=12）
- [ ] 响应时间 < 1秒
- [ ] 错误提示清晰（邮箱已存在等）

**测试用例**:
```python
# TC-H1-001: 正常注册
def test_register_success():
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test1234!",
        "confirm_password": "Test1234!"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()

# TC-H1-002: 邮箱已存在
def test_register_duplicate_email():
    response = client.post("/api/auth/register", json={
        "email": "existing@example.com",
        ...
    })
    assert response.status_code == 400
    assert "email already exists" in response.json()["detail"]

```

---

##### H2: 用户登录 (REQ-H2)

**需求描述**:  
用户通过邮箱和密码登录，系统验证凭证并返回JWT Token。

**API端点**: `POST /api/auth/login`

**请求参数**:
```json
{
  "email": "zhangsan@example.com",
  "password": "SecurePassword123!"
}
```

**处理流程**:
```
接收登录凭证
  ↓
查询用户（by email）
  ↓
验证密码（bcrypt.verify）
  ↓
生成JWT Token
  - access_token (有效期: 1小时)
  - refresh_token (有效期: 7天)
  ↓
更新last_login时间
  ↓
返回Token和用户信息
```

**响应示例**:
```json
{
  "user": {
    "user_id": "u_1234567890",
    "username": "zhangsan",
    "email": "zhangsan@example.com"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**JWT Token内容**:
```json
{
  "sub": "u_1234567890",  // user_id
  "email": "zhangsan@example.com",
  "exp": 1704456789,  // 过期时间
  "iat": 1704453189   // 签发时间
}
```

**验收标准**:
- [ ] 正确验证用户凭证
- [ ] 生成有效的JWT Token
- [ ] 更新登录时间
- [ ] 响应时间 < 500ms
- [ ] 错误提示清晰（用户不存在、密码错误）
- [ ] 登录失败3次后锁定账户（5分钟）

---

##### H3: Token刷新 (REQ-H3)

**需求描述**:  
使用refresh_token获取新的access_token，避免用户频繁登录。

**API端点**: `POST /api/auth/refresh`

**请求参数**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**验收标准**:
- [ ] 验证refresh_token有效性
- [ ] 生成新的access_token
- [ ] 响应时间 < 200ms

---

##### H4: 用户登出 (REQ-H4)

**需求描述**:  
用户登出时，将Token加入黑名单（使用Redis）。

**API端点**: `POST /api/auth/logout`

**请求Header**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "message": "Successfully logged out"
}
```

**技术实现**:
```python
# 将Token加入Redis黑名单
redis_client.setex(
    f"blacklist:{token}",
    ttl=token_remaining_time,
    value="1"
)
```

**验收标准**:
- [ ] Token成功加入黑名单
- [ ] 黑名单Token无法访问受保护API
- [ ] Redis TTL设置正确

---

##### H5: 用户信息获取 (REQ-H5)

**需求描述**:  
获取当前登录用户的信息。

**API端点**: `GET /api/auth/me`

**请求Header**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "user_id": "u_1234567890",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-20T14:30:00Z"
}
```

**验收标准**:
- [ ] 正确解析JWT Token
- [ ] 返回完整用户信息
- [ ] 响应时间 < 200ms

---

##### H6: 密码修改 (REQ-H6)

**需求描述**:  
用户可以修改自己的密码。

**API端点**: `POST /api/auth/change-password`

**请求参数**:
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

**验收标准**:
- [ ] 验证旧密码正确
- [ ] 密码加密存储

**说明**：新密码强度验证、两次新密码一致性验证由前端负责。

---

##### H7: JWT中间件 (REQ-H7)

**需求描述**:  
实现JWT认证中间件，保护需要登录的API。

**技术实现**:
```python
# app/api/dependencies/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    JWT认证依赖
    验证Token并返回当前用户信息
    """
    token = credentials.credentials
    
    # 1. 检查Token是否在黑名单
    if redis_client.exists(f"blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    # 2. 验证Token
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # 3. 从数据库获取用户信息
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
```

**使用示例**:
```python
@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)  # 需要登录
):
    user_id = current_user["user_id"]
    # ... 业务逻辑
```

**验收标准**:
- [ ] 正确验证Token
- [ ] 处理过期Token
- [ ] 处理黑名单Token
- [ ] 处理无效Token
- [ ] 性能影响 < 50ms

---

### 4.3 模块A: 论文管理模块

**负责人**: @后端开发A  
**优先级**: P0（核心功能）  
**预计工期**: 2周  
**依赖**: Module H（用户认证）

#### 功能需求

##### A1: 论文上传 (REQ-A1)

**需求描述**:  
用户可以上传PDF格式的学术论文，系统自动解析论文内容并构建知识图谱。

**输入**:
- PDF文件（< 50MB）
- 用户ID
- 可选：论文元数据（标题、作者等）

**处理流程**:
```
PDF上传
  ↓
文件存储（temp/uploads/）
  ↓
异步任务队列（Celery）
  ↓
PDF解析（PyMuPDF）
  ├─ 提取文本
  ├─ 提取元数据
  └─ 识别章节结构
  ↓
文本分块（按section）
  ↓
调用Graphiti.add_episode API
  ├─ 自动LLM实体抽取（Paper、Method、Dataset、Task等）
  ├─ 自动关系抽取（PROPOSES、EVALUATES_ON等）
  └─ 写入图谱（用户图谱 user:xxx 或全局图谱 global）
  ↓
返回解析结果
```

**输出**:
```json
{
  "paper_id": "uuid-xxx",
  "status": "completed",
  "entities_count": 25,
  "relations_count": 18,
  "summary": "本文提出了...",
  "key_methods": ["SwinV3", "TokenMixing"],
  "datasets": ["ImageNet", "COCO"],
  "processing_time": 45.2
}
```

**技术规格**:
- API端点: `POST /api/papers/upload`
- 依赖服务: `IngestService`, `PDFParser`
- 异步任务: `ingest_pdf_task`
- Graphiti方法: `graphiti.add_episode()`（内部调用LLM进行实体抽取）
- 超时设置: 5分钟

**验收标准**:
- [ ] 支持PDF上传（< 50MB）
- [ ] 解析准确率 > 80%（人工抽样10篇）
- [ ] 实体抽取覆盖率 > 85%
- [ ] 处理时间 < 2分钟（标准论文）
- [ ] 异步任务可监控状态
- [ ] 错误处理完善（格式错误、解析失败等）

**测试用例**:
```python
# TC-A1-001: 正常上传
def test_upload_valid_pdf():
    response = client.post("/api/papers/upload", 
                           files={"file": valid_pdf})
    assert response.status_code == 200
    assert "paper_id" in response.json()

# TC-A1-002: 文件过大
def test_upload_large_pdf():
    response = client.post("/api/papers/upload",
                           files={"file": large_pdf})
    assert response.status_code == 413

# TC-A1-003: 格式错误
def test_upload_invalid_format():
    response = client.post("/api/papers/upload",
                           files={"file": txt_file})
    assert response.status_code == 400
```

---

##### A2: 论文详情 (REQ-A2)

**需求描述**:  
获取论文的完整结构化信息，包括方法、数据集、结果等。

**需求描述**:  
获取论文的完整结构化信息，包括方法、数据集、结果等。

**API端点**: `GET /api/papers/{paper_id}`

**响应示例**:
```json
{
  "paper_id": "uuid-1",
  "title": "Swin Transformer V3",
  "authors": [...],
  "abstract": "...",
  "sections": [
    {"title": "Introduction", "content": "..."},
    {"title": "Method", "content": "..."}
  ],
  "entities": {
    "methods": ["SwinV3", "TokenMixing"],
    "datasets": ["ImageNet", "COCO"],
    "tasks": ["Image Classification"]
  },
  "relations": [
    {"type": "PROPOSES", "target": "SwinV3"},
    {"type": "EVALUATES_ON", "target": "ImageNet"}
  ],
  "citations_count": 125,
  "related_papers": [...]
}
```

**验收标准**:
- [ ] 返回完整论文信息
- [ ] 包含实体和关系
- [ ] 包含相关论文推荐
- [ ] 响应时间 < 500ms

---

### 4.3 模块B: 知识图谱模块

**负责人**: @后端开发B  
**优先级**: P0（核心功能）  
**预计工期**: 3周

#### 功能需求

##### B1: 图谱搜索 (REQ-B1)

**需求描述**:  
提供混合搜索（语义 + BM25）和节点距离重排功能，支持双图谱架构。

**API端点**: `POST /api/graph/search`

**请求参数**:
```json
{
  "query": "attention mechanism in transformers",
  "user_id": "user123",
  "search_scope": "auto",  // auto | user | global
  "rerank_mode": "rrf",    // rrf | mmr | cross_encoder
  "focal_node_uuid": null,  // 可选：中心节点
  "limit": 20
}
```

**处理逻辑**:
```python
# 双图谱Fallback机制
def search_with_fallback(query, user_id):
    # 1. 搜索用户图谱
    user_results = graphiti.search(query, group_id=f"user:{user_id}")
    
    # 2. 如果结果不足，搜索全局图谱
    if len(user_results) < threshold:
        global_results = graphiti.search(query, group_id="global")
        results = merge_results(user_results, global_results)
    
    # 3. 如果仍不足，触发外部搜索
    if len(results) < threshold:
        trigger_external_search(query, user_id)
    
    return results
```

**响应示例**:
```json
{
  "results": [
    {
      "node_id": "uuid-1",
      "node_type": "Method",
      "name": "Self-Attention",
      "summary": "...",
      "relevance_score": 0.95,
      "source": "user_graph"
    }
  ],
  "search_strategy": "user_then_global",
  "external_search_triggered": false,
  "total": 18
}
```

**技术规格**:
- 依赖: `GraphService`, `NamespaceService`, `GraphitiClient`
- Graphiti方法: `graphiti.search()`, `graphiti._search()`
- 搜索配置: 使用`SearchConfig`自定义参数

**验收标准**:
- [ ] 混合搜索正确实现
- [ ] 双图谱Fallback正确
- [ ] 支持3种重排模式
- [ ] 搜索响应时间 < 2秒
- [ ] 搜索结果相关性 > 70%（人工评估）

---

##### B2: 节点查询 (REQ-B2)

**需求描述**:  
通过UUID获取节点详情，包括邻居节点。

**API端点**: `GET /api/graph/node/{uuid}`

**响应示例**:
```json
{
  "node": {
    "uuid": "uuid-1",
    "type": "Method",
    "name": "Vision Transformer",
    "properties": {...},
    "summary": "...",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "neighbors": [
    {
      "uuid": "uuid-2",
      "type": "Paper",
      "name": "An Image is Worth 16x16 Words",
      "relation": "PROPOSED_BY",
      "distance": 1
    }
  ],
  "communities": ["Computer Vision", "Transformers"]
}
```

**验收标准**:
- [ ] 正确返回节点信息
- [ ] 包含1-hop邻居
- [ ] 包含社区信息
- [ ] 响应时间 < 500ms

---

##### B3: 路径查询 (REQ-B3)

**需求描述**:  
查找两个节点之间的关系路径。

**API端点**: `POST /api/graph/path`

**请求参数**:
```json
{
  "source_uuid": "uuid-1",
  "target_uuid": "uuid-2",
  "max_depth": 3
}
```

**响应示例**:
```json
{
  "paths": [
    {
      "length": 2,
      "nodes": [
        {"uuid": "uuid-1", "name": "ViT"},
        {"uuid": "uuid-3", "name": "BERT"},
        {"uuid": "uuid-2", "name": "Transformer"}
      ],
      "relations": ["IMPROVES_OVER", "BASED_ON"]
    }
  ]
}
```

**验收标准**:
- [ ] 找到最短路径
- [ ] 支持多条路径返回
- [ ] 最大深度限制生效
- [ ] 超时保护（5秒）

---

##### B4: Schema定义 (REQ-B4)

**需求描述**:  
定义8种实体类型和9种关系类型，使用Pydantic验证。

**实体类型**:
```python
# app/schemas/entities.py

class PaperEntity(BaseModel):
    title: str
    arxiv_id: Optional[str]
    doi: Optional[str]
    abstract: str
    year: int
    venue: Optional[str]
    authors: List[str]

class MethodEntity(BaseModel):
    name: str
    description: str
    category: Optional[str]

class DatasetEntity(BaseModel):
    name: str
    description: Optional[str]
    domain: Optional[str]

# ... 其他5种实体
```

**关系类型**:
```python
# app/schemas/relations.py

class RelationType(str, Enum):
    PROPOSES = "PROPOSES"
    EVALUATES_ON = "EVALUATES_ON"
    SOLVES = "SOLVES"
    IMPROVES_OVER = "IMPROVES_OVER"
    CITES = "CITES"
    USES_METRIC = "USES_METRIC"
    AUTHORED_BY = "AUTHORED_BY"
    AFFILIATED_WITH = "AFFILIATED_WITH"
    HAS_CONCEPT = "HAS_CONCEPT"
```

**验收标准**:
- [ ] 8种实体类型完整定义
- [ ] 9种关系类型完整定义
- [ ] Pydantic验证通过
- [ ] 单元测试覆盖率 > 90%

---

### 4.4 模块C: 智能问答模块

**负责人**: @后端开发C  
**优先级**: P0（核心功能）  
**预计工期**: 3周

#### 功能需求

##### C1: Agent对话 (REQ-C1)

**需求描述**:  
用户可以向Agent提问，Agent自动调用工具、聚合上下文、生成回答。

**API端点**: `POST /api/chat`

**请求参数**:
```json
{
  "user_id": "user123",
  "message": "最近视觉Transformer有哪些改进？",
  "session_id": "session-456",
  "context": []  // 可选：历史上下文
}
```

**Agent工作流程**:
```
接收用户消息
  ↓
【意图理解】
  LLM分析：需要搜索ViT相关论文
  ↓
【工具选择】
  选中工具：
    - graph_query_tool
    - external_search_tool
  ↓
【工具执行】
  graph_query_tool.execute("vision transformer", user_id)
    → 返回20个结果
  
  判断：结果充足？
    No → external_search_tool.execute("ViT improvements 2024")
           → arXiv搜索 → 自动摄入5篇新论文
  ↓
【上下文聚合】
  - 图谱搜索结果
  - 用户阅读历史
  - 用户兴趣标签
  ↓
【回答生成】
  LLM生成结构化回答 + 引用来源
  ↓
【后处理】
  - 保存聊天历史
  - 更新用户画像
  ↓
返回回答
```

**响应示例**:
```json
{
  "reply": "近两年视觉Transformer的主要改进包括：\n\n1. **结构优化**：Swin Transformer V3引入了Token-Mixing Normalization...\n\n2. **训练效率**：DeiT III通过...\n\n3. **应用扩展**：MedViT将ViT应用于医学影像...",
  "citations": [
    {
      "text": "Token-Mixing Normalization",
      "source_type": "paper",
      "source_id": "uuid-1",
      "source_name": "Swin Transformer V3"
    }
  ],
  "tools_used": ["graph_query", "external_search"],
  "graph_results_count": 20,
  "external_papers_added": 5,
  "confidence": 0.87,
  "session_id": "session-456"
}
```

**技术规格**:
- 依赖: `AgentService`, `ToolRegistry`, `LLMClient`
- LLM模型: GPT-4 (gpt-4-turbo)
- 工具调用: Function Calling API
- 上下文窗口: 16K tokens

**验收标准**:
- [ ] Agent能理解用户意图
- [ ] 正确选择和调用工具
- [ ] 回答包含引用来源
- [ ] 回答质量 > 4/5（人工评分）
- [ ] 响应时间 < 10秒
- [ ] 错误处理完善

**测试用例**:
```python
# TC-C1-001: 基础问答
def test_basic_chat():
    response = client.post("/api/chat", json={
        "user_id": "test_user",
        "message": "什么是Vision Transformer？"
    })
    assert response.status_code == 200
    assert "reply" in response.json()
    assert len(response.json()["citations"]) > 0

# TC-C1-002: 触发外部搜索
def test_external_search_trigger():
    response = client.post("/api/chat", json={
        "user_id": "test_user",
        "message": "2024年最新的ViT论文有哪些？"
    })
    result = response.json()
    assert "external_search" in result["tools_used"]

# TC-C1-003: 长对话
def test_multi_turn_chat():
    # 第一轮
    r1 = client.post("/api/chat", json={
        "user_id": "test_user",
        "message": "什么是Swin Transformer？"
    })
    session_id = r1.json()["session_id"]
    
    # 第二轮（上下文延续）
    r2 = client.post("/api/chat", json={
        "user_id": "test_user",
        "message": "它和ViT有什么区别？",
        "session_id": session_id
    })
    assert "Swin" in r2.json()["reply"]
```

---

##### C2: Agent工具系统 (REQ-C2)

**需求描述**:  
实现6个核心工具，支持工具注册和调用。

**工具清单**:

1. **GraphQueryTool** - 图谱查询
   ```python
   class GraphQueryTool(BaseTool):
       name = "graph_query"
       description = "在知识图谱中搜索相关学术信息"
       
       async def execute(self, input_data):
           # 实现图谱搜索
           pass
   ```

2. **ExternalSearchTool** - 外部搜索
   ```python
   class ExternalSearchTool(BaseTool):
       name = "external_search"
       description = "在arXiv和Semantic Scholar搜索最新论文"
       
       async def execute(self, input_data):
           # 调用arXiv API
           # 自动下载和摄入
           pass
   ```

3. **PDFParseTool** - PDF解析
4. **PaperCompareTool** - 论文对比
5. **CommunityQueryTool** - 社区查询
6. **UserProfileTool** - 用户画像查询

**工具注册器**:
```python
# app/tools/tool_registry.py
tool_registry = ToolRegistry()
tool_registry.register(GraphQueryTool())
tool_registry.register(ExternalSearchTool())
# ...
```

**验收标准**:
- [ ] 6个工具全部实现
- [ ] 工具注册机制正常
- [ ] 每个工具有单元测试
- [ ] 工具文档完整

---

##### C3: 对话历史 (REQ-C3)

**需求描述**:  
保存和查询用户的聊天历史。

**API端点**: `GET /api/history/chat/{user_id}`

**响应示例**:
```json
{
  "history": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "user_message": "什么是Vision Transformer？",
      "agent_reply": "Vision Transformer是...",
      "tools_used": ["graph_query"],
      "satisfaction": 5
    }
  ],
  "total": 45
}
```

**验收标准**:
- [ ] 正确保存聊天记录
- [ ] 支持分页查询
- [ ] 支持按时间筛选
- [ ] 响应时间 < 500ms

---

### 4.5 模块D: 用户画像模块（已删除）

**说明**：为简化MVP开发，用户画像和阅读历史功能延后到v2.0版本实现。

---

### 4.6 模块E: 搜索与推荐模块

**负责人**: @后端开发E  
**优先级**: P1（重要功能）  
**预计工期**: 2周

#### 功能需求

##### E1: 外部搜索集成 (REQ-E1)

**需求描述**:  
集成arXiv和Semantic Scholar API，支持外部论文搜索。

**arXiv集成**:
```python
# app/integrations/arxiv_client.py

class ArxivClient:
    async def search(self, query: str, max_results: int = 10):
        """搜索arXiv论文"""
        papers = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        return [self._parse_paper(p) for p in papers.results()]
    
    async def download_pdf(self, arxiv_id: str):
        """下载PDF"""
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        # 下载逻辑
```

**自动摄入机制**:
```python
async def search_and_ingest(query, user_id):
    # 1. 搜索arXiv
    papers = await arxiv_client.search(query)
    
    # 2. 自动下载PDF
    for paper in papers[:5]:  # 限制数量
        pdf = await arxiv_client.download_pdf(paper.arxiv_id)
        
        # 3. 自动摄入图谱
        await ingest_service.ingest_pdf(
            pdf, 
            metadata=paper,
            group_id="global"  # 写入全局图谱
        )
```

**API端点**: `POST /api/search/external`

**请求参数**:
```json
{
  "query": "vision transformer 2024",
  "source": "arxiv",  // arxiv | semantic_scholar
  "max_results": 10,
  "auto_ingest": true
}
```

**响应示例**:
```json
{
  "papers": [
    {
      "arxiv_id": "2401.12345",
      "title": "...",
      "authors": [...],
      "abstract": "...",
      "pdf_url": "...",
      "ingested": true
    }
  ],
  "total_found": 156,
  "ingested_count": 5
}
```

**验收标准**:
- [ ] arXiv API集成正常
- [ ] Semantic Scholar API集成正常
- [ ] 自动摄入机制正确
- [ ] 搜索响应时间 < 5秒
- [ ] 错误处理（API限流、网络错误）

---

##### E2: 论文推荐（已删除）

**说明**：为简化MVP开发，论文推荐功能延后到v2.0版本实现。

---

##### E3: 论文对比（已删除）

**说明**：为简化MVP开发，论文对比功能延后到v2.0版本实现。

---

### 4.7 模块F: 社区管理模块

**负责人**: @后端开发F  
**优先级**: P2（增强功能）  
**预计工期**: 1.5周

#### 功能需求

##### F1: 社区检测 (REQ-F1)

**需求描述**:  
使用Graphiti的`build_communities`功能检测研究社区。

**API端点**: `POST /api/communities/detect`

**请求参数**:
```json
{
  "group_id": "global",  // or "user:123"
  "update_existing": true
}
```

**技术实现**:
```python
async def detect_communities(group_id):
    await graphiti.build_communities(
        group_id=group_id,
        update_communities=True
    )
```

**验收标准**:
- [ ] 正确调用Graphiti API
- [ ] 支持用户和全局图谱
- [ ] 异步任务执行
- [ ] 进度可监控

---

##### F2: 社区查询 (REQ-F2)

**需求描述**:  
查询图谱中的研究社区。

**API端点**: `GET /api/communities`

**响应示例**:
```json
{
  "communities": [
    {
      "community_id": "comm-1",
      "name": "Vision Transformers",
      "summary": "研究视觉Transformer架构的社区",
      "node_count": 156,
      "key_papers": ["ViT", "Swin", "DeiT"],
      "key_methods": ["Self-Attention", "Patch Embedding"]
    }
  ]
}
```

**验收标准**:
- [ ] 正确获取社区列表
- [ ] 包含社区摘要
- [ ] 响应时间 < 1秒

---

### 4.8 模块G: 图谱可视化模块

**负责人**: @后端开发G  
**优先级**: P1（重要功能）  
**预计工期**: 1.5周

**使用场景**:  
用户在前端图谱可视化页面可以：
- 查看自己的个人知识图谱（节点和边的可视化）
- 交互式探索：点击节点查看详细属性
- 交互式探索：点击边查看关系属性
- 筛选和过滤：按实体类型、关系类型筛选
- 局部探索：展开某个节点的邻居节点

#### 功能需求

##### G1: 用户图谱数据获取 (REQ-G1)

**需求描述**:  
获取用户个人知识图谱的节点和边数据，供前端可视化渲染。支持分页、筛选、局部查询。

**API端点**: `GET /api/graph/visualization/my-graph`

**请求Header**:
```
Authorization: Bearer <access_token>
```

**请求参数**:
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| node_types | string[] | 否 | all | 筛选节点类型，如 `["Paper", "Method"]` |
| relation_types | string[] | 否 | all | 筛选关系类型，如 `["PROPOSES", "CITES"]` |
| limit | int | 否 | 500 | 最大返回节点数（防止大图卡顿） |
| center_node_uuid | string | 否 | null | 中心节点UUID（返回其邻居） |
| max_hops | int | 否 | 2 | 从中心节点的最大跳数（1-3） |
| include_properties | bool | 否 | false | 是否包含节点/边的详细属性 |

**响应示例**:
```json
{
  "user_id": "user123",
  "graph_data": {
    "nodes": [
      {
        "id": "uuid-1",
        "type": "Paper",
        "name": "Vision Transformer",
        "label": "Vision Transformer",
        "summary": "A paper about ViT...",
        "created_at": "2024-01-15T10:30:00Z",
        "size": 10,
        "color": "#4A90E2"
      },
      {
        "id": "uuid-2",
        "type": "Method",
        "name": "Self-Attention",
        "label": "Self-Attention",
        "summary": "Attention mechanism...",
        "created_at": "2024-01-15T10:35:00Z",
        "size": 8,
        "color": "#E94B3C"
      }
    ],
    "edges": [
      {
        "id": "edge-1",
        "source": "uuid-1",
        "target": "uuid-2",
        "type": "PROPOSES",
        "label": "PROPOSES",
        "created_at": "2024-01-15T10:35:00Z",
        "strength": 0.9
      }
    ]
  },
  "metadata": {
    "total_nodes_in_graph": 1523,
    "returned_nodes": 500,
    "total_edges_in_graph": 3456,
    "returned_edges": 892,
    "has_more": true,
    "generated_at": "2024-01-15T14:30:00Z"
  },
  "node_type_stats": {
    "Paper": 350,
    "Method": 100,
    "Dataset": 30,
    "Task": 20
  }
}
```

**权限控制**:
- ✅ 用户只能查看自己的个人图谱（group_id = "user:{user_id}"）
- ✅ JWT Token认证必需
- ❌ 不允许查看其他用户的图谱

**处理逻辑**:
```python
async def get_my_graph(user_id, filters):
    # 1. 从Graphiti获取用户图谱数据
    group_id = f"user:{user_id}"
    
    # 2. 如果指定了center_node，获取局部图谱
    if filters.center_node_uuid:
        graph_data = await graphiti.get_node_neighbors(
            node_uuid=filters.center_node_uuid,
            max_hops=filters.max_hops,
            group_id=group_id
        )
    else:
        # 获取全图（带限制）
        graph_data = await graphiti.get_graph(
            group_id=group_id,
            limit=filters.limit
        )
    
    # 3. 应用筛选
    filtered_data = apply_filters(graph_data, filters)
    
    # 4. 转换为前端格式
    return format_for_visualization(filtered_data)
```

**验收标准**:
- [ ] 支持JWT认证
- [ ] 用户只能查看自己的图谱
- [ ] 支持按节点类型筛选
- [ ] 支持按关系类型筛选
- [ ] 支持局部图谱查询（center_node + max_hops）
- [ ] 大图谱（>5000节点）响应时间 < 5秒
- [ ] 返回数据格式适配前端可视化库（如 ECharts、D3.js、Cytoscape.js）
- [ ] 错误处理完善（图谱为空、节点不存在等）

**测试用例**:
```python
# TC-G1-001: 获取完整图谱
def test_get_full_graph():
    response = client.get("/api/graph/visualization/my-graph", 
                         headers=auth_headers)
    assert response.status_code == 200
    assert "nodes" in response.json()["graph_data"]
    assert "edges" in response.json()["graph_data"]

# TC-G1-002: 筛选特定类型
def test_filter_by_node_type():
    response = client.get("/api/graph/visualization/my-graph?node_types=Paper,Method",
                         headers=auth_headers)
    nodes = response.json()["graph_data"]["nodes"]
    assert all(n["type"] in ["Paper", "Method"] for n in nodes)

# TC-G1-003: 局部图谱查询
def test_get_local_graph():
    response = client.get(
        "/api/graph/visualization/my-graph?center_node_uuid=uuid-1&max_hops=2",
        headers=auth_headers
    )
    assert response.status_code == 200
```

---

##### G2: 节点详情查询 (REQ-G2)

**需求描述**:  
用户点击图谱中的节点时，获取该节点的完整属性信息。

**API端点**: `GET /api/graph/nodes/{node_uuid}`

**请求Header**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "node": {
    "uuid": "uuid-1",
    "type": "Paper",
    "name": "Vision Transformer",
    "properties": {
      "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
      "authors": ["Alexey Dosovitskiy", "Lucas Beyer", "..."],
      "abstract": "While the Transformer architecture has become...",
      "year": 2021,
      "venue": "ICLR",
      "arxiv_id": "2010.11929",
      "doi": "10.48550/arXiv.2010.11929",
      "citations_count": 15000,
      "keywords": ["Vision Transformer", "Self-Attention", "Image Classification"]
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:20:00Z",
    "group_id": "user:user123"
  },
  "neighbors": {
    "incoming": [
      {
        "uuid": "uuid-5",
        "type": "Paper",
        "name": "DeiT",
        "relation": "CITES",
        "relation_created_at": "2024-01-15T10:35:00Z"
      }
    ],
    "outgoing": [
      {
        "uuid": "uuid-2",
        "type": "Method",
        "name": "Self-Attention",
        "relation": "PROPOSES",
        "relation_created_at": "2024-01-15T10:35:00Z"
      },
      {
        "uuid": "uuid-3",
        "type": "Dataset",
        "name": "ImageNet",
        "relation": "EVALUATES_ON",
        "relation_created_at": "2024-01-15T10:36:00Z"
      }
    ]
  },
  "statistics": {
    "total_neighbors": 15,
    "incoming_edges": 8,
    "outgoing_edges": 7
  }
}
```

**权限控制**:
- ✅ 用户只能查看自己图谱中的节点
- ✅ JWT Token认证必需
- ❌ 如果节点不属于用户图谱，返回404

**验收标准**:
- [ ] 正确返回节点的所有属性
- [ ] 包含邻居节点列表（incoming/outgoing）
- [ ] 权限验证正确
- [ ] 响应时间 < 500ms
- [ ] 节点不存在时返回404
- [ ] 无权限访问时返回403

---

##### G3: 边详情查询 (REQ-G3)

**需求描述**:  
用户点击图谱中的边时，获取该关系的完整属性信息。

**API端点**: `GET /api/graph/edges/{edge_uuid}`

或者使用：`GET /api/graph/edges?source={source_uuid}&target={target_uuid}&type={relation_type}`

**请求Header**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "edge": {
    "uuid": "edge-uuid-1",
    "type": "PROPOSES",
    "source_node": {
      "uuid": "uuid-1",
      "type": "Paper",
      "name": "Vision Transformer"
    },
    "target_node": {
      "uuid": "uuid-2",
      "type": "Method",
      "name": "Self-Attention"
    },
    "properties": {
      "confidence": 0.95,
      "source_text": "We propose a pure transformer architecture...",
      "extracted_from": "Method section, paragraph 2",
      "fact": "The Vision Transformer paper proposes the Self-Attention mechanism for image recognition."
    },
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:00Z",
    "group_id": "user:user123"
  },
  "context": {
    "related_papers": ["uuid-5", "uuid-6"],
    "co_occurrence_count": 3
  }
}
```

**权限控制**:
- ✅ 用户只能查看自己图谱中的边
- ✅ JWT Token认证必需
- ❌ 如果边不属于用户图谱，返回404

**验收标准**:
- [ ] 正确返回边的所有属性
- [ ] 包含源节点和目标节点信息
- [ ] 权限验证正确
- [ ] 响应时间 < 300ms
- [ ] 边不存在时返回404
- [ ] 无权限访问时返回403

---

##### G4: 图谱统计概览 (REQ-G4)

**需求描述**:  
获取用户图谱的统计信息，在可视化页面顶部显示。

**API端点**: `GET /api/graph/visualization/stats`

**请求Header**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "user_id": "user123",
  "statistics": {
    "total_nodes": 1523,
    "total_edges": 3456,
    "node_types": {
      "Paper": 850,
      "Method": 350,
      "Dataset": 150,
      "Task": 80,
      "Metric": 50,
      "Author": 30,
      "Institution": 10,
      "Concept": 3
    },
    "relation_types": {
      "PROPOSES": 850,
      "EVALUATES_ON": 650,
      "CITES": 1200,
      "SOLVES": 300,
      "IMPROVES_OVER": 200,
      "USES_METRIC": 150,
      "AUTHORED_BY": 80,
      "AFFILIATED_WITH": 20,
      "HAS_CONCEPT": 6
    },
    "last_updated": "2024-01-20T14:30:00Z",
    "graph_created_at": "2024-01-01T08:00:00Z",
    "top_nodes": [
      {
        "uuid": "uuid-1",
        "name": "Vision Transformer",
        "type": "Paper",
        "degree": 25
      },
      {
        "uuid": "uuid-2",
        "name": "Self-Attention",
        "type": "Method",
        "degree": 18
      }
    ]
  }
}
```

**验收标准**:
- [ ] 正确统计节点和边的数量
- [ ] 按类型分类统计
- [ ] 包含图谱更新时间
- [ ] 响应时间 < 1秒
- [ ] 支持缓存（更新频率：5分钟）

---

##### G5: 节点邻居展开 (REQ-G5)

**需求描述**:  
在图谱可视化页面中，用户双击某个节点，展开其未显示的邻居节点。

**API端点**: `GET /api/graph/nodes/{node_uuid}/neighbors`

**请求Header**:
```
Authorization: Bearer <access_token>
```

**请求参数**:
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| direction | string | 否 | both | incoming / outgoing / both |
| node_types | string[] | 否 | all | 筛选邻居节点类型 |
| relation_types | string[] | 否 | all | 筛选关系类型 |
| limit | int | 否 | 50 | 最大返回邻居数 |

**响应示例**:
```json
{
  "center_node_uuid": "uuid-1",
  "neighbors": {
    "nodes": [
      {
        "id": "uuid-10",
        "type": "Paper",
        "name": "DeiT",
        "label": "DeiT",
        "summary": "Data-efficient image transformers...",
        "size": 8,
        "color": "#4A90E2"
      },
      {
        "id": "uuid-11",
        "type": "Method",
        "name": "Knowledge Distillation",
        "label": "Knowledge Distillation",
        "summary": "...",
        "size": 6,
        "color": "#E94B3C"
      }
    ],
    "edges": [
      {
        "id": "edge-10",
        "source": "uuid-10",
        "target": "uuid-1",
        "type": "CITES",
        "label": "CITES",
        "strength": 0.8
      },
      {
        "id": "edge-11",
        "source": "uuid-1",
        "target": "uuid-11",
        "type": "PROPOSES",
        "label": "PROPOSES",
        "strength": 0.9
      }
    ]
  },
  "metadata": {
    "total_neighbors": 25,
    "returned_neighbors": 10,
    "has_more": true
  }
}
```

**前端使用场景**:
```javascript
// 用户双击节点时
async function onNodeDoubleClick(nodeId) {
  const response = await fetch(`/api/graph/nodes/${nodeId}/neighbors?limit=20`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  
  // 将新节点和边添加到现有图谱
  graph.addNodes(data.neighbors.nodes);
  graph.addEdges(data.neighbors.edges);
}
```

**验收标准**:
- [ ] 正确返回邻居节点和连接边
- [ ] 支持方向筛选（incoming/outgoing/both）
- [ ] 支持类型筛选
- [ ] 支持分页
- [ ] 响应时间 < 1秒
- [ ] 不返回已存在于前端的节点（可选优化）

---

## 5. 数据需求

### 5.1 数据需求总览

数据是AI科研助手系统的核心资产，包括：
- **种子数据**：系统初始化所需的基础数据
- **运行时数据**：系统运行过程中产生的数据
- **测试数据**：开发和测试环境使用的数据

| 数据类型 | 数量级 | 来源 | 优先级 |
|---------|--------|------|--------|
| 种子论文 | 1000+ | arXiv/公开数据集 | P0 |
| 实体Schema | 8种 | 手动定义 | P0 |
| 关系Schema | 9种 | 手动定义 | P0 |
| 测试论文PDF | 50+ | 手动收集 | P0 |
| 用户测试数据 | 10+ | 模拟生成 | P1 |
| 标注数据 | 100+ | 人工标注 | P1 |

---

### 5.2 初始数据需求（种子数据）

#### REQ-D1: 种子论文库

**需求描述**:  
系统上线前需要预先构建基础知识图谱，包含1000+篇学术论文。

**数据来源**:
```
1. arXiv公开数据集
   - 领域：Computer Vision, NLP, Machine Learning
   - 时间范围：2020-2024
   - 数量：~500篇

2. 经典论文集
   - 高引用论文（> 500 citations）
   - 领域奠基性论文
   - 数量：~300篇

3. 最新会议论文
   - CVPR/ICCV/NeurIPS/ICML 2023-2024
   - 数量：~200篇
```

**数据格式**:
```json
{
  "paper_id": "arxiv-2301.12345",
  "title": "Vision Transformer for Dense Prediction",
  "authors": ["Author1", "Author2"],
  "abstract": "...",
  "year": 2023,
  "venue": "CVPR",
  "arxiv_id": "2301.12345",
  "doi": "10.1109/CVPR52729.2023.00001",
  "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
  "categories": ["cs.CV", "cs.AI"]
}
```

**数据质量要求**:
- [ ] PDF可正常解析（无扫描版）
- [ ] 元数据完整（至少包含标题、作者、年份）
- [ ] 论文语言为英文
- [ ] 文件大小 < 50MB
- [ ] 无损坏或缺失页

**验收标准**:
- [ ] 种子论文 ≥ 1000篇
- [ ] 覆盖3个以上主要AI领域
- [ ] PDF解析成功率 > 95%
- [ ] 实体抽取覆盖率 > 80%

---

#### REQ-D2: 实体和关系Schema

**需求描述**:  
定义清晰的实体类型和关系类型Schema。

**实体Schema（8种）**:

```python
# 1. Paper实体
class PaperEntity:
    required: [title, abstract, year]
    optional: [arxiv_id, doi, venue, authors, keywords, citations_count]
    
# 2. Method实体
class MethodEntity:
    required: [name, description]
    optional: [category, complexity, performance_metrics]

# 3. Dataset实体
class DatasetEntity:
    required: [name]
    optional: [description, domain, size, format, url]

# 4. Task实体
class TaskEntity:
    required: [name]
    optional: [description, category, benchmark_metric]

# 5. Metric实体
class MetricEntity:
    required: [name]
    optional: [description, formula, range, unit]

# 6. Author实体
class AuthorEntity:
    required: [name]
    optional: [affiliation, h_index, research_interests, homepage]

# 7. Institution实体
class InstitutionEntity:
    required: [name]
    optional: [country, type, ranking, website]

# 8. Concept实体
class ConceptEntity:
    required: [name]
    optional: [description, category, related_concepts]
```

**关系Schema（9种）**:

| 关系类型 | 源节点 | 目标节点 | 必需属性 | 可选属性 |
|---------|--------|---------|---------|---------|
| PROPOSES | Paper | Method | - | year, confidence |
| EVALUATES_ON | Paper | Dataset | - | metric, result_value |
| SOLVES | Method | Task | - | performance |
| IMPROVES_OVER | Method | Method | - | improvement_rate |
| CITES | Paper | Paper | - | citation_context |
| USES_METRIC | Paper | Metric | - | result_value |
| AUTHORED_BY | Paper | Author | - | author_order |
| AFFILIATED_WITH | Author | Institution | - | position, start_date |
| HAS_CONCEPT | Paper | Concept | - | relevance_score |

**验收标准**:
- [ ] Schema文档完整
- [ ] Pydantic模型定义完成
- [ ] Schema验证测试通过
- [ ] 与Graphiti兼容性验证

---

#### REQ-D3: 测试数据集

**需求描述**:  
准备高质量的测试数据用于开发和QA。

**测试PDF集合**:
```
1. 标准论文（30篇）
   - 结构完整（含Abstract、Method、Experiments等）
   - 格式规范（双栏、单栏各半）
   - 页数适中（8-15页）

2. 边界案例（10篇）
   - 超长论文（> 30页）
   - 超短论文（< 5页）
   - 特殊格式（预印本、workshop等）

3. 异常案例（10篇）
   - 含大量公式的论文
   - 含大量图表的论文
   - 多语言混合论文
```

**测试用户数据**:
```json
{
  "test_users": [
    {
      "user_id": "test_user_001",
      "profile": {
        "research_direction": "Computer Vision",
        "reading_history": ["paper_001", "paper_002", ...],
        "interests": ["Vision Transformer", "Object Detection"]
      }
    },
    // ... 10个测试用户
  ]
}
```

**标注数据（用于验证）**:
```
100篇论文的人工标注数据：
- 实体标注：方法、数据集、任务
- 关系标注：PROPOSES、EVALUATES_ON等
- 摘要标注：论文核心内容
- 用途：验证实体抽取准确率
```

**验收标准**:
- [ ] 测试PDF ≥ 50篇
- [ ] 标注数据 ≥ 100篇
- [ ] 测试用户 ≥ 10个
- [ ] 标注一致性 > 90%

---

### 5.3 运行时数据需求

#### REQ-D4: 用户数据

**用户基础数据**:
```sql
-- 用户表
user_id: VARCHAR(50) PRIMARY KEY
username: VARCHAR(100)
email: VARCHAR(100) UNIQUE
password_hash: VARCHAR(255)
created_at: TIMESTAMP
last_login: TIMESTAMP
```

**用户行为数据**:
```
1. 聊天历史
   - 存储时长：永久
   - 预估量：10万条/月
   - 增长速率：线性

2. 阅读历史
   - 存储时长：永久
   - 预估量：5万条/月
   - 增长速率：线性

3. 上传论文记录
   - 存储时长：永久
   - 预估量：1万篇/月
   - 增长速率：指数增长
```

**数据保留策略**:
```
- 用户画像：永久保留
- 聊天历史：永久保留
- 临时文件（PDF上传）：7天后清理
- 日志文件：保留90天
- 备份数据：保留180天
```

---

#### REQ-D5: 图谱数据

**Neo4j图数据库**:

**节点数据规模预估**:
```
初期（Month 1）：
- Paper节点：1,000
- Method节点：500
- Dataset节点：200
- Task节点：100
- 其他节点：200
- 总计：~2,000节点

增长期（Month 6）：
- Paper节点：10,000
- Method节点：5,000
- Dataset节点：1,000
- Task节点：500
- 其他节点：1,500
- 总计：~18,000节点

稳定期（Year 1）：
- Paper节点：50,000
- Method节点：20,000
- Dataset节点：5,000
- Task节点：2,000
- 其他节点：8,000
- 总计：~85,000节点
```

**关系数据规模预估**:
```
关系/节点比例：约3:1
Year 1 预估：~250,000条关系
```

**存储需求**:
```
每个Paper节点：~5KB（含属性和embedding）
每个关系：~1KB
Year 1 存储需求：
  - 节点：85,000 × 5KB = 425MB
  - 关系：250,000 × 1KB = 250MB
  - 索引和缓存：~2GB
  - 总计：~3GB
```

**备份策略**:
```
- 全量备份：每周日凌晨
- 增量备份：每日凌晨
- 备份保留：最近4周的全量 + 最近7天的增量
- 异地备份：每月全量备份
```

---

#### REQ-D6: 关系数据库数据

**MySQL数据规模预估**:

```sql
-- 用户表
users: ~1,000行/年

-- 聊天历史表
chat_history: ~120,000行/年
  (1000用户 × 10对话/月 × 12月)

-- 阅读历史表
reading_history: ~60,000行/年
  (1000用户 × 5篇/月 × 12月)

-- 用户画像表
user_profiles: ~1,000行/年

总存储需求：
  - 数据：~500MB/年
  - 索引：~200MB/年
  - 总计：~1GB/年
```

---

### 5.4 数据质量标准

#### REQ-D7: 数据质量要求

**完整性要求**:
```
Paper实体：
- 必填字段完整率：100%
- 可选字段完整率：> 60%

Method实体：
- 名称唯一性：100%
- 描述完整率：> 80%

关系：
- 有效关系（源和目标节点存在）：100%
- 关系属性完整率：> 70%
```

**准确性要求**:
```
实体抽取：
- 准确率：> 85%
- 召回率：> 80%
- F1分数：> 82%

关系抽取：
- 准确率：> 75%
- 召回率：> 70%
- F1分数：> 72%

元数据准确性：
- 论文标题匹配：> 95%
- 作者识别准确率：> 90%
- 年份准确率：100%
```

**一致性要求**:
```
实体归一化：
- 重复实体检测率：> 90%
- 自动合并准确率：> 85%

数据格式：
- 日期格式：ISO 8601
- 文本编码：UTF-8
- 数值精度：小数点后2位
```

**时效性要求**:
```
数据更新：
- 用户画像更新：实时
- 图谱数据更新：< 5分钟
- 推荐结果更新：< 1小时
- 社区重建：每周
```

---

### 5.5 数据获取与处理

#### REQ-D8: 数据获取流程

**种子数据获取**:
```python
# 1. arXiv数据获取
def fetch_arxiv_papers(categories, start_date, end_date, limit):
    """
    从arXiv API批量获取论文
    
    参数：
    - categories: ['cs.CV', 'cs.AI', 'cs.LG']
    - start_date: '2020-01-01'
    - end_date: '2024-12-31'
    - limit: 1000
    """
    papers = []
    for category in categories:
        query = f"cat:{category} AND submittedDate:[{start_date} TO {end_date}]"
        results = arxiv.Search(query=query, max_results=limit)
        papers.extend(process_arxiv_results(results))
    return papers

# 2. 论文PDF下载
def download_papers(papers):
    """批量下载论文PDF"""
    for paper in papers:
        pdf = download_pdf(paper.pdf_url)
        save_to_storage(pdf, f"seeds/{paper.arxiv_id}.pdf")

# 3. 批量摄入
def batch_ingest(pdf_files):
    """批量摄入到图谱"""
    for pdf in pdf_files:
        task = ingest_pdf_task.delay(pdf)
        monitor_task_status(task.id)
```

**数据预处理Pipeline**:
```
原始PDF
  ↓
文本提取（PyMuPDF）
  ↓
文本清洗
  - 移除页眉页脚
  - 修复断行
  - 统一格式
  ↓
章节识别
  - Abstract
  - Introduction
  - Method
  - Experiments
  - Conclusion
  ↓
分块（Chunking）
  - 每个section作为一个chunk
  - 长section进一步分割（< 2000 tokens）
  ↓
质量检查
  - 文本完整性
  - 格式规范性
  - 可读性评分
  ↓
存储到暂存区
```

**数据验证Pipeline**:
```
实体抽取结果
  ↓
格式验证
  - Schema compliance
  - 必填字段检查
  ↓
语义验证
  - 实体类型合理性
  - 关系逻辑一致性
  ↓
去重检查
  - 实体名称相似度
  - 自动合并建议
  ↓
人工审核（抽样10%）
  ↓
写入图谱
```

---

### 5.6 数据安全与隐私

#### REQ-D9: 数据安全要求

**数据分类**:
```
Level 1 - 公开数据：
  - 论文元数据
  - 实体和关系
  - 公开的图谱数据
  - 保护措施：无需加密

Level 2 - 用户数据：
  - 用户画像
  - 阅读历史
  - 聊天历史
  - 保护措施：传输加密 + 访问控制

Level 3 - 敏感数据：
  - 用户凭证（密码）
  - 个人身份信息
  - 保护措施：加密存储 + 严格访问控制
```

**加密要求**:
```
传输加密：
  - HTTPS/TLS 1.3
  - 最小密钥长度：2048 bits

存储加密：
  - 密码：bcrypt (cost factor: 12)
  - 敏感字段：AES-256
  - 数据库：透明数据加密（TDE）
```

**访问控制**:
```
数据库访问：
  - 最小权限原则
  - 应用账号：读写权限
  - 备份账号：只读权限
  - 管理账号：全部权限（审计日志）

API访问：
  - JWT Token认证
  - 用户只能访问自己的数据
  - 管理员可访问所有数据（审计日志）
```

**隐私保护**:
```
数据匿名化：
  - 测试环境使用脱敏数据
  - 用户ID不可逆哈希
  - 日志中不记录敏感信息

数据删除：
  - 用户可删除自己的数据
  - 删除后30天内可恢复
  - 30天后物理删除
```

---

### 5.7 数据治理

#### REQ-D10: 数据管理规范

**数据所有权**:
```
论文数据：
  - 来源：公开数据源
  - 版权：遵循原始论文版权
  - 使用：学术研究用途

用户数据：
  - 所有权：用户本人
  - 使用：经用户同意
  - 导出：用户可导出自己的数据
```

**数据质量监控**:
```
每日监控指标：
  - 新增论文数
  - 实体抽取成功率
  - 数据完整性
  - 异常数据检测

每周报告：
  - 数据质量评分
  - 数据增长趋势
  - 异常问题汇总
  - 改进建议
```

**数据版本管理**:
```
Schema版本：
  - 使用语义化版本（Semantic Versioning）
  - 版本变更需要迁移脚本
  - 保持向后兼容性

图谱快照：
  - 每月创建快照
  - 快照保留6个月
  - 用于回滚和审计
```

**数据清理策略**:
```
定期清理：
  - 临时文件：7天
  - 失败任务记录：30天
  - 系统日志：90天
  - 用户删除数据：30天软删除 + 物理删除

数据归档：
  - 1年以上的聊天历史：归档到冷存储
  - 访问频率 < 1次/月的论文：归档
  - 归档数据查询延迟：< 5秒
```

---

### 5.8 数据需求优先级

| 数据需求ID | 需求名称 | 优先级 | 责任人 | 依赖 | 交付时间 |
|-----------|---------|--------|--------|------|---------|
| REQ-D1 | 种子论文库 | P0 | @Dev-B | - | Sprint 1 |
| REQ-D2 | Schema定义 | P0 | @Dev-B | - | Sprint 1 |
| REQ-D3 | 测试数据集 | P0 | @QA | REQ-D1 | Sprint 1 |
| REQ-D4 | 用户数据结构 | P0 | @Dev-D | - | Sprint 1 |
| REQ-D5 | 图谱数据规划 | P0 | @Dev-B | REQ-D2 | Sprint 1 |
| REQ-D6 | 关系DB设计 | P0 | @Dev-D | - | Sprint 1 |
| REQ-D7 | 数据质量标准 | P1 | @QA | REQ-D3 | Sprint 2 |
| REQ-D8 | 数据获取流程 | P0 | @Dev-E | REQ-D1 | Sprint 2 |
| REQ-D9 | 数据安全规范 | P1 | @DevOps | - | Sprint 2 |
| REQ-D10 | 数据治理规范 | P2 | @PM | - | Sprint 3 |

---

## 6. 非功能需求

### 6.1 性能需求

| 指标 | 要求 | 测试方法 |
|-----|------|---------|
| API响应时间 | P95 < 3秒 | 压力测试 |
| 图谱搜索 | < 2秒 | 性能测试 |
| PDF解析 | < 2分钟 | 计时测试 |
| 并发用户 | 支持100+ | 并发测试 |
| 数据库查询 | < 500ms | 慢查询监控 |

### 6.2 可靠性需求

- **系统可用性**: 99.5%
- **数据备份**: 每日增量备份
- **错误处理**: 所有API都有错误处理
- **日志记录**: 完整的操作日志

### 6.3 安全需求

- **API认证**: JWT Token（暂用mock）
- **数据加密**: HTTPS传输
- **输入验证**: Pydantic验证
- **SQL注入防护**: ORM参数化查询

### 6.4 可扩展性需求

- **模块化设计**: 各模块独立
- **服务解耦**: 异步任务队列
- **水平扩展**: 支持多实例部署
- **配置外部化**: 环境变量管理

### 6.5 可维护性需求

- **代码规范**: PEP8
- **注释覆盖**: > 60%
- **单元测试**: 覆盖率 > 70%
- **API文档**: OpenAPI自动生成

---

## 7. 技术架构

### 7.1 系统架构图

```
┌─────────────┐
│   前端UI    │
│  (React)    │
└──────┬──────┘
       │ HTTP/WebSocket
       ↓
┌─────────────────────────────────┐
│      FastAPI Backend            │
├─────────────────────────────────┤
│  API Layer (routes/)            │
│  Service Layer (services/)      │
│  Model Layer (models/)          │
└──────┬──────────────────┬───────┘
       │                  │
       ↓                  ↓
┌─────────────┐    ┌─────────────┐
│  Graphiti   │    │   Celery    │
│  + Neo4j    │    │   Worker    │
└─────────────┘    └──────┬──────┘
                          │
                          ↓
                   ┌─────────────┐
                   │   Redis     │
                   └─────────────┘
```

### 7.2 技术栈

| 层级 | 技术选型 | 版本 |
|-----|---------|------|
| Web框架 | FastAPI | 0.109+ |
| 图谱引擎 | Graphiti + Neo4j | Latest |
| LLM | OpenAI GPT-4 | gpt-4-turbo |
| 向量化 | Sentence-Transformers | 2.2+ |
| 任务队列 | Celery + Redis | 5.3+ |
| 数据库 | PostgreSQL | 14+ |
| PDF解析 | PyMuPDF | 1.23+ |
| 容器化 | Docker | 20.10+ |

### 7.3 数据库设计

**Neo4j（图数据库）**:
- 节点: Paper, Method, Dataset, Task, Metric, Author, Institution, Concept
- 关系: PROPOSES, EVALUATES_ON, SOLVES, CITES, etc.
- 使用Graphiti管理

**MySQL（关系数据库）**:
```sql
-- 用户表
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP NULL,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 聊天历史表
CREATE TABLE chat_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(100),
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    tools_used JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_time (user_id, timestamp DESC),
    INDEX idx_session (session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 阅读历史表
CREATE TABLE reading_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    paper_id VARCHAR(100) NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    INDEX idx_user_read (user_id, read_at DESC),
    INDEX idx_paper (paper_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 用户画像表
CREATE TABLE user_profiles (
    user_id VARCHAR(50) PRIMARY KEY,
    research_direction TEXT,
    interests JSON,
    expertise_level VARCHAR(20),
    reading_count INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**数据库迁移管理（Alembic）**:

Alembic配置文件 `alembic.ini`:
```ini
[alembic]
script_location = alembic
sqlalchemy.url = mysql+pymysql://user:password@localhost/research_agent

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic
```

迁移脚本示例 `alembic/versions/001_create_users.py`:
```python
"""create users table

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(50), primary_key=True),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('last_login', sa.TIMESTAMP, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    op.create_index('idx_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_email', 'users')
    op.drop_table('users')
```

**Alembic常用命令**:
```bash
# 初始化Alembic
alembic init alembic

# 创建迁移脚本
alembic revision -m "create users table"

# 自动生成迁移（检测模型变化）
alembic revision --autogenerate -m "add new columns"

# 执行迁移（升级到最新版本）
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

---

## 8. 开发分工

### 8.1 团队组成

| 角色 | 姓名 | 职责 | 负责模块 |
|-----|------|------|---------|
| 项目经理 | [PM] | 整体协调、进度管理 | 全部 |
| 后端开发A | [Dev-A] | 论文管理模块 | Module A |
| 后端开发B | [Dev-B] | 知识图谱模块 | Module B |
| 后端开发C | [Dev-C] | 智能问答模块 | Module C |
| 后端开发D | [Dev-D] | 用户画像模块 | Module D |
| 后端开发E | [Dev-E] | 搜索与推荐 | Module E |
| 后端开发F | [Dev-F] | 社区管理 | Module F |
| 后端开发G | [Dev-G] | **图谱可视化模块**（交互式） | Module G |
| 后端开发H | [Dev-H] | 用户认证模块 | Module H |
| 测试工程师 | [QA] | 测试、质量保证 | 全部 |
| DevOps | [Ops] | 部署、运维 | 基础设施 |

### 8.2 模块依赖关系

```
Module H (用户认证)      ← 基础模块，最先开发（Week 1）
    ↓
Module B (图谱)          ← 基础模块（Week 1-2）
    ↓
Module A (论文管理)      ← 依赖Module H, B
    ↓
Module C (智能问答)      ← 依赖Module A, B
    ↓
Module D (用户画像)      ← 依赖Module C, H
Module E (搜索推荐)      ← 依赖Module A, B, D
    ↓
Module F (社区管理)      ← 依赖Module B
Module G (可视化)        ← 依赖Module B
```

**开发顺序建议**:
1. Week 1: Module H (用户认证) + 数据库初始化
2. Week 1-2: Module B (图谱基础，可与H部分并行)
3. Week 3-4: Module A (论文管理)
4. Week 5-7: Module C (智能问答)
5. Week 6-7: Module D (用户画像，可并行)
6. Week 7-8: Module E (搜索推荐)
7. Week 8: Module F, G (社区、可视化，可并行)

### 8.3 沟通机制

- **每日站会**: 早上10:00，15分钟，同步进度和问题
- **周会**: 每周五下午，Review本周进度，规划下周任务
- **技术评审**: 关键功能开发前，团队评审设计方案
- **代码审查**: 所有PR需至少1人Review
- **文档同步**: 使用Confluence维护技术文档

---

## 9. 里程碑与交付

### 9.1 迭代计划

#### Sprint 1: 基础架构（Week 1-2）

**目标**: 搭建基础架构，完成用户认证和图谱模块

**交付物**:
- [ ] Docker环境搭建完成（MySQL + Neo4j + Redis）
- [ ] Alembic数据库迁移配置完成
- [ ] 用户认证模块实现（REQ-H1~H7）
- [ ] JWT认证中间件实现
- [ ] Schema定义完成（REQ-B4）
- [ ] 图谱搜索实现（REQ-B1, B2, B3）
- [ ] 单元测试覆盖率 > 60%

**Demo内容**:
- 演示用户注册和登录
- 演示JWT Token认证
- 演示图谱搜索API（需登录）
- 演示节点查询API

---

#### Sprint 2: 论文管理（Week 3-4）

**目标**: 实现论文上传、解析、摄入

**交付物**:
- [ ] PDF上传API（REQ-A1）
- [ ] PDF解析器实现
- [ ] 实体抽取服务实现
- [ ] 论文查询API（REQ-A2, A3）
- [ ] 异步任务正常运行

**Demo内容**:
- 演示上传论文并自动构建图谱
- 演示论文查询

---

#### Sprint 3: 智能问答（Week 5-7）

**目标**: 实现Agent对话和工具系统

**交付物**:
- [ ] 6个工具全部实现（REQ-C2）
- [ ] Agent对话实现（REQ-C1）
- [ ] 对话历史实现（REQ-C3）
- [ ] 端到端对话测试通过

**Demo内容**:
- 演示完整对话流程
- 演示工具调用
- 演示外部搜索fallback

---

#### Sprint 4: 外部搜索与扩展功能（Week 6-8）

**目标**: 实现外部搜索、社区管理和可视化

**交付物**:
- [ ] 外部搜索集成（REQ-E1）
- [ ] 社区管理（REQ-F1, F2）
- [ ] 可视化支持（REQ-G1）

**Demo内容**:
- 演示外部搜索和自动摄入
- 演示社区检测
- 演示图谱可视化

---

### 9.2 最终交付物

**代码**:
- [ ] 完整的后端代码（所有模块）
- [ ] 单元测试（覆盖率 > 70%）
- [ ] 集成测试
- [ ] 代码符合规范（PEP8）

**文档**:
- [ ] API文档（OpenAPI）
- [ ] 部署文档
- [ ] 用户手册
- [ ] 技术文档

**环境**:
- [ ] Docker镜像
- [ ] docker-compose配置
- [ ] 环境变量说明
- [ ] 数据库迁移脚本

**演示**:
- [ ] 完整功能演示视频
- [ ] PPT演示文稿

---

## 10. 验收标准

### 10.1 功能验收

**P0功能（必须实现）**:
- [x] 论文上传和解析
- [x] 知识图谱构建
- [x] 图谱搜索
- [x] Agent智能问答
- [x] 工具调用
- [x] 外部搜索fallback

**P1功能（重要）**:
- [x] 对话历史
- [ ] 用户图谱可视化（含节点/边详情查询）

**P2功能（增强）**:
- [x] 社区检测
- [ ] 图谱统计概览

### 10.2 性能验收

| 指标 | 目标 | 测试方法 | 是否通过 |
|-----|------|---------|---------|
| API响应时间 | P95 < 3秒 | 压力测试 | [ ] |
| 图谱数据获取 | < 5秒（5000节点） | 性能测试 | [ ] |
| 节点详情查询 | < 500ms | 性能测试 | [ ] |
| 并发用户 | 100+ | JMeter测试 | [ ] |
| 论文解析准确率 | > 85% | 人工抽样 | [ ] |
| 推荐精准度 | > 60% | 用户反馈 | [ ] |
| 系统可用性 | > 99% | 监控统计 | [ ] |

### 10.3 质量验收

- [ ] 单元测试覆盖率 > 70%
- [ ] 所有P0功能有集成测试
- [ ] 无P0/P1级别bug
- [ ] P2级别bug < 5个
- [ ] 代码通过Lint检查
- [ ] API文档完整

### 10.4 验收流程

1. **开发自测**: 开发人员完成模块后自测
2. **代码审查**: PR提交，至少1人Review
3. **QA测试**: 测试工程师执行测试用例
4. **集成测试**: 多模块联调测试
5. **用户验收**: PM和产品经理验收
6. **部署上线**: DevOps部署到生产环境

---

## 11. 风险管理

### 11.1 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|-----|------|------|---------|
| LLM API限流 | 中 | 高 | 实现请求队列，添加重试机制 |
| Neo4j性能瓶颈 | 中 | 高 | 优化查询，添加索引，考虑分片 |
| PDF解析失败率高 | 中 | 中 | 多个解析器备用，人工校验 |
| 实体抽取准确率低 | 高 | 高 | 优化Prompt，添加后处理规则 |
| 外部API不稳定 | 中 | 中 | 添加缓存，实现降级方案 |

### 11.2 进度风险

| 风险 | 概率 | 影响 | 应对措施 |
|-----|------|------|---------|
| 需求变更 | 中 | 高 | 冻结需求，变更走评审流程 |
| 人员变动 | 低 | 高 | 代码文档完善，知识共享 |
| 技术难点卡住 | 中 | 中 | 提前技术攻关，寻求外部支持 |
| 测试时间不足 | 中 | 中 | TDD开发，边开发边测试 |

### 11.3 资源风险

| 风险 | 概率 | 影响 | 应对措施 |
|-----|------|------|---------|
| OpenAI成本过高 | 中 | 中 | 监控用量，优化调用次数 |
| 服务器资源不足 | 低 | 中 | 云服务按需扩容 |
| 第三方服务故障 | 低 | 高 | 关键服务多备份 |

### 11.4 风险监控

- **每日**: 检查关键指标（API成功率、LLM用量）
- **每周**: Review风险清单，更新应对措施
- **每月**: 总结风险经验，优化风险管理

---

## 12. 附录

### 12.1 术语表

| 术语 | 定义 |
|-----|------|
| Graphiti | 知识图谱框架，基于Neo4j |
| Episode | Graphiti中的数据单元，代表一次数据摄入 |
| Entity | 实体，如Paper、Method、Dataset |
| Relation | 关系，如PROPOSES、CITES |
| Community | 社区，相关实体的聚类 |
| Agent | AI代理，可以调用工具完成任务 |
| Tool | Agent可调用的功能模块 |
| Namespace | 图谱命名空间，用于隔离用户数据 |
| Fallback | 降级机制，当主要方法失败时的备选方案 |

### 12.2 参考文档

- **Graphiti API文档**: `Graphiti API文档.md`
- **功能需求清单**: `functional-requirements.md`
- **架构分析**: `开发日志/架构分析与改进方案.md`
- **开发TodoList**: `开发日志/项目后端开发TodoList.md`

### 12.3 联系方式

| 角色 | 姓名 | 邮箱 | 钉钉/企微 |
|-----|------|------|----------|
| 项目经理 | [PM] | pm@example.com | - |
| 技术负责人 | [TL] | tl@example.com | - |

---

## 📝 文档变更记录

| 版本 | 日期 | 修改人 | 修改内容 |
|-----|------|--------|---------|
| v1.0 | 2025-12-09 | PM | 初始版本 |
| v1.1 | 2025-12-09 | PM | 新增第5章：数据需求（10个子需求） |
| v1.2 | 2025-12-09 | PM | 新增Module H：用户认证（7个子需求）<br>数据库改为MySQL + Alembic |
| v1.3 | 2025-12-09 | PM | 简化MVP范围：<br>- 移除user_role<br>- 前后端职责明确（验证逻辑前置）<br>- 删除A2论文查询、D1用户画像、D2阅读历史、E2论文推荐、E3论文对比 |
| v1.4 | 2025-12-10 | PM | **重大更新**：Module G 图谱可视化模块<br>- 重新设计为交互式图谱可视化（P1优先级提升）<br>- REQ-G1: 用户图谱数据获取API（支持筛选、分页、局部查询）<br>- REQ-G2: 节点详情查询API（支持点击查看属性）<br>- REQ-G3: 边详情查询API（支持点击查看关系属性）<br>- REQ-G4: 图谱统计概览API<br>- REQ-G5: 节点邻居展开API（支持双击展开）<br>- 所有API支持JWT认证和权限控制<br>- 预计工期调整为1.5周 |

---

## ✅ 签署确认

**项目经理**: ________________  日期: __________

**技术负责人**: ________________  日期: __________

**产品经理**: ________________  日期: __________

---

**项目启动日期**: 2025-12-10  
**预计完成日期**: 2026-02-09  
**当前状态**: 🟢 进行中

---

*本PRD为ResearchAgent v1.0的正式产品需求文档，所有开发工作应以本文档为准。如有疑问或需要澄清，请联系项目经理。*

