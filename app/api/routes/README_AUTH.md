# 用户认证模块 (Module H) - 开发文档

## 📋 概述

本模块实现了AI科研助手系统的用户认证功能，符合开发任务分配表v1.3/v1.4的要求。

**负责人**: 后端开发H  
**优先级**: P0（基础功能）  
**状态**: ✅ 已完成

## 🎯 已完成任务

### ✅ 任务1: 用户注册 (REQ-H1)
- **API端点**: `POST /api/auth/register`
- **功能**: 
  - 用户注册接口
  - 邮箱唯一性验证
  - 密码bcrypt加密（cost=12）
  - 生成JWT Token
- **文件位置**:
  - `app/api/routes/auth.py` - 认证路由
  - `app/services/auth_service.py` - 认证服务
  - `app/models/user_models.py` - 用户模型
  - `app/core/security.py` - 密码加密、Token生成

### ✅ 任务2: 用户登录 (REQ-H2)
- **API端点**: `POST /api/auth/login`
- **功能**:
  - 用户登录接口
  - 验证用户凭证
  - 生成JWT Token（access + refresh）
  - 更新登录时间
  - 登录失败3次锁定账户（5分钟）

### ✅ 任务3: Token刷新 (REQ-H3)
- **API端点**: `POST /api/auth/refresh`
- **功能**:
  - 使用refresh_token获取新access_token
  - 验证refresh_token有效性

### ✅ 任务4: 用户登出 (REQ-H4)
- **API端点**: `POST /api/auth/logout`
- **功能**:
  - 用户登出
  - Token加入Redis黑名单
  - 设置正确的TTL

### ✅ 任务5: 获取用户信息 (REQ-H5)
- **API端点**: `GET /api/auth/me`
- **功能**:
  - 获取当前登录用户信息
  - 解析JWT Token

### ✅ 任务6: 密码修改 (REQ-H6)
- **API端点**: `POST /api/auth/change-password`
- **功能**:
  - 修改密码
  - 验证旧密码
  - 密码加密存储

### ✅ 任务7: JWT认证中间件 (REQ-H7)
- **文件位置**: `app/api/dependencies/auth.py`
- **功能**:
  - 实现JWT认证依赖
  - 验证Token有效性
  - 检查黑名单
  - 获取当前用户信息

## 🔧 v1.3 更新内容

根据PRD v1.3要求，已完成以下修改：

1. **移除user_role字段**
   - ❌ 数据库模型中移除`user_role`列
   - ❌ 注册请求中移除`user_role`参数
   - ❌ JWT Token中移除`role`字段
   - ❌ 移除角色权限依赖函数`require_role()`

2. **移除confirm_password验证**
   - ❌ 注册请求中移除`confirm_password`参数
   - ❌ 修改密码请求中移除`confirm_new_password`参数
   - ✅ 前端负责密码一致性验证

3. **JWT Token结构**
   ```json
   {
     "sub": "u_1234567890",
     "email": "zhangsan@example.com",
     "exp": 1704456789,
     "iat": 1704453189
   }
   ```
   **注意**: 不再包含`role`字段

## 📦 交付物

- ✅ 7个API端点实现
- ✅ JWT认证中间件
- ✅ 密码加密工具
- ✅ Token生成工具
- ✅ Redis黑名单管理
- ✅ 单元测试（覆盖率 > 80%）
- ✅ API文档

## 🗄️ 数据库迁移

### 创建迁移

```bash
# 查看当前迁移状态
alembic current

# 执行迁移到最新版本
alembic upgrade head

# 回滚一个版本
alembic downgrade -1
```

### 迁移脚本

1. **001_initial_tables.py** - 创建初始表（包含旧的user_role字段）
2. **002_remove_user_role.py** - 移除user_role字段（v1.3要求）

## 🧪 运行测试

### 安装测试依赖

```bash
pip install -r tests/requirements-test.txt
```

### 运行所有测试

```bash
# 运行所有测试
pytest tests/test_auth.py -v

# 运行特定测试类
pytest tests/test_auth.py::TestUserRegistration -v

# 运行特定测试方法
pytest tests/test_auth.py::TestUserRegistration::test_register_success -v

# 生成覆盖率报告
pytest tests/test_auth.py --cov=app.services.auth_service --cov=app.api.routes.auth --cov-report=html
```

### 测试覆盖范围

- ✅ 用户注册（成功、重复邮箱、弱密码）
- ✅ 用户登录（成功、错误密码、不存在的用户）
- ✅ Token刷新（成功、无效Token）
- ✅ 用户登出（成功、Token黑名单验证）
- ✅ 获取用户信息（成功、未提供Token）
- ✅ 修改密码（成功、旧密码错误）
- ✅ 密码加密验证
- ✅ JWT Token解码

## 📞 协作接口

### 提供给其他模块

```python
from app.api.dependencies.auth import get_current_user
from app.services.auth_service import AuthService
from app.core.security import hash_password, verify_password, create_access_token

# 在其他路由中使用JWT认证
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.user_id}
```

### 依赖

- MySQL数据库
- Redis（Token黑名单、登录失败计数）
- python-jose（JWT）
- passlib[bcrypt]（密码加密）

## 🔐 安全特性

1. **密码加密**: bcrypt算法，cost=12
2. **JWT Token**: 
   - access_token有效期1小时
   - refresh_token有效期7天
   - 算法: HS256
3. **登录保护**: 失败3次锁定5分钟
4. **Token黑名单**: 登出后Token立即失效
5. **密码强度要求**:
   - 长度 ≥ 8位
   - 包含大写字母
   - 包含小写字母
   - 包含数字
   - 包含特殊字符

## 📝 API使用示例

### 1. 用户注册

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "张三",
    "email": "zhangsan@example.com",
    "password": "SecurePass123!"
  }'
```

### 2. 用户登录

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhangsan@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. 获取用户信息

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

### 4. 刷新Token

```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

### 5. 修改密码

```bash
curl -X POST "http://localhost:8000/api/auth/change-password" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "OldPass123!",
    "new_password": "NewPass456!"
  }'
```

### 6. 登出

```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer <access_token>"
```

## 🐛 常见问题

### Q1: 密码强度验证失败
**A**: 确保密码至少8位，包含大小写字母、数字和特殊字符。前端应该在提交前进行验证。

### Q2: Token过期
**A**: 使用refresh_token获取新的access_token，或重新登录。

### Q3: 登录失败次数过多
**A**: 等待5分钟后重试，或联系管理员重置。

### Q4: 邮箱已被注册
**A**: 使用其他邮箱注册，或使用该邮箱登录。

## 📊 性能指标

- ✅ 注册响应时间 < 1秒
- ✅ 登录响应时间 < 500ms
- ✅ Token刷新响应时间 < 200ms
- ✅ 获取用户信息响应时间 < 200ms
- ✅ JWT认证中间件性能影响 < 50ms

## 🎉 验收标准

- ✅ 所有7个API端点正常工作
- ✅ JWT认证中间件正确验证Token
- ✅ 密码正确加密（bcrypt, cost=12）
- ✅ Token黑名单机制正常
- ✅ 登录失败锁定机制正常
- ✅ 单元测试覆盖率 > 80%
- ✅ API文档完整
- ✅ 错误处理完善
- ✅ 响应时间符合要求

## 📅 开发时间

- **计划工期**: 1周
- **实际工期**: 1周
- **开发人员**: 后端开发H

---

**最后更新**: 2025-12-10  
**版本**: v1.3  
**状态**: ✅ 已完成并通过验收

