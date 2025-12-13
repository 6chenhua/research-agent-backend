"""
聊天与研究会话相关的Pydantic模型
根据PRD_研究与聊天模块.md设计
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ==================== 研究会话 Schemas ====================

class CreateResearchRequest(BaseModel):
    """创建研究会话请求 - REQ-CHAT-1"""
    title: Optional[str] = Field(None, description="会话标题，默认生成")
    domains: List[str] = Field(..., min_length=1, description="研究领域（至少1个）")
    description: Optional[str] = Field(None, description="研究描述")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "AI研究",
                "domains": ["AI", "SE"],
                "description": "研究Agent Memory相关技术"
            }
        }


class CreateResearchResponse(BaseModel):
    """创建研究会话响应 - REQ-CHAT-1"""
    session_id: str = Field(..., description="会话UUID")
    title: str = Field(..., description="会话标题")
    domains: List[str] = Field(..., description="研究领域")
    created_at: str = Field(..., description="创建时间ISO格式")
    message: str = Field(default="Research session created successfully")
    community_build_triggered: bool = Field(default=True, description="是否触发社区构建")


class ResearchSessionInfo(BaseModel):
    """研究会话信息"""
    session_id: str
    title: str
    domains: List[str]
    message_count: int = 0
    last_message_at: Optional[str] = None
    created_at: str


class ResearchSessionListResponse(BaseModel):
    """获取研究会话列表响应 - REQ-CHAT-2"""
    sessions: List[ResearchSessionInfo]
    pagination: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total": 0,
            "limit": 20,
            "offset": 0,
            "has_more": False
        }
    )


# ==================== 聊天消息 Schemas ====================

class ChatSendRequest(BaseModel):
    """发送消息请求 - REQ-CHAT-3"""
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., min_length=1, description="用户消息")
    attached_papers: Optional[List[str]] = Field(default=[], description="附带的论文ID列表")
    stream: bool = Field(default=False, description="是否流式响应（暂不实现）")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "message": "agent memory的SOTA是什么技术？",
                "attached_papers": [],
                "stream": False
            }
        }


class UserMessageInfo(BaseModel):
    """用户消息信息"""
    message_id: str
    role: str = "user"
    content: str
    attached_papers: List[str] = []
    created_at: str


class SearchResultItem(BaseModel):
    """搜索结果项"""
    type: str = Field(..., description="类型：entity/relation/community")
    uuid: str = Field(..., description="节点UUID")
    name: str = Field(..., description="节点名称")
    snippet: str = Field(..., description="内容摘要")
    relevance_score: float = Field(..., description="相关性分数")
    source: str = Field(default="Your research notes", description="来源")


class ContextData(BaseModel):
    """Context结构化数据"""
    source: str = Field(..., description="来源：graph/paper")
    search_results: List[SearchResultItem] = []
    search_stats: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total_searched": 0,
            "total_returned": 0,
            "search_time_ms": 0
        }
    )


class AgentMessageInfo(BaseModel):
    """Agent消息信息"""
    message_id: str
    role: str = "agent"
    content: str
    context_string: Optional[str] = None
    context_data: Optional[ContextData] = None
    created_at: str


class ChatSendStatus(BaseModel):
    """发送消息状态"""
    graph_updated: bool = True
    papers_parsed: List[str] = []
    community_updated: bool = False


class ChatSendResponse(BaseModel):
    """发送消息响应 - REQ-CHAT-3"""
    user_message: UserMessageInfo
    agent_message: AgentMessageInfo
    status: ChatSendStatus


# ==================== 聊天历史 Schemas ====================

class ChatMessageInfo(BaseModel):
    """聊天消息详情"""
    message_id: str
    role: str
    content: str
    attached_papers: Optional[List[str]] = None
    context_string: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    created_at: str


class SessionInfoBrief(BaseModel):
    """会话简要信息"""
    title: str
    domains: List[str]
    created_at: str


class ChatHistoryResponse(BaseModel):
    """获取聊天历史响应 - REQ-CHAT-4"""
    session_id: str
    session_info: SessionInfoBrief
    messages: List[ChatMessageInfo]
    pagination: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total": 0,
            "limit": 50,
            "offset": 0,
            "has_more": False
        }
    )


# ==================== 错误响应 ====================

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str
