"""
用户模块相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


# ==================== 统计数据模型 ====================

class GraphStats(BaseModel):
    """图谱统计数据"""
    total_entities: int = Field(default=0, description="实体节点数量")
    total_episodes: int = Field(default=0, description="Episode节点数量")
    total_edges: int = Field(default=0, description="关系边数量")


class ResearchStats(BaseModel):
    """研究统计数据"""
    total_sessions: int = Field(default=0, description="研究会话数量")
    total_messages: int = Field(default=0, description="聊天消息总数")
    domains: List[str] = Field(default_factory=list, description="涉及的研究领域")


class PaperStats(BaseModel):
    """论文统计数据"""
    total_uploaded: int = Field(default=0, description="已上传论文数量")
    total_parsed: int = Field(default=0, description="已解析论文数量")
    added_to_graph: int = Field(default=0, description="已添加到图谱的论文数量")


# ==================== 用户偏好设置模型 ====================

class GraphSettings(BaseModel):
    """图谱可视化设置"""
    default_layout: str = Field(default="force", description="默认布局: force / hierarchical / circular")
    show_episodes: bool = Field(default=False, description="默认是否显示Episode节点")
    show_labels: bool = Field(default=True, description="是否显示节点标签")


class ChatSettings(BaseModel):
    """聊天设置"""
    auto_expand_context: bool = Field(default=False, description="是否默认展开context")
    message_limit: int = Field(default=50, description="每次加载的消息数")


class PaperSettings(BaseModel):
    """论文设置"""
    auto_parse: bool = Field(default=True, description="是否自动解析上传的论文")
    default_granularity: str = Field(default="section", description="添加到图谱的默认粒度")


# ==================== 用户画像模型（个性化） ====================

class InteractionStats(BaseModel):
    """交互统计"""
    total_sessions: int = Field(default=0, description="总会话数")
    total_messages: int = Field(default=0, description="总消息数")
    total_papers: int = Field(default=0, description="总论文数")
    last_active_at: Optional[str] = Field(default=None, description="最后活跃时间")


class TopicCount(BaseModel):
    """话题计数"""
    topic: str = Field(..., description="话题关键词")
    count: int = Field(default=1, description="出现次数")


class UserProfile(BaseModel):
    """
    用户画像（用于个性化）
    
    存储在 users.preferences 字段中，由系统自动分析更新。
    """
    # 研究兴趣（domain: 出现次数）
    research_interests: dict = Field(
        default_factory=dict, 
        description="研究兴趣，格式: {domain: count}"
    )
    
    # 知识水平
    expertise_level: str = Field(
        default="intermediate", 
        description="知识水平: beginner / intermediate / expert"
    )
    
    # 回复偏好
    preferred_depth: str = Field(
        default="normal", 
        description="回复深度偏好: brief / normal / detailed"
    )
    preferred_language: str = Field(
        default="zh-CN", 
        description="语言偏好: zh-CN / en-US"
    )
    
    # 常问话题
    frequently_asked_topics: List[TopicCount] = Field(
        default_factory=list, 
        description="常问话题列表"
    )
    
    # 交互统计
    interaction_stats: InteractionStats = Field(
        default_factory=InteractionStats, 
        description="交互统计数据"
    )


class UserPreferences(BaseModel):
    """用户偏好设置（包含画像和UI设置）"""
    # UI 偏好
    default_domains: List[str] = Field(default_factory=list, description="默认研究领域")
    theme: str = Field(default="light", description="主题: dark / light / auto")
    language: str = Field(default="zh-CN", description="语言: zh-CN / en-US")
    graph_settings: Optional[GraphSettings] = Field(default=None, description="图谱可视化设置")
    chat_settings: Optional[ChatSettings] = Field(default=None, description="聊天设置")
    paper_settings: Optional[PaperSettings] = Field(default=None, description="论文设置")
    
    # 个性化画像（系统自动更新）
    research_interests: dict = Field(default_factory=dict, description="研究兴趣统计")
    expertise_level: str = Field(default="intermediate", description="知识水平")
    preferred_depth: str = Field(default="normal", description="回复深度偏好")
    frequently_asked_topics: List[TopicCount] = Field(default_factory=list, description="常问话题")
    interaction_stats: Optional[InteractionStats] = Field(default=None, description="交互统计")


# ==================== 请求模型 ====================

class UpdateProfileRequest(BaseModel):
    """更新用户资料请求"""
    email: Optional[EmailStr] = Field(default=None, description="新邮箱地址")
    preferences: Optional[UserPreferences] = Field(default=None, description="用户偏好设置")


# ==================== 响应模型 ====================

class UserProfileResponse(BaseModel):
    """获取用户资料响应 - REQ-USER-1"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(default=None, description="邮箱地址")
    created_at: str = Field(..., description="注册时间 (ISO格式)")
    
    graph_stats: GraphStats = Field(default_factory=GraphStats, description="图谱统计")
    research_stats: ResearchStats = Field(default_factory=ResearchStats, description="研究统计")
    paper_stats: PaperStats = Field(default_factory=PaperStats, description="论文统计")
    
    last_login_at: Optional[str] = Field(default=None, description="最后登录时间 (ISO格式)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "researcher001",
                "email": "researcher@example.com",
                "created_at": "2025-12-01T10:00:00Z",
                "graph_stats": {
                    "total_entities": 120,
                    "total_episodes": 30,
                    "total_edges": 320
                },
                "research_stats": {
                    "total_sessions": 5,
                    "total_messages": 120,
                    "domains": ["AI", "SE", "CV"]
                },
                "paper_stats": {
                    "total_uploaded": 15,
                    "total_parsed": 12,
                    "added_to_graph": 8
                },
                "last_login_at": "2025-12-11T09:00:00Z"
            }
        }


class UpdateProfileResponse(BaseModel):
    """更新用户资料响应 - REQ-USER-2"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(default=None, description="邮箱地址")
    preferences: Optional[UserPreferences] = Field(default=None, description="用户偏好设置")
    updated_at: str = Field(..., description="更新时间 (ISO格式)")
    message: str = Field(default="Profile updated successfully", description="操作结果消息")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "researcher001",
                "email": "newemail@example.com",
                "preferences": {
                    "default_domains": ["AI", "CV"],
                    "theme": "dark",
                    "language": "zh-CN"
                },
                "updated_at": "2025-12-11T10:00:00Z",
                "message": "Profile updated successfully"
            }
        }


