# 📚 执行SQL脚本指南

## 📋 可用的SQL脚本

| 脚本文件 | 说明 | 推荐场景 |
|---------|------|---------|
| **create_database.sql** | 创建数据库+表+测试数据 | 快速开始测试 |
| **create_database_no_data.sql** | 仅创建数据库和表 | 生产环境或空库开始 |
| **insert_test_data.sql** | 仅插入测试数据 | 补充测试数据 |

---

## 🎯 方式一：使用MySQL命令行（推荐）

### Windows用户

```bash
# 1. 打开命令提示符（CMD）或PowerShell

# 2. 导航到项目目录
cd D:\My_Python_Project\graduationProject

# 3. 执行SQL脚本（选择一个）

# 方案A：创建数据库+表+测试数据（推荐用于开发）
mysql -u root -p < scripts/create_database.sql

# 方案B：仅创建数据库和表（不含测试数据）
mysql -u root -p < scripts/create_database_no_data.sql

# 如果使用方案B，可以稍后添加测试数据：
mysql -u root -p < scripts/insert_test_data.sql

# 4. 输入MySQL密码
```

### Linux/Mac用户

```bash
# 1. 打开终端

# 2. 导航到项目目录
cd /path/to/graduationProject

# 3. 执行SQL脚本
mysql -u root -p < scripts/create_database.sql

# 4. 输入MySQL密码
```

---

## 🎯 方式二：使用MySQL命令行交互模式

```bash
# 1. 登录MySQL
mysql -u root -p

# 2. 在MySQL提示符下执行
mysql> source D:/My_Python_Project/graduationProject/scripts/create_database.sql;

# 或者使用反斜杠
mysql> \. D:/My_Python_Project/graduationProject/scripts/create_database.sql

# 3. 查看结果
mysql> USE research_agent;
mysql> SHOW TABLES;
```

---

## 🎯 方式三：使用Docker（如果MySQL在容器中）

```bash
# 1. 确保MySQL容器正在运行
docker-compose ps

# 2. 将SQL文件复制到容器
docker cp scripts/create_database.sql research_agent_mysql:/tmp/

# 3. 在容器中执行SQL
docker-compose exec mysql mysql -u root -p -e "source /tmp/create_database.sql"

# 或者进入容器交互式执行
docker-compose exec mysql bash
mysql -u root -p
source /tmp/create_database.sql
```

---

## 🎯 方式四：使用MySQL Workbench（图形界面）

### 步骤：

1. **打开MySQL Workbench**

2. **连接到MySQL服务器**
   - Host: `localhost`
   - Port: `3306`
   - Username: `root`
   - Password: 你的密码

3. **打开SQL脚本**
   - 点击菜单：`File` → `Open SQL Script`
   - 选择：`scripts/create_database.sql`

4. **执行脚本**
   - 点击工具栏的 ⚡ 闪电图标
   - 或按快捷键：`Ctrl+Shift+Enter`

5. **查看结果**
   - 在左侧 `SCHEMAS` 面板刷新
   - 应该能看到 `research_agent` 数据库

---

## 🎯 方式五：使用Navicat等其他工具

### Navicat:

1. 连接到MySQL
2. 右键点击连接 → `Execute SQL File`
3. 选择 `scripts/create_database.sql`
4. 点击 `Start` 执行

### DBeaver:

1. 连接到MySQL
2. 打开SQL编辑器
3. 加载 `scripts/create_database.sql`
4. 点击 `Execute SQL Script`

---

## ✅ 验证数据库创建成功

### 方法1：命令行验证

```bash
mysql -u root -p
```

```sql
-- 查看所有数据库
SHOW DATABASES;

-- 使用数据库
USE research_agent;

-- 查看所有表
SHOW TABLES;

-- 查看表结构
DESCRIBE users;
DESCRIBE user_profiles;
DESCRIBE chat_history;

-- 查看表数据
SELECT * FROM users;
```

### 方法2：Python验证

创建测试脚本 `test_connection.py`:

```python
import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='your_password',  # 替换为你的密码
        database='research_agent',
        charset='utf8mb4'
    )
    
    with connection.cursor() as cursor:
        # 查看所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("✅ 数据库连接成功！")
        print(f"📊 共有 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 查看用户数量
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👤 共有 {user_count} 个用户")
    
    connection.close()
    
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

运行：
```bash
python test_connection.py
```

---

## 📋 预期结果

执行成功后，应该看到：

```
✅ 数据库创建完成！
📊 共创建了 7 个表
👤 插入了 3 个测试用户
```

**创建的表：**
1. `users` - 用户表
2. `user_profiles` - 用户画像表
3. `chat_history` - 聊天历史表
4. `reading_history` - 阅读历史表
5. `paper_metadata` - 论文元数据表
6. `task_status` - 任务状态表
7. `user_feedback` - 用户反馈表

**测试用户：**
- 📧 test1@example.com (密码: Test1234!) - 学生
- 📧 researcher@example.com (密码: Test1234!) - 研究员
- 📧 teacher@example.com (密码: Test1234!) - 教师

---

## 🔄 重新创建数据库

如果需要重新创建（删除旧数据）：

```bash
# 直接执行create_database.sql即可，脚本开头有DROP DATABASE
mysql -u root -p < scripts/create_database.sql
```

或者手动删除：

```sql
DROP DATABASE IF EXISTS research_agent;
```

然后重新执行创建脚本。

---

## ⚠️ 常见问题

### 1. 权限不足

**错误**: `ERROR 1044 (42000): Access denied`

**解决**:
```sql
-- 使用root用户登录
mysql -u root -p

-- 授予权限
GRANT ALL PRIVILEGES ON research_agent.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. 数据库已存在

**错误**: `ERROR 1007 (HY000): Can't create database 'research_agent'; database exists`

**解决**: 脚本开头已经包含 `DROP DATABASE IF EXISTS`，应该不会出现此问题。如果仍然出现，手动删除：

```sql
DROP DATABASE research_agent;
```

### 3. 字符集问题

**错误**: 乱码或字符集错误

**解决**: 确保连接时指定字符集：

```sql
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
```

### 4. 外键约束失败

**错误**: `ERROR 1452 (23000): Cannot add or update a child row`

**解决**: 按顺序创建表（脚本已正确排序），先创建父表（users），再创建子表。

---

## 📝 下一步

数据库创建成功后：

1. **更新.env文件**
   ```bash
   MYSQL_DATABASE=research_agent
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   ```

2. **测试应用连接**
   ```bash
   # 启动应用
   uvicorn main:app --reload
   
   # 访问
   http://localhost:8000/docs
   ```

3. **注册测试用户**
   - 使用Swagger UI
   - 或使用已有测试用户登录

---

## 🆘 获取帮助

如果遇到问题：

1. 查看MySQL错误日志
2. 检查MySQL服务是否运行
3. 验证用户权限
4. 确认端口未被占用

**查看MySQL状态**:
```bash
# Windows
net start mysql

# Linux/Mac
sudo systemctl status mysql
```

---

**创建时间**: 2025-12-09  
**适用版本**: MySQL 8.0+

