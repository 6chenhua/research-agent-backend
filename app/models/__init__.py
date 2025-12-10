"""
数据库模型模块
只包含SQLAlchemy ORM模型
"""
from app.models.db_models import (
    # 用户相关
    User,
    UserProfile,
    
    # 聊天和历史
    ChatHistory,
    ReadingHistory,
    
    # 论文
    PaperMetadata,
    
    # 任务和反馈
    TaskStatus,
    UserFeedback,
    
    # 枚举
    UserRole,
    ExpertiseLevel,
)

__all__ = [
    "User",
    "UserProfile",
    "ChatHistory",
    "ReadingHistory",
    "PaperMetadata",
    "TaskStatus",
    "UserFeedback",
    "UserRole",
    "ExpertiseLevel",
]
