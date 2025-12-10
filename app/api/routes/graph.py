"""图谱API路由
提供知识图谱的核心API接口：搜索、节点查询、邻居查询、路径查询等
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.schemas.graph import (
    GraphSearchRequest, GraphSearchResponse,
    NodeDetailRequest, NodeDetailResponse,
    PathQueryRequest, PathQueryResponse
)
from app.services.graph_service import GraphService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/search",
    response_model=GraphSearchResponse,
    summary="图谱混合搜索",
    description="""
    执行图谱混合搜索（语义+BM25）
    
    特性：
    - 支持语义搜索和BM25混合
    - 双图谱Fallback机制（用户图谱 -> 全局图谱）
    - 多种重排模式（RRF/MMR/Cross-Encoder/Node Distance）
    - 支持局部搜索（指定中心节点）
    
    示例请求：
    ```json
    {
        "query": "transformer architecture",
        "group_id": "user:123",
        "limit": 10,
        "rerank_mode": "rrf",
        "enable_fallback": true
    }
    ```
    """,
    tags=["Graph"]
)
async def graph_search(req: GraphSearchRequest, svc: GraphService = Depends()):
    """执行图谱混合搜索
    
    Args:
        req: 搜索请求参数
        svc: 图谱服务
        
    Returns:
        GraphSearchResponse: 搜索结果
    """
    try:
        return await svc.search(req)
    except Exception as e:
        logger.error(f"Graph search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get(
    "/node/{uuid}",
    response_model=NodeDetailResponse,
    summary="获取节点详情",
    description="""
    通过UUID获取节点的详细信息
    
    可选包含邻居节点信息
    
    示例：
    - GET /api/graph/node/paper_001
    - GET /api/graph/node/paper_001?include_neighbors=true&neighbor_limit=20
    """,
    tags=["Graph"]
)
async def get_node(
    uuid: str,
    include_neighbors: bool = Query(False, description="是否包含邻居节点"),
    neighbor_limit: int = Query(10, description="邻居节点数量限制", ge=1, le=50),
    svc: GraphService = Depends()
):
    """获取节点详细信息
    
    Args:
        uuid: 节点UUID
        include_neighbors: 是否包含邻居节点
        neighbor_limit: 邻居节点数量限制
        svc: 图谱服务
        
    Returns:
        NodeDetailResponse: 节点详情
    """
    try:
        return await svc.get_node_detail(uuid, include_neighbors, neighbor_limit)
    except Exception as e:
        logger.error(f"Get node error: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Node not found: {uuid}")


@router.get(
    "/node/{uuid}/neighbors",
    summary="获取节点邻居",
    description="""
    获取指定节点的邻居节点和连接边
    
    支持：
    - 方向筛选（incoming/outgoing/both）
    - 节点类型筛选
    - 关系类型筛选
    - 分页
    
    示例：
    - GET /api/graph/node/paper_001/neighbors
    - GET /api/graph/node/paper_001/neighbors?direction=outgoing&limit=20
    - GET /api/graph/node/paper_001/neighbors?node_types=Method,Dataset
    """,
    tags=["Graph"]
)
async def get_neighbors(
    uuid: str,
    direction: str = Query("both", description="方向（incoming/outgoing/both）"),
    node_types: Optional[str] = Query(None, description="节点类型，逗号分隔"),
    relation_types: Optional[str] = Query(None, description="关系类型，逗号分隔"),
    limit: int = Query(50, description="返回数量限制", ge=1, le=100),
    svc: GraphService = Depends()
):
    """获取节点的邻居
    
    Args:
        uuid: 节点UUID
        direction: 方向（incoming/outgoing/both）
        node_types: 节点类型筛选（逗号分隔）
        relation_types: 关系类型筛选（逗号分隔）
        limit: 返回数量限制
        svc: 图谱服务
        
    Returns:
        包含邻居节点和边的字典
    """
    try:
        # 解析类型筛选参数
        node_type_list = node_types.split(',') if node_types else None
        relation_type_list = relation_types.split(',') if relation_types else None
        
        return await svc.get_neighbors(
            uuid=uuid,
            direction=direction,
            node_types=node_type_list,
            relation_types=relation_type_list,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Get neighbors error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get neighbors: {str(e)}")


@router.post(
    "/path",
    response_model=PathQueryResponse,
    summary="查找节点间路径",
    description="""
    查找两个节点之间的路径
    
    特性：
    - 最短路径优先
    - 支持多条路径
    - 可限制最大路径长度
    - 超时保护（5秒）
    
    示例请求：
    ```json
    {
        "source_uuid": "paper_001",
        "target_uuid": "paper_002",
        "max_depth": 5,
        "limit": 10,
        "group_id": "user:123"
    }
    ```
    """,
    tags=["Graph"]
)
async def find_path(req: PathQueryRequest, svc: GraphService = Depends()):
    """查找两个节点之间的路径
    
    Args:
        req: 路径查询请求
        svc: 图谱服务
        
    Returns:
        PathQueryResponse: 路径查询结果
    """
    try:
        return await svc.find_paths(req)
    except Exception as e:
        logger.error(f"Find path error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Path finding failed: {str(e)}")


# 保留向后兼容的端点
@router.get(
    "/entity/{uuid}",
    summary="获取实体（向后兼容）",
    description="获取实体节点信息（建议使用 /node/{uuid}）",
    tags=["Graph"],
    deprecated=True
)
async def get_entity(uuid: str, svc: GraphService = Depends()):
    """获取实体节点（向后兼容端点）
    
    Args:
        uuid: 节点UUID
        svc: 图谱服务
        
    Returns:
        节点信息
    """
    try:
        return await svc.get_entity(uuid)
    except Exception as e:
        logger.error(f"Get entity error: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Entity not found: {uuid}")