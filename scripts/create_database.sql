-- ========================================
-- AI Research Agent - 数据库创建脚本
-- ========================================
-- MySQL 8.0+
-- 字符集: utf8mb4
-- 排序规则: utf8mb4_unicode_ci
-- ========================================

-- 创建数据库
DROP DATABASE IF EXISTS research_agent;
CREATE DATABASE research_agent 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE research_agent;

-- ========================================
-- 1. 用户表 (users)
-- ========================================
CREATE TABLE users (
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    user_role ENUM('student', 'researcher', 'teacher') NOT NULL DEFAULT 'student' COMMENT '用户角色',
    
    -- 状态字段
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    is_verified BOOLEAN NOT NULL DEFAULT FALSE COMMENT '邮箱是否验证',
    
    -- 安全字段
    failed_login_attempts INT NOT NULL DEFAULT 0 COMMENT '登录失败次数',
    locked_until TIMESTAMP NULL DEFAULT NULL COMMENT '账户锁定到期时间',
    
    -- 时间字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_login TIMESTAMP NULL DEFAULT NULL COMMENT '最后登录时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 主键
    PRIMARY KEY (user_id),
    
    -- 唯一索引
    UNIQUE KEY uk_email (email),
    
    -- 普通索引
    INDEX idx_email (email),
    INDEX idx_created_at (created_at),
    INDEX idx_user_role (user_role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ========================================
-- 2. 用户画像表 (user_profiles)
-- ========================================
CREATE TABLE user_profiles (
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    research_direction TEXT NULL COMMENT '研究方向',
    interests JSON NULL COMMENT '兴趣标签（JSON格式）',
    expertise_level ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'beginner' COMMENT '专业水平',
    
    -- 统计字段
    reading_count INT NOT NULL DEFAULT 0 COMMENT '阅读论文数量',
    chat_count INT NOT NULL DEFAULT 0 COMMENT '聊天次数',
    
    -- 时间字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 主键
    PRIMARY KEY (user_id),
    
    -- 外键
    CONSTRAINT fk_user_profiles_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户画像表';

-- ========================================
-- 3. 聊天历史表 (chat_history)
-- ========================================
CREATE TABLE chat_history (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    session_id VARCHAR(100) NULL COMMENT '会话ID',
    
    -- 对话内容
    message TEXT NOT NULL COMMENT '用户消息',
    response TEXT NOT NULL COMMENT 'AI回复',
    
    -- 元数据
    tools_used JSON NULL COMMENT '使用的工具列表',
    citations JSON NULL COMMENT '引用来源',
    confidence INT NULL COMMENT '置信度(0-100)',
    
    -- 时间字段
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '时间戳',
    
    -- 主键
    PRIMARY KEY (id),
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_time (user_id, timestamp),
    
    -- 外键
    CONSTRAINT fk_chat_history_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天历史表';

-- ========================================
-- 4. 阅读历史表 (reading_history)
-- ========================================
CREATE TABLE reading_history (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    paper_id VARCHAR(100) NOT NULL COMMENT '论文ID（对应图谱中的节点）',
    
    -- 阅读信息
    duration_seconds INT NOT NULL DEFAULT 0 COMMENT '阅读时长（秒）',
    completed BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否读完',
    rating INT NULL COMMENT '评分(1-5)',
    notes TEXT NULL COMMENT '笔记',
    
    -- 时间字段
    read_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '阅读时间',
    
    -- 主键
    PRIMARY KEY (id),
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_paper_id (paper_id),
    INDEX idx_read_at (read_at),
    INDEX idx_user_read (user_id, read_at),
    INDEX idx_user_paper (user_id, paper_id),
    
    -- 外键
    CONSTRAINT fk_reading_history_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='阅读历史表';

-- ========================================
-- 5. 论文元数据缓存表 (paper_metadata)
-- ========================================
CREATE TABLE paper_metadata (
    paper_id VARCHAR(100) NOT NULL COMMENT '论文ID（对应图谱节点UUID）',
    
    -- 基本信息
    title VARCHAR(500) NOT NULL COMMENT '论文标题',
    authors JSON NULL COMMENT '作者列表',
    abstract TEXT NULL COMMENT '摘要',
    
    -- 发表信息
    year INT NULL COMMENT '发表年份',
    venue VARCHAR(200) NULL COMMENT '会议/期刊',
    arxiv_id VARCHAR(50) NULL COMMENT 'arXiv ID',
    doi VARCHAR(100) NULL COMMENT 'DOI',
    
    -- 统计信息
    citations_count INT NOT NULL DEFAULT 0 COMMENT '引用数',
    read_count INT NOT NULL DEFAULT 0 COMMENT '阅读次数',
    
    -- PDF信息
    pdf_path VARCHAR(500) NULL COMMENT 'PDF存储路径',
    pdf_url VARCHAR(500) NULL COMMENT 'PDF在线URL',
    
    -- 时间字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 主键
    PRIMARY KEY (paper_id),
    
    -- 唯一索引
    UNIQUE KEY uk_arxiv_id (arxiv_id),
    UNIQUE KEY uk_doi (doi),
    
    -- 普通索引
    INDEX idx_year (year),
    INDEX idx_venue (venue),
    INDEX idx_title (title(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='论文元数据缓存表';

-- ========================================
-- 6. 任务状态表 (task_status)
-- ========================================
CREATE TABLE task_status (
    task_id VARCHAR(100) NOT NULL COMMENT 'Celery任务ID',
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    
    -- 任务信息
    task_type VARCHAR(50) NOT NULL COMMENT '任务类型',
    task_name VARCHAR(200) NOT NULL COMMENT '任务名称',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '任务状态(pending/running/success/failed)',
    
    -- 任务参数和结果
    params JSON NULL COMMENT '任务参数',
    result JSON NULL COMMENT '任务结果',
    error_message TEXT NULL COMMENT '错误信息',
    
    -- 进度信息
    progress INT NOT NULL DEFAULT 0 COMMENT '进度(0-100)',
    
    -- 时间字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    started_at TIMESTAMP NULL COMMENT '开始时间',
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    
    -- 主键
    PRIMARY KEY (task_id),
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_task_type (task_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_user_status (user_id, status),
    
    -- 外键
    CONSTRAINT fk_task_status_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务状态表';

-- ========================================
-- 7. 用户反馈表 (user_feedback)
-- ========================================
CREATE TABLE user_feedback (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id VARCHAR(50) NULL COMMENT '用户ID',
    
    -- 反馈内容
    feedback_type VARCHAR(20) NOT NULL COMMENT '反馈类型(bug/feature/improvement/other)',
    content TEXT NOT NULL COMMENT '反馈内容',
    rating INT NULL COMMENT '评分(1-5)',
    
    -- 关联信息
    related_chat_id BIGINT NULL COMMENT '关联的聊天记录ID',
    related_paper_id VARCHAR(100) NULL COMMENT '关联的论文ID',
    
    -- 处理状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '处理状态(pending/reviewing/resolved/closed)',
    admin_reply TEXT NULL COMMENT '管理员回复',
    
    -- 时间字段
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    resolved_at TIMESTAMP NULL COMMENT '解决时间',
    
    -- 主键
    PRIMARY KEY (id),
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_feedback_type (feedback_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_user_feedback (user_id, created_at),
    INDEX idx_type_status (feedback_type, status),
    
    -- 外键（允许匿名反馈，所以用SET NULL）
    CONSTRAINT fk_user_feedback_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户反馈表';

-- ========================================
-- 插入测试数据（可选）
-- ========================================

-- 插入测试用户
-- 注意：密码为 Test1234! 的bcrypt哈希值
INSERT INTO users (user_id, username, email, password_hash, user_role, is_active, is_verified)
VALUES 
    ('u_test_001', 'TestUser1', 'test1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpCqU3bPDdJm', 'student', TRUE, TRUE),
    ('u_test_002', 'Researcher1', 'researcher@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpCqU3bPDdJm', 'researcher', TRUE, TRUE),
    ('u_test_003', 'Teacher1', 'teacher@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpCqU3bPDdJm', 'teacher', TRUE, TRUE);

-- 插入测试用户画像
INSERT INTO user_profiles (user_id, research_direction, interests, expertise_level)
VALUES 
    ('u_test_001', 'Deep Learning', '["Machine Learning", "Computer Vision", "NLP"]', 'beginner'),
    ('u_test_002', 'Reinforcement Learning', '["Deep Learning", "RL", "Robotics"]', 'intermediate'),
    ('u_test_003', 'Knowledge Graph', '["Knowledge Graph", "GNN", "Recommendation"]', 'expert');

-- ========================================
-- 查看创建的表
-- ========================================
SHOW TABLES;

-- 查看表结构示例
-- DESCRIBE users;
-- DESCRIBE user_profiles;
-- DESCRIBE chat_history;

-- ========================================
-- 数据库统计信息
-- ========================================
SELECT
    TABLE_NAME AS '表名',
    TABLE_ROWS AS '行数',
    ROUND(DATA_LENGTH / 1024 / 1024, 2) AS '数据大小(MB)',
    ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS '索引大小(MB)',
    TABLE_COMMENT AS '备注'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'research_agent'
ORDER BY TABLE_NAME;

-- ========================================
-- 完成
-- ========================================
SELECT '✅ 数据库创建完成！' AS message;
SELECT '📊 共创建了 7 个表' AS info;
SELECT '👤 插入了 3 个测试用户' AS test_data;

