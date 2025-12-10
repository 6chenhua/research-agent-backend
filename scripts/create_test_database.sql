-- ========================================
-- AI Research Agent - 测试数据库创建脚本
-- ========================================
-- 用途: 专门用于运行自动化测试
-- 警告: 测试过程中此数据库会被频繁清空和重建
-- ========================================

-- 创建测试数据库
DROP DATABASE IF EXISTS test_research_agent;
CREATE DATABASE test_research_agent 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- 注意: 表结构会由 SQLAlchemy 通过 Base.metadata.create_all() 自动创建
-- 这样可以确保测试使用的表结构与代码中定义的模型完全一致

