-- ============================================================
-- MySQL数据库初始化脚本
-- 项目：学术研究知识图谱系统
-- 版本：v1.0
-- 创建日期：2025-12-11
-- ============================================================

-- 1. 创建数据库
-- ============================================================
CREATE DATABASE IF NOT EXISTS knowledge_graph_system
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE knowledge_graph_system;

-- 2. 删除旧表（如果存在）
-- ============================================================
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS papers;
DROP TABLE IF EXISTS research_sessions;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- 3. 创建表
-- ============================================================

-- 3.1 用户表
-- ------------------------------------------------------------
CREATE TABLE users (
    -- 主键
    id VARCHAR(36) PRIMARY KEY COMMENT '用户UUID',
    
    -- 认证信息
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名，唯一',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希（bcrypt）',
    email VARCHAR(255) DEFAULT NULL COMMENT '邮箱地址',
    
    -- 用户偏好
    preferences JSON DEFAULT NULL COMMENT '用户偏好设置（JSON格式）',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    last_login_at TIMESTAMP NULL DEFAULT NULL COMMENT '最后登录时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 3.2 研究会话表
-- ------------------------------------------------------------
CREATE TABLE research_sessions (
    -- 主键
    id VARCHAR(36) PRIMARY KEY COMMENT '会话UUID',
    
    -- 关联
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    
    -- 会话信息
    title VARCHAR(255) NOT NULL COMMENT '会话标题',
    domains JSON NOT NULL COMMENT '研究领域数组，如["AI","SE"]',
    description TEXT DEFAULT NULL COMMENT '会话描述',
    
    -- 统计信息（冗余字段，用于快速查询）
    message_count INT DEFAULT 0 COMMENT '消息数量',
    last_message_at TIMESTAMP NULL DEFAULT NULL COMMENT '最后消息时间',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at),
    INDEX idx_user_updated (user_id, updated_at),
    
    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='研究会话表';

-- 3.3 聊天消息表
-- ------------------------------------------------------------
CREATE TABLE chat_messages (
    -- 主键
    id VARCHAR(36) PRIMARY KEY COMMENT '消息UUID',
    
    -- 关联
    session_id VARCHAR(36) NOT NULL COMMENT '会话ID',
    
    -- 消息信息
    role ENUM('user', 'agent') NOT NULL COMMENT '角色：user用户 / agent助手',
    content TEXT NOT NULL COMMENT '消息内容',
    
    -- Context信息（仅Agent消息有值）
    context_string TEXT DEFAULT NULL COMMENT '格式化的context文本，前端直接展示',
    context_data JSON DEFAULT NULL COMMENT '结构化context数据',
    
    -- 附加信息
    attached_papers JSON DEFAULT NULL COMMENT '附带的论文ID列表',
    metadata JSON DEFAULT NULL COMMENT '元数据：tokens、响应时间等',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 索引
    INDEX idx_session_id (session_id),
    INDEX idx_session_time (session_id, created_at),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at),
    
    -- 外键
    FOREIGN KEY (session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天消息表';

-- 3.4 论文表
-- ------------------------------------------------------------
CREATE TABLE papers (
    -- 主键
    id VARCHAR(36) PRIMARY KEY COMMENT '论文UUID',
    
    -- 关联
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    
    -- 文件信息
    filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '磁盘存储路径',
    file_size BIGINT NOT NULL COMMENT '文件大小（字节）',
    domain VARCHAR(50) DEFAULT NULL COMMENT '论文领域',
    
    -- 解析状态
    status ENUM('uploaded', 'parsing', 'parsed', 'failed') DEFAULT 'uploaded' COMMENT '解析状态',
    parsed_content JSON DEFAULT NULL COMMENT '解析后的内容（JSON格式）',
    parse_error TEXT DEFAULT NULL COMMENT '解析失败原因',
    parse_progress INT DEFAULT 0 COMMENT '解析进度（0-100）',
    parsed_at TIMESTAMP NULL DEFAULT NULL COMMENT '解析完成时间',
    
    -- 图谱状态
    added_to_graph BOOLEAN DEFAULT FALSE COMMENT '是否已添加到图谱',
    graph_episode_ids JSON DEFAULT NULL COMMENT '添加到图谱的Episode UUID列表',
    added_to_graph_at TIMESTAMP NULL DEFAULT NULL COMMENT '添加到图谱的时间',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_domain (domain),
    INDEX idx_added_to_graph (added_to_graph),
    INDEX idx_created_at (created_at),
    INDEX idx_user_status (user_id, status),
    
    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='论文表';

-- 4. 创建触发器（可选）
-- ============================================================

DELIMITER $$

-- 4.1 插入消息时更新会话统计
CREATE TRIGGER trg_chat_messages_insert
AFTER INSERT ON chat_messages
FOR EACH ROW
BEGIN
    UPDATE research_sessions
    SET 
        message_count = message_count + 1,
        last_message_at = NEW.created_at,
        updated_at = NEW.created_at
    WHERE id = NEW.session_id;
END$$

-- 4.2 删除消息时更新会话统计
CREATE TRIGGER trg_chat_messages_delete
AFTER DELETE ON chat_messages
FOR EACH ROW
BEGIN
    UPDATE research_sessions
    SET 
        message_count = GREATEST(0, message_count - 1),
        updated_at = NOW()
    WHERE id = OLD.session_id;
END$$

DELIMITER ;

-- 5. 插入测试数据（可选）
-- ============================================================

-- 插入测试用户
-- INSERT INTO users (id, username, password_hash, email) VALUES
-- ('550e8400-e29b-41d4-a716-446655440000', 'test_user', '$2b$12$...', 'test@example.com');

-- 6. 验证
-- ============================================================

SHOW TABLES;

SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    AVG_ROW_LENGTH,
    DATA_LENGTH,
    INDEX_LENGTH,
    TABLE_COMMENT
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'knowledge_graph_system'
ORDER BY TABLE_NAME;

-- 查看索引
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as COLUMNS,
    INDEX_TYPE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'knowledge_graph_system'
GROUP BY TABLE_NAME, INDEX_NAME, INDEX_TYPE
ORDER BY TABLE_NAME, INDEX_NAME;

-- 查看外键
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'knowledge_graph_system'
AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME;

-- ============================================================
-- 初始化完成
-- ============================================================
SELECT '数据库初始化完成！' as status;

