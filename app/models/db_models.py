"""
数据库模型定义
按照数据库Schema设计文档，只包含4张核心表：
1. users - 用户表
2. research_sessions - 研究会话表
3. chat_messages - 聊天消息表
4. papers - 论文表
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

class MessageRole(str, enum.Enum):
    """消息角色枚举"""
    USER = "user"
    AGENT = "agent"


class PaperStatus(str, enum.Enum):
    """论文解析状态枚举"""
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"


# ==================== 1. 用户表 ====================

class User(Base):
    """
    用户表
    存储用户账号信息、认证凭证、偏好设置
    """
    __tablename__ = "users"

    # 主键
    user_id = Column(String(36), primary_key=True, comment="用户UUID")
    
    # 认证信息
    username = Column(String(50), unique=True, nullable=False, comment="用户名，唯一")
    password_hash = Column(String(255), nullable=False, comment="密码哈希（bcrypt）")
    email = Column(String(255), nullable=True, comment="邮箱地址")
    
    # 用户偏好
    preferences = Column(JSON, nullable=True, comment="用户偏好设置（JSON格式）")
    
    # 时间戳
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="注册时间"
    )
    last_login_at = Column(TIMESTAMP, nullable=True, comment="最后登录时间")
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        comment="更新时间"
    )
    
    # 关系
    research_sessions = relationship("ResearchSession", back_populates="user", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="user", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
        Index('idx_created_at', 'created_at'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


# ==================== 2. 研究会话表 ====================

class ResearchSession(Base):
    """
    研究会话表
    存储用户创建的研究会话，包括会话标题、研究领域等
    """
    __tablename__ = "research_sessions"

    # 主键
    id = Column(String(36), primary_key=True, comment="会话UUID")
    
    # 关联
    user_id = Column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    # 会话信息
    title = Column(String(255), nullable=False, comment="会话标题")
    domains = Column(JSON, nullable=False, comment="研究领域数组，如['AI','SE']")
    description = Column(Text, nullable=True, comment="会话描述")
    
    # 统计信息（冗余字段，用于快速查询）
    message_count = Column(Integer, default=0, nullable=False, comment="消息数量")
    last_message_at = Column(TIMESTAMP, nullable=True, comment="最后消息时间")
    
    # 时间戳
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
    user = relationship("User", back_populates="research_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_rs_user_id', 'user_id'),
        Index('idx_rs_created_at', 'created_at'),
        Index('idx_rs_updated_at', 'updated_at'),
        Index('idx_rs_user_updated', 'user_id', 'updated_at'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<ResearchSession(id={self.id}, title={self.title})>"


# ==================== 3. 聊天消息表 ====================

class ChatMessage(Base):
    """
    聊天消息表
    存储用户与Agent的对话记录，每条消息独立存储
    """
    __tablename__ = "chat_messages"

    # 主键
    id = Column(String(36), primary_key=True, comment="消息UUID")
    
    # 关联
    session_id = Column(
        String(36),
        ForeignKey("research_sessions.id", ondelete="CASCADE"),
        nullable=False,
        comment="会话ID"
    )
    
    # 消息信息
    role = Column(Enum(MessageRole), nullable=False, comment="角色：user用户 / agent助手")
    content = Column(Text, nullable=False, comment="消息内容")
    
    # Context信息（仅Agent消息有值）
    context_string = Column(Text, nullable=True, comment="格式化的context文本，前端直接展示")
    context_data = Column(JSON, nullable=True, comment="结构化context数据")
    
    # 附加信息
    attached_papers = Column(JSON, nullable=True, comment="附带的论文ID列表")
    extra_data = Column(JSON, nullable=True, comment="元数据：tokens、响应时间等")
    
    # 时间戳
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="创建时间"
    )
    
    # 关系
    session = relationship("ResearchSession", back_populates="messages")
    
    # 索引
    __table_args__ = (
        Index('idx_cm_session_id', 'session_id'),
        Index('idx_cm_session_time', 'session_id', 'created_at'),
        Index('idx_cm_role', 'role'),
        Index('idx_cm_created_at', 'created_at'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, session={self.session_id})>"


# ==================== 4. 论文表 ====================

class Paper(Base):
    """
    论文表
    存储用户上传的论文文件，包括解析状态、解析内容、图谱状态等
    """
    __tablename__ = "papers"

    # 主键
    id = Column(String(36), primary_key=True, comment="论文UUID")
    
    # 关联
    user_id = Column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    # 文件信息
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="磁盘存储路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小（字节）")
    domains = Column(JSON, nullable=True, comment="论文领域列表，如['AI','NLP']，由LLM分析abstract自动识别")
    
    # 解析状态
    status = Column(
        Enum(PaperStatus),
        server_default="uploaded",
        nullable=False,
        comment="解析状态"
    )
    parsed_content = Column(JSON, nullable=True, comment="解析后的内容（JSON格式）")
    parse_error = Column(Text, nullable=True, comment="解析失败原因")
    parse_progress = Column(Integer, default=0, nullable=False, comment="解析进度（0-100）")
    parsed_at = Column(TIMESTAMP, nullable=True, comment="解析完成时间")
    
    # 图谱状态
    added_to_graph = Column(Boolean, server_default="0", nullable=False, comment="是否已添加到图谱")
    graph_episode_ids = Column(JSON, nullable=True, comment="添加到图谱的Episode UUID列表")
    added_to_graph_at = Column(TIMESTAMP, nullable=True, comment="添加到图谱的时间")
    
    # 时间戳
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="上传时间"
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
        comment="更新时间"
    )
    
    # 关系
    user = relationship("User", back_populates="papers")
    
    # 索引
    # 注意：domains 是 JSON 类型，不支持普通索引
    __table_args__ = (
        Index('idx_papers_user_id', 'user_id'),
        Index('idx_papers_status', 'status'),
        Index('idx_papers_added_to_graph', 'added_to_graph'),
        Index('idx_papers_created_at', 'created_at'),
        Index('idx_papers_user_status', 'user_id', 'status'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )

    def __repr__(self):
        return f"<Paper(id={self.id}, filename={self.filename}, status={self.status})>"
