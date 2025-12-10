-- MySQL初始化脚本
-- 此脚本在Docker容器首次启动时自动执行

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS research_agent 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE research_agent;

-- 创建应用用户（如果不存在）
-- 注意：Docker环境变量已经创建了用户，这里只是确保权限正确

-- 授予权限
GRANT ALL PRIVILEGES ON research_agent.* TO 'research_user'@'%';
FLUSH PRIVILEGES;

-- 显示成功信息
SELECT 'MySQL初始化完成！' AS message;

