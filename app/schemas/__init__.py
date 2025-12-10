"""
Pydantic模型模块
用于API请求和响应的数据验证
"""

# 认证相关
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    UserInfo,
    UserMeResponse,
    TokenPayload,
    MessageResponse,
)

# 聊天相关
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

# 论文相关
from app.schemas.paper import (
    PaperMetadata,
)

# 用户相关
from app.schemas.user import (
    UserProfile,
    UserInterest,
)

# 历史相关
from app.schemas.history import (
    ChatMessage,
    ChatHistory,
)

# 图谱相关
from app.schemas.graph import (
    GraphSearchRequest,
    GraphSearchResponse,
)

# 社区相关
from app.schemas.community import (
    Community,
    CommunityNode,
)

# 推荐相关
from app.schemas.recommendation import (
    PaperRecommendation,
    DirectionRecommendation,
)

# 图谱实体和关系
from app.schemas.entities import (
    PaperEntity,
    MethodEntity,
    DatasetEntity,
    TaskEntity,
    MetricEntity,
    AuthorEntity,
    InstitutionEntity,
    ConceptEntity,
)

from app.schemas.relations import (
    RelationType,
)

__all__ = [
    # Auth
    "RegisterRequest",
    "RegisterResponse",
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "ChangePasswordRequest",
    "ChangePasswordResponse",
    "UserInfo",
    "UserMeResponse",
    "TokenPayload",
    "MessageResponse",
    
    # Chat
    "ChatRequest",
    "ChatResponse",
    
    # Paper
    "PaperMetadata",
    
    # User
    "UserProfile",
    "UserInterest",
    
    # History
    "ChatMessage",
    "ChatHistory",
    
    # Graph
    "GraphSearchRequest",
    "GraphSearchResponse",
    
    # Community
    "Community",
    "CommunityNode",
    
    # Recommendation
    "PaperRecommendation",
    "DirectionRecommendation",
    
    # Entities
    "PaperEntity",
    "MethodEntity",
    "DatasetEntity",
    "TaskEntity",
    "MetricEntity",
    "AuthorEntity",
    "InstitutionEntity",
    "ConceptEntity",
    
    # Relations
    "RelationType",
]
