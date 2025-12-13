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
    LoginUserInfo,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    LogoutResponse,
    ErrorResponse,
    TokenPayload,
)

# 聊天相关
from app.schemas.chat import (
    ChatSendResponse,
    ChatHistoryResponse,
    ChatSendRequest,
    CreateResearchResponse,
    ChatMessageInfo,
    ChatSendStatus,
    CreateResearchRequest,
    ContextData,
    ResearchSessionListResponse,
    ResearchSessionInfo,
    SearchResultItem,
)

# 论文相关
from app.schemas.paper import (
    PaperMetadata,
)

# 用户相关
from app.schemas.user import (
    GraphStats,
    ResearchStats,
    PaperStats,
    UserPreferences,
    UpdateProfileRequest,
    UserProfileResponse,
    UpdateProfileResponse,
)

# 历史相关
from app.schemas.history import (
    ChatMessage,
    ChatHistory,
)

# 图谱相关 (PRD_图谱模块.md)
from app.schemas.graph import (
    GraphNode,
    GraphEdge,
    GraphStats as GraphStatsDetail,
    UserGraphResponse,
    NodeDetailResponse,
    EdgeDetailResponse,
    GraphStatsResponse,
    GraphErrorResponse,
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
    "LoginUserInfo",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "ChangePasswordRequest",
    "ChangePasswordResponse",
    "LogoutResponse",
    "ErrorResponse",
    "TokenPayload",
    
    # Chat
    "ChatSendResponse",
    "ChatHistoryResponse",
    "ChatSendRequest",
    "CreateResearchResponse",
    "ChatMessageInfo",
    "ChatSendStatus",
    "CreateResearchRequest",
    "ContextData",
    "ResearchSessionListResponse",
    "ResearchSessionInfo",
    "SearchResultItem",
    
    # Paper
    "PaperMetadata",
    
    # User
    "GraphStats",
    "ResearchStats",
    "PaperStats",
    "UserPreferences",
    "UpdateProfileRequest",
    "UserProfileResponse",
    "UpdateProfileResponse",
    
    # History
    "ChatMessage",
    "ChatHistory",
    
    # Graph (PRD_图谱模块.md)
    "GraphNode",
    "GraphEdge",
    "GraphStatsDetail",
    "UserGraphResponse",
    "NodeDetailResponse",
    "EdgeDetailResponse",
    "GraphStatsResponse",
    "GraphErrorResponse",
    
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
