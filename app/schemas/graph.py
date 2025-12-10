"""
图谱相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any, Dict
from enum import Enum


class RerankMode(str, Enum):
    """重排序模式枚举"""
    RRF = "rrf"  # Reciprocal Rank Fusion
    MMR = "mmr"  # Maximal Marginal Relevance
    CROSS_ENCODER = "cross_encoder"  # Cross-Encoder重排
    NODE_DISTANCE = "node_distance"  # 节点距离重排


class GraphSearchRequest(BaseModel):
    """图谱搜索请求
    
    支持混合搜索（语义+BM25）、双图谱Fallback、多种重排模式
    """
    query: str = Field(..., description="搜索查询字符串", min_length=1)
    group_id: Optional[str] = Field(None, description="命名空间ID（如：global, user:123）")
    limit: int = Field(10, description="返回结果数量", ge=1, le=100)
    rerank_mode: Optional[RerankMode] = Field(None, description="重排序模式")
    center_node_uuid: Optional[str] = Field(None, description="中心节点UUID（用于局部搜索）")
    max_distance: Optional[int] = Field(None, description="最大跳数（用于节点距离重排）", ge=1, le=5)
    enable_fallback: bool = Field(True, description="是否启用双图谱Fallback")
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('搜索查询不能为空')
        return v.strip()
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "query": "transformer architecture for NLP",
                "group_id": "user:123",
                "limit": 10,
                "rerank_mode": "rrf",
                "enable_fallback": True
            }
        }


class SearchResult(BaseModel):
    """单个搜索结果"""
    uuid: str = Field(..., description="节点UUID")
    name: str = Field(..., description="节点名称")
    entity_type: Optional[str] = Field(None, description="实体类型")
    score: float = Field(..., description="相关度分数", ge=0.0)
    summary: Optional[str] = Field(None, description="节点摘要")
    properties: Dict[str, Any] = Field(default_factory=dict, description="节点属性")
    source: str = Field("user", description="来源（user/global/external）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "paper_001",
                "name": "Attention Is All You Need",
                "entity_type": "Paper",
                "score": 0.95,
                "summary": "Introduces Transformer architecture",
                "properties": {"year": 2017, "venue": "NeurIPS"},
                "source": "user"
            }
        }


class GraphSearchResponse(BaseModel):
    """图谱搜索响应"""
    results: List[SearchResult] = Field(default_factory=list, description="搜索结果列表")
    total: int = Field(0, description="总结果数", ge=0)
    query: str = Field(..., description="原始查询")
    rerank_mode: Optional[str] = Field(None, description="使用的重排模式")
    search_time_ms: Optional[float] = Field(None, description="搜索耗时（毫秒）")
    fallback_triggered: bool = Field(False, description="是否触发了Fallback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [],
                "total": 5,
                "query": "transformer",
                "rerank_mode": "rrf",
                "search_time_ms": 234.5,
                "fallback_triggered": False
            }
        }


class NodeDetailRequest(BaseModel):
    """节点详情请求"""
    uuid: str = Field(..., description="节点UUID")
    include_neighbors: bool = Field(False, description="是否包含邻居节点")
    neighbor_limit: int = Field(10, description="邻居节点数量限制", ge=1, le=50)


class NeighborNode(BaseModel):
    """邻居节点"""
    uuid: str
    name: str
    entity_type: Optional[str] = None
    relation_type: str = Field(..., description="与中心节点的关系类型")
    direction: str = Field(..., description="方向（incoming/outgoing）")


class NodeDetailResponse(BaseModel):
    """节点详情响应"""
    uuid: str
    name: str
    entity_type: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    summary: Optional[str] = None
    neighbors: Optional[List[NeighborNode]] = None
    neighbor_count: int = Field(0, description="邻居总数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "paper_001",
                "name": "Attention Is All You Need",
                "entity_type": "Paper",
                "properties": {"year": 2017, "venue": "NeurIPS"},
                "summary": "Introduces Transformer architecture",
                "neighbors": [],
                "neighbor_count": 15
            }
        }


class PathQueryRequest(BaseModel):
    """路径查询请求"""
    source_uuid: str = Field(..., description="源节点UUID")
    target_uuid: str = Field(..., description="目标节点UUID")
    max_depth: int = Field(5, description="最大路径长度", ge=1, le=10)
    limit: int = Field(10, description="返回路径数量", ge=1, le=50)
    group_id: Optional[str] = Field(None, description="命名空间ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "paper_001",
                "target_uuid": "paper_002",
                "max_depth": 5,
                "limit": 10,
                "group_id": "user:123"
            }
        }


class PathNode(BaseModel):
    """路径中的节点"""
    uuid: str
    name: str
    entity_type: Optional[str] = None


class PathEdge(BaseModel):
    """路径中的边"""
    source_uuid: str
    target_uuid: str
    relation_type: str


class Path(BaseModel):
    """单条路径"""
    nodes: List[PathNode] = Field(default_factory=list)
    edges: List[PathEdge] = Field(default_factory=list)
    length: int = Field(0, description="路径长度（边数）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [
                    {"uuid": "p1", "name": "Paper A", "entity_type": "Paper"},
                    {"uuid": "p2", "name": "Paper B", "entity_type": "Paper"}
                ],
                "edges": [
                    {"source_uuid": "p1", "target_uuid": "p2", "relation_type": "CITES"}
                ],
                "length": 1
            }
        }


class PathQueryResponse(BaseModel):
    """路径查询响应"""
    paths: List[Path] = Field(default_factory=list)
    total_paths: int = Field(0, description="找到的总路径数")
    shortest_length: Optional[int] = Field(None, description="最短路径长度")
    query_time_ms: Optional[float] = Field(None, description="查询耗时（毫秒）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "paths": [],
                "total_paths": 3,
                "shortest_length": 2,
                "query_time_ms": 156.3
            }
        }

