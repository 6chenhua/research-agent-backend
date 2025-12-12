"""
图谱模块 Pydantic Schema
根据 PRD_图谱模块.md 设计

实现需求：
- REQ-GRAPH-1: 获取用户图谱
- REQ-GRAPH-2: 获取节点详情
- REQ-GRAPH-3: 获取边详情
- REQ-GRAPH-4: 图谱统计信息
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


# ==================== REQ-GRAPH-1: 获取用户图谱 ====================

class GraphNode(BaseModel):
    """图谱节点（简化版）
    
    用于图谱可视化渲染，只包含基本信息
    """
    uuid: str = Field(..., description="节点UUID")
    name: str = Field(..., description="节点名称")
    type: str = Field(..., description="节点类型：entity / episode / community")
    domain: Optional[str] = Field(None, description="所属领域")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "node_123",
                "name": "Agent Memory",
                "type": "entity",
                "domain": "AI",
                "created_at": "2025-12-10T10:00:00Z"
            }
        }


class GraphEdge(BaseModel):
    """图谱边（简化版）
    
    用于图谱可视化渲染，只包含基本信息
    """
    uuid: str = Field(..., description="边UUID")
    source: str = Field(..., description="源节点UUID")
    target: str = Field(..., description="目标节点UUID")
    type: str = Field("RELATES_TO", description="关系类型")
    weight: float = Field(1.0, description="关系权重", ge=0.0, le=1.0)
    created_at: Optional[datetime] = Field(None, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "edge_456",
                "source": "node_123",
                "target": "node_124",
                "type": "RELATES_TO",
                "weight": 0.85,
                "created_at": "2025-12-10T10:05:00Z"
            }
        }


class GraphStats(BaseModel):
    """图谱统计信息（简化版）
    
    用于 UserGraphResponse 中的统计数据
    """
    total_nodes: int = Field(0, description="总节点数")
    total_edges: int = Field(0, description="总边数")
    entity_count: int = Field(0, description="实体节点数")
    episode_count: int = Field(0, description="Episode节点数")
    community_count: int = Field(0, description="社区节点数")


class UserGraphResponse(BaseModel):
    """用户图谱响应 (REQ-GRAPH-1)
    
    获取用户的知识图谱数据，用于前端可视化渲染
    """
    user_id: str = Field(..., description="用户ID")
    graph_stats: GraphStats = Field(..., description="图谱统计")
    nodes: List[GraphNode] = Field(default_factory=list, description="节点列表")
    edges: List[GraphEdge] = Field(default_factory=list, description="边列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "graph_stats": {
                    "total_nodes": 150,
                    "total_edges": 320,
                    "entity_count": 120,
                    "episode_count": 30,
                    "community_count": 0
                },
                "nodes": [
                    {
                        "uuid": "node_123",
                        "name": "Agent Memory",
                        "type": "entity",
                        "domain": "AI",
                        "created_at": "2025-12-10T10:00:00Z"
                    }
                ],
                "edges": [
                    {
                        "uuid": "edge_456",
                        "source": "node_123",
                        "target": "node_124",
                        "type": "RELATES_TO",
                        "weight": 0.85,
                        "created_at": "2025-12-10T10:05:00Z"
                    }
                ]
            }
        }


# ==================== REQ-GRAPH-2: 获取节点详情 ====================

class NodeRelation(BaseModel):
    """节点关系信息"""
    edge_uuid: str = Field(..., description="边UUID")
    type: str = Field(..., description="关系类型")
    direction: str = Field(..., description="方向：outgoing / incoming")


class NeighborNode(BaseModel):
    """邻居节点详情"""
    uuid: str = Field(..., description="节点UUID")
    name: str = Field(..., description="节点名称")
    type: str = Field(..., description="节点类型")
    relation: NodeRelation = Field(..., description="关系信息")


class SourceEpisode(BaseModel):
    """来源Episode
    
    记录节点是从哪个Episode中抽取出来的
    """
    uuid: str = Field(..., description="Episode UUID")
    content: str = Field(..., description="Episode内容（截取前200字符）")
    created_at: Optional[datetime] = Field(None, description="创建时间")


class NodeProperties(BaseModel):
    """节点属性"""
    domain: Optional[str] = Field(None, description="所属领域")
    summary: Optional[str] = Field(None, description="节点摘要")
    entity_type: Optional[str] = Field(None, description="实体类型")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class NodeDetailResponse(BaseModel):
    """节点详情响应 (REQ-GRAPH-2)
    
    获取指定节点的详细信息，用于点击节点后查看详情
    """
    uuid: str = Field(..., description="节点UUID")
    name: str = Field(..., description="节点名称")
    type: str = Field(..., description="节点类型：entity / episode / community")
    properties: NodeProperties = Field(..., description="节点属性")
    neighbors: Optional[List[NeighborNode]] = Field(None, description="邻居节点列表")
    source_episodes: Optional[List[SourceEpisode]] = Field(None, description="来源Episode列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "node_123",
                "name": "Agent Memory",
                "type": "entity",
                "properties": {
                    "domain": "AI",
                    "summary": "Agent Memory是一种长期记忆机制，用于存储对话历史...",
                    "entity_type": "concept",
                    "created_at": "2025-12-10T10:00:00Z",
                    "updated_at": "2025-12-11T08:30:00Z"
                },
                "neighbors": [
                    {
                        "uuid": "node_124",
                        "name": "RAG",
                        "type": "entity",
                        "relation": {
                            "edge_uuid": "edge_456",
                            "type": "IMPROVED_BY",
                            "direction": "outgoing"
                        }
                    }
                ],
                "source_episodes": [
                    {
                        "uuid": "ep_1",
                        "content": "用户问：agent memory的SOTA是什么技术",
                        "created_at": "2025-12-10T10:00:00Z"
                    }
                ]
            }
        }


# ==================== REQ-GRAPH-3: 获取边详情 ====================

class EdgeNodeInfo(BaseModel):
    """边关联的节点信息"""
    uuid: str = Field(..., description="节点UUID")
    name: str = Field(..., description="节点名称")
    type: str = Field(..., description="节点类型")


class EdgeProperties(BaseModel):
    """边属性"""
    weight: float = Field(1.0, description="关系权重")
    description: Optional[str] = Field(None, description="关系描述")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class EdgeDetailResponse(BaseModel):
    """边详情响应 (REQ-GRAPH-3)
    
    获取指定边（关系）的详细信息
    """
    uuid: str = Field(..., description="边UUID")
    type: str = Field(..., description="关系类型")
    source: EdgeNodeInfo = Field(..., description="源节点信息")
    target: EdgeNodeInfo = Field(..., description="目标节点信息")
    properties: EdgeProperties = Field(..., description="边属性")
    source_episodes: Optional[List[SourceEpisode]] = Field(None, description="来源Episode列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "edge_456",
                "type": "IMPROVED_BY",
                "source": {
                    "uuid": "node_123",
                    "name": "Agent Memory",
                    "type": "entity"
                },
                "target": {
                    "uuid": "node_124",
                    "name": "RAG",
                    "type": "entity"
                },
                "properties": {
                    "weight": 0.85,
                    "description": "RAG技术改进了Agent Memory的召回率",
                    "created_at": "2025-12-10T10:05:00Z",
                    "updated_at": "2025-12-11T08:30:00Z"
                },
                "source_episodes": [
                    {
                        "uuid": "ep_2",
                        "content": "根据论文XYZ，RAG改进了Agent Memory...",
                        "created_at": "2025-12-10T10:05:00Z"
                    }
                ]
            }
        }


# ==================== REQ-GRAPH-4: 图谱统计信息 ====================

class TopEntity(BaseModel):
    """热门实体
    
    按连接数排序的top实体
    """
    uuid: str = Field(..., description="实体UUID")
    name: str = Field(..., description="实体名称")
    connection_count: int = Field(..., description="连接数")


class GrowthStats(BaseModel):
    """增长统计"""
    last_7_days_nodes: int = Field(0, description="最近7天新增节点数")
    last_7_days_edges: int = Field(0, description="最近7天新增边数")


class GraphStatistics(BaseModel):
    """完整图谱统计
    
    包含详细的图谱统计信息
    """
    total_nodes: int = Field(0, description="总节点数")
    total_edges: int = Field(0, description="总边数")
    node_types: Dict[str, int] = Field(default_factory=dict, description="按类型统计节点数")
    entity_domains: Dict[str, int] = Field(default_factory=dict, description="按领域统计实体数")
    top_entities: List[TopEntity] = Field(default_factory=list, description="热门实体列表")
    growth: GrowthStats = Field(default_factory=GrowthStats, description="增长统计")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")


class GraphStatsResponse(BaseModel):
    """图谱统计响应 (REQ-GRAPH-4)
    
    获取用户图谱的统计信息
    """
    user_id: str = Field(..., description="用户ID")
    statistics: GraphStatistics = Field(..., description="统计信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "statistics": {
                    "total_nodes": 150,
                    "total_edges": 320,
                    "node_types": {
                        "entity": 120,
                        "episode": 30
                    },
                    "entity_domains": {
                        "AI": 60,
                        "SE": 30,
                        "CV": 30
                    },
                    "top_entities": [
                        {
                            "uuid": "node_123",
                            "name": "Agent Memory",
                            "connection_count": 25
                        },
                        {
                            "uuid": "node_124",
                            "name": "RAG",
                            "connection_count": 20
                        }
                    ],
                    "growth": {
                        "last_7_days_nodes": 15,
                        "last_7_days_edges": 32
                    },
                    "last_updated": "2025-12-11T10:00:00Z"
                }
            }
        }


# ==================== 错误响应模型 ====================

class GraphErrorResponse(BaseModel):
    """图谱模块错误响应
    
    统一的错误响应格式
    """
    error: str = Field(..., description="错误代码：ACCESS_DENIED / NODE_NOT_FOUND / EDGE_NOT_FOUND / USER_NOT_FOUND")
    message: str = Field(..., description="错误信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ACCESS_DENIED",
                "message": "Cannot access other user's graph"
            }
        }
