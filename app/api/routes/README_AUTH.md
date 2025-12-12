# 用户认证模块 - 开发文档

## 📋 概述

本模块实现了AI科研助手系统的用户认证功能，符合PRD_认证模块.md的设计规范。

**负责人**: Backend Developer  
**优先级**: P0（MVP必需）  
**状态**: ✅ 已完成

## 🎯 API端点

### REQ-AUTH-1: 用户注册
- **端点**: `POST /api/v1/auth/register`
- **功能**: 
  - 新用户通过用户名和密码注册账号
  - 用户名唯一性验证（正则：`^[a-zA-Z0-9_]{3,50}$`）
  - 密码bcrypt加密（salt rounds = 12）
  - 注册成功后在Neo4j中创建用户专属的图谱命名空间

### REQ-AUTH-2: 用户登录
- **端点**: `POST /api/v1/auth/login`
- **功能**:
  - 用户通过用户名和密码登录
  - 验证成功后返回JWT access_token和refresh_token
  - 登录限流：同一用户名15分钟内最多尝试5次

### REQ-AUTH-3: 刷新Token
- **端点**: `POST /api/v1/auth/refresh`
- **功能**:
  - 使用refresh_token获取新的access_token
  - 避免用户频繁重新登录

### REQ-AUTH-4: 修改密码
- **端点**: `POST /api/v1/auth/change-password`
- **功能**:
  - 已登录用户修改自己的密码
  - 需要验证旧密码

### REQ-AUTH-5: 用户登出
- **端点**: `POST /api/v1/auth/logout`
- **功能**:
  - 用户登出系统
  - 将当前Token加入黑名单

## 🔧 技术规格

### JWT Token结构

**access_token (有效期30分钟)**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "researcher001",
  "exp": 1704456789,
  "type": "access"
}
```

**refresh_token (有效期7天)**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "exp": 1705060589,
  "type": "refresh"
}
```

### 密码要求
- 长度 >= 8位
- 包含大写字母
- 包含小写字母
- 包含数字

### 文件结构
```
app/
├── api/
│   ├── routes/
│   │   └── auth.py          # 认证路由
│   └── dependencies/
│       └── auth.py          # JWT认证中间件
├── services/
│   └── auth_service.py      # 认证服务
├── schemas/
│   └── auth.py              # 请求/响应模型
├── core/
│   ├── security.py          # 密码加密、Token生成
│   └── redis_client.py      # Token黑名单、登录限流
└── models/
    └── db_models.py         # User模型
```

## 📝 API使用示例

### 1. 用户注册

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "researcher001",
    "password": "Password123",
    "email": "researcher@example.com"
  }'
```

**响应 (201 Created)**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "researcher001",
  "created_at": "2025-12-11T10:00:00Z",
  "message": "Registration successful"
}
```

### 2. 用户登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "researcher001",
    "password": "Password123"
  }'
```

**响应 (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "researcher001"
  }
}
```

### 3. 刷新Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**响应 (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 4. 修改密码

```bash
curl -X POST "http://localhost:8000/api/v1/auth/change-password" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "Password123",
    "new_password": "NewPassword456"
  }'
```

**响应 (200 OK)**:
```json
{
  "message": "Password changed successfully",
  "require_relogin": true
}
```

### 5. 登出

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应 (200 OK)**:
```json
{
  "message": "Logged out successfully"
}
```

## 🚨 错误响应

### 400 Bad Request - 用户名已存在
```json
{
  "error": "INVALID_INPUT",
  "message": "Username already exists"
}
```

### 400 Bad Request - 密码过弱
```json
{
  "error": "WEAK_PASSWORD",
  "message": "Password must be at least 8 characters and contain uppercase, lowercase, and numbers"
}
```

### 401 Unauthorized - 凭证错误
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Invalid username or password"
}
```

### 401 Unauthorized - 旧密码错误
```json
{
  "error": "WRONG_PASSWORD",
  "message": "Old password is incorrect"
}
```

### 401 Unauthorized - Token无效
```json
{
  "error": "INVALID_TOKEN",
  "message": "Invalid or expired refresh token"
}
```

### 429 Too Many Requests - 登录尝试过多
```json
{
  "error": "RATE_LIMIT",
  "message": "Too many login attempts. Please try again in 15 minutes."
}
```

## 🔐 安全考虑

1. **密码存储**: 使用bcrypt哈希，salt rounds = 12
2. **Token安全**:
   - access_token有效期：30分钟
   - refresh_token有效期：7天
   - 使用HS256签名算法
   - SECRET_KEY存储在环境变量中
3. **登录限流**: 同一用户名15分钟内最多尝试5次
4. **Token黑名单**: 登出后Token立即失效
5. **HTTPS传输**: 生产环境必须使用HTTPS

## ✅ 验收标准

1. ✅ 用户注册成功后，MySQL中有对应记录，密码已哈希
2. ✅ 登录成功返回有效的JWT Token
3. ✅ Token刷新机制正常工作
4. ✅ 修改密码后，旧Token失效（如实现了黑名单）
5. ✅ 登出后Token无法继续使用
6. ✅ 所有错误响应符合规范

## 🧪 运行测试

```bash
# 运行认证模块测试
pytest tests/test_auth.py -v

# 运行快速集成测试
python scripts/test_auth_module.py
```

---

**最后更新**: 2025-12-12  
**版本**: v2.0 (符合PRD_认证模块.md)  
**状态**: ✅ 已完成
