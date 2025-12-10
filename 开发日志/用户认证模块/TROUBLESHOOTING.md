# 🔧 故障排查指南

## 问题1: ModuleNotFoundError: No module named 'asyncmy'

### 错误信息
```
ModuleNotFoundError: No module named 'asyncmy'
```

### 原因
缺少MySQL异步驱动`asyncmy`包。

### 解决方案

#### 方案1: 安装单个包（推荐）

在虚拟环境中运行：

```bash
# Windows (PowerShell)
.venv\Scripts\pip install asyncmy

# Windows (CMD)
.venv\Scripts\pip.exe install asyncmy

# Linux/macOS
source .venv/bin/activate
pip install asyncmy
```

#### 方案2: 重新安装所有依赖

```bash
# Windows (PowerShell)
.venv\Scripts\pip install -r requirements.txt

# Windows (CMD)
.venv\Scripts\pip.exe install -r requirements.txt

# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

#### 方案3: 使用aiomysql替代asyncmy

如果asyncmy安装失败，可以使用aiomysql：

1. 修改`requirements.txt`:
```
# 注释掉asyncmy
# asyncmy>=0.2.9

# 添加aiomysql
aiomysql>=0.2.0
```

2. 修改`app/core/database.py`的DATABASE_URL:
```python
# 原来
DATABASE_URL = (
    f"mysql+asyncmy://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}"
    f"/{settings.MYSQL_DATABASE}?charset=utf8mb4"
)

# 改为
DATABASE_URL = (
    f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}"
    f"/{settings.MYSQL_DATABASE}?charset=utf8mb4"
)
```

3. 安装aiomysql:
```bash
.venv\Scripts\pip install aiomysql
```

### 验证安装

```bash
# 验证asyncmy是否安装成功
.venv\Scripts\python -c "import asyncmy; print(asyncmy.__version__)"

# 或验证aiomysql
.venv\Scripts\python -c "import aiomysql; print(aiomysql.__version__)"
```

---

## 问题2: 虚拟环境激活问题

### Windows PowerShell执行策略错误

如果遇到以下错误：
```
无法加载文件 .venv\Scripts\Activate.ps1，因为在此系统上禁止运行脚本
```

**解决方案**:
```powershell
# 临时允许执行脚本（当前会话）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 然后激活虚拟环境
.venv\Scripts\Activate.ps1
```

### 使用CMD代替PowerShell

```cmd
# 激活虚拟环境
.venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt
```

---

## 问题3: MySQL连接失败

### 错误信息
```
Can't connect to MySQL server
```

### 检查清单

1. **MySQL服务是否运行**:
```bash
# Windows
net start mysql

# 查看MySQL服务状态
sc query mysql
```

2. **验证MySQL配置**:
```bash
mysql -u root -p
```

3. **检查.env配置**:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=research_agent
```

4. **创建数据库**:
```sql
CREATE DATABASE research_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 问题4: Redis连接失败

### 错误信息
```
Error connecting to Redis
```

### 检查清单

1. **Redis服务是否运行**:
```bash
# Windows
redis-server

# 测试连接
redis-cli ping
# 应该返回: PONG
```

2. **检查.env配置**:
```env
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

---

## 问题5: Alembic迁移失败

### 错误信息
```
Target database is not up to date
```

### 解决方案

1. **查看当前迁移状态**:
```bash
alembic current
```

2. **查看迁移历史**:
```bash
alembic history
```

3. **升级到最新版本**:
```bash
alembic upgrade head
```

4. **如果迁移冲突，回滚后重新升级**:
```bash
# 回滚到初始状态
alembic downgrade base

# 重新升级
alembic upgrade head
```

---

## 问题6: 导入模块错误

### 错误信息
```
ImportError: attempted relative import with no known parent package
```

### 解决方案

确保从项目根目录运行：

```bash
# 正确 ✅
cd d:\My_Python_Project\graduationProject
python -m uvicorn main:app --reload

# 错误 ❌
cd d:\My_Python_Project\graduationProject\app
python -m uvicorn main:app --reload
```

---

## 问题7: 端口被占用

### 错误信息
```
[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

### 解决方案

#### 方案1: 使用其他端口
```bash
uvicorn main:app --reload --port 8001
```

#### 方案2: 查找并关闭占用端口的进程
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# Linux/macOS
lsof -i :8000
kill -9 <进程ID>
```

---

## 问题8: 依赖版本冲突

### 错误信息
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

### 解决方案

#### 方案1: 使用虚拟环境（推荐）
```bash
# 创建新的虚拟环境
python -m venv .venv_new

# Windows
.venv_new\Scripts\activate
pip install -r requirements.txt

# Linux/macOS
source .venv_new/bin/activate
pip install -r requirements.txt
```

#### 方案2: 强制重新安装
```bash
pip install --force-reinstall -r requirements.txt
```

---

## 快速诊断脚本

创建一个诊断脚本来检查环境：

```python
# scripts/diagnose.py
import sys
import os

print("🔍 环境诊断\n")

# 1. Python版本
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}\n")

# 2. 检查关键包
packages = [
    'fastapi', 'uvicorn', 'sqlalchemy', 'alembic',
    'asyncmy', 'redis', 'jose', 'passlib'
]

print("📦 关键包检查:")
for package in packages:
    try:
        module = __import__(package)
        version = getattr(module, '__version__', 'unknown')
        print(f"  ✅ {package}: {version}")
    except ImportError:
        print(f"  ❌ {package}: 未安装")

# 3. 检查环境变量
print("\n🔧 环境变量检查:")
env_vars = [
    'MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_USER', 'MYSQL_DATABASE',
    'REDIS_URL', 'SECRET_KEY', 'OPENAI_API_KEY'
]

from dotenv import load_dotenv
load_dotenv()

for var in env_vars:
    value = os.getenv(var)
    if value:
        # 隐藏敏感信息
        if 'PASSWORD' in var or 'KEY' in var:
            print(f"  ✅ {var}: ***已设置***")
        else:
            print(f"  ✅ {var}: {value}")
    else:
        print(f"  ❌ {var}: 未设置")

print("\n✨ 诊断完成")
```

运行诊断：
```bash
python scripts/diagnose.py
```

---

## 联系支持

如果以上方案都无法解决问题，请提供以下信息：

1. **错误完整堆栈**
2. **Python版本**: `python --version`
3. **操作系统**: Windows/Linux/macOS
4. **已安装的包**: `pip list`
5. **.env配置**（隐藏敏感信息）

---

**最后更新**: 2025-12-10

