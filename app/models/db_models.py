"""
数据库模型定义
使用SQLAlchemy ORM定义所有数据库表
"""
from sqlalchemy import (
    Column, String, Integer, BigInteger, Boolean, Text,
    TIMESTAMP, Enum, ForeignKey, Index, JSON
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# ==================== 枚举类型 ====================

class UserRole(str, enum.Enum):
    """用户角色枚举"""
    STUDENT = "student"
    RESEARCHER = "researcher"
    TEACHER = "teacher"


class ExpertiseLevel(str, enum.Enum):
    """专业水平枚举"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# ==================== 用户相关表 ====================

class User(Base):
    """
    用户表
    存储用户基本信息和认证信息
    """
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True, comment="用户ID")
    username = Column(String(100), nullable=False, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    
    # 状态字段
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    is_verified = Column(Boolean, default=False, nullable=False, comment="邮箱是否验证")
    
    # 安全字段
    failed_login_attempts = Column(Integer, default=0, nullable=False, comment="登录失败次数")
    locked_until = Column(TIMESTAMP, nullable=True, comment="账户锁定到期时间")
    
    # 时间字段
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="创建时间"
    )
    last_login = Column(TIMESTAMP, nullable=True, comment="最后登录时间")
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        comment="更新时间"
    )
    
    # 关系
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    reading_histories = relationship("ReadingHistory", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_created_at', 'created_at'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"


class UserProfile(Base):
    """
    用户画像表
    存储用户的研究方向、兴趣等个性化信息
    """
    __tablename__ = "user_profiles"

    user_id = Column(
        String(50),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="用户ID"
    )
    research_direction = Column(Text, nullable=True, comment="研究方向")
    interests = Column(JSON, nullable=True, comment="兴趣标签（JSON格式）")
    expertise_level = Column(
        Enum(ExpertiseLevel),
        default=ExpertiseLevel.BEGINNER,
        nullable=True,
        comment="专业水平"
    )
    
    # 统计字段
    reading_count = Column(Integer, default=0, nullable=False, comment="阅读论文数量")
    chat_count = Column(Integer, default=0, nullable=False, comment="聊天次数")
    
    # 时间字段
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        comment="更新时间"
    )
    
    # 关系
    user = relationship("User", back_populates="profile")
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, direction={self.research_direction})>"


# ==================== 聊天历史表 ====================

class ChatHistory(Base):
    """
    聊天历史表
    存储用户与AI助手的对话记录
    """
    __tablename__ = "chat_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(
        String(50),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    session_id = Column(String(100), nullable=True, index=True, comment="会话ID")
    
    # 对话内容
    message = Column(Text, nullable=False, comment="用户消息")
    response = Column(Text, nullable=False, comment="AI回复")
    
    # 元数据
    tools_used = Column(JSON, nullable=True, comment="使用的工具列表")
    citations = Column(JSON, nullable=True, comment="引用来源")
    confidence = Column(Integer, nullable=True, comment="置信度(0-100)")
    
    # 时间字段
    timestamp = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        index=True,
        comment="时间戳"
    )
    
    # 关系
    user = relationship("User", back_populates="chat_histories")
    
    # 索引
    __table_args__ = (
        Index('idx_user_time', 'user_id', 'timestamp'),
        Index('idx_session', 'session_id'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, user_id={self.user_id}, session={self.session_id})>"


# ==================== 阅读历史表 ====================

class ReadingHistory(Base):
    """
    阅读历史表
    记录用户阅读论文的历史
    """
    __tablename__ = "reading_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(
        String(50),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    paper_id = Column(String(100), nullable=False, index=True, comment="论文ID（对应图谱中的节点）")
    
    # 阅读信息
    duration_seconds = Column(Integer, default=0, nullable=False, comment="阅读时长（秒）")
    completed = Column(Boolean, default=False, nullable=False, comment="是否读完")
    rating = Column(Integer, nullable=True, comment="评分(1-5)")
    notes = Column(Text, nullable=True, comment="笔记")
    
    # 时间字段
    read_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        index=True,
        comment="阅读时间"
    )
    
    # 关系
    user = relationship("User", back_populates="reading_histories")
    
    # 索引
    __table_args__ = (
        Index('idx_user_read', 'user_id', 'read_at'),
        Index('idx_paper', 'paper_id'),
        Index('idx_user_paper', 'user_id', 'paper_id'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<ReadingHistory(id={self.id}, user_id={self.user_id}, paper_id={self.paper_id})>"


# ==================== 论文元数据缓存表 ====================

class PaperMetadata(Base):
    """
    论文元数据缓存表
    缓存从图谱中频繁查询的论文元数据
    """
    __tablename__ = "paper_metadata"

    paper_id = Column(String(100), primary_key=True, comment="论文ID（对应图谱节点UUID）")
    
    # 基本信息
    title = Column(String(500), nullable=False, comment="论文标题")
    authors = Column(JSON, nullable=True, comment="作者列表")
    abstract = Column(Text, nullable=True, comment="摘要")
    
    # 发表信息
    year = Column(Integer, nullable=True, index=True, comment="发表年份")
    venue = Column(String(200), nullable=True, index=True, comment="会议/期刊")
    arxiv_id = Column(String(50), nullable=True, unique=True, comment="arXiv ID")
    doi = Column(String(100), nullable=True, unique=True, comment="DOI")
    
    # 统计信息
    citations_count = Column(Integer, default=0, nullable=False, comment="引用数")
    read_count = Column(Integer, default=0, nullable=False, comment="阅读次数")
    
    # PDF信息
    pdf_path = Column(String(500), nullable=True, comment="PDF存储路径")
    pdf_url = Column(String(500), nullable=True, comment="PDF在线URL")
    
    # 时间字段
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        comment="更新时间"
    )
    
    # 索引
    __table_args__ = (
        Index('idx_year', 'year'),
        Index('idx_venue', 'venue'),
        Index('idx_title', 'title', mysql_length=255),  # 全文索引需要指定长度
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<PaperMetadata(paper_id={self.paper_id}, title={self.title[:50]})>"


# ==================== 任务状态表 ====================

class TaskStatus(Base):
    """
    异步任务状态表
    用于追踪Celery任务的执行状态
    """
    __tablename__ = "task_status"

    task_id = Column(String(100), primary_key=True, comment="Celery任务ID")
    user_id = Column(
        String(50),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    # 任务信息
    task_type = Column(String(50), nullable=False, index=True, comment="任务类型")
    task_name = Column(String(200), nullable=False, comment="任务名称")
    status = Column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
        comment="任务状态(pending/running/success/failed)"
    )
    
    # 任务参数和结果
    params = Column(JSON, nullable=True, comment="任务参数")
    result = Column(JSON, nullable=True, comment="任务结果")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 进度信息
    progress = Column(Integer, default=0, nullable=False, comment="进度(0-100)")
    
    # 时间字段
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="创建时间"
    )
    started_at = Column(TIMESTAMP, nullable=True, comment="开始时间")
    completed_at = Column(TIMESTAMP, nullable=True, comment="完成时间")
    
    # 索引
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_task_type', 'task_type'),
        Index('idx_created', 'created_at'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<TaskStatus(task_id={self.task_id}, type={self.task_type}, status={self.status})>"


# ==================== 用户反馈表 ====================

class UserFeedback(Base):
    """
    用户反馈表
    收集用户对系统的反馈和评价
    """
    __tablename__ = "user_feedback"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(
        String(50),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="用户ID"
    )
    
    # 反馈内容
    feedback_type = Column(
        String(20),
        nullable=False,
        index=True,
        comment="反馈类型(bug/feature/improvement/other)"
    )
    content = Column(Text, nullable=False, comment="反馈内容")
    rating = Column(Integer, nullable=True, comment="评分(1-5)")
    
    # 关联信息
    related_chat_id = Column(BigInteger, nullable=True, comment="关联的聊天记录ID")
    related_paper_id = Column(String(100), nullable=True, comment="关联的论文ID")
    
    # 处理状态
    status = Column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
        comment="处理状态(pending/reviewing/resolved/closed)"
    )
    admin_reply = Column(Text, nullable=True, comment="管理员回复")
    
    # 时间字段
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        index=True,
        comment="创建时间"
    )
    resolved_at = Column(TIMESTAMP, nullable=True, comment="解决时间")
    
    # 索引
    __table_args__ = (
        Index('idx_user_feedback', 'user_id', 'created_at'),
        Index('idx_type_status', 'feedback_type', 'status'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<UserFeedback(id={self.id}, type={self.feedback_type}, status={self.status})>"

