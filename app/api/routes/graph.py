"""
图谱 API 路由
提供知识图谱的核心 API 接口

根据 PRD_图谱模块.md 实现：
- REQ-GRAPH-1: GET /api/v1/graph/{user_id} - 获取用户图谱
- REQ-GRAPH-2: GET /api/v1/graph/node/{node_uuid} - 获取节点详情
- REQ-GRAPH-3: GET /api/v1/graph/edge/{edge_uuid} - 获取边详情
- REQ-GRAPH-4: GET /api/v1/graph/stats - 图谱统计信息

特性：
- ✅ JWT 认证（安全）
- ✅ 命名空间隔离（通过 group_id = user_id）
- ✅ 权限校验（只能访问自己的图谱）

注意：路由定义顺序很重要！
- 具体路由（如 /stats, /node/{}, /edge/{}）必须放在通配符路由（/{user_id}）之前
- 否则通配符会匹配所有路径导致路由冲突
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from app.schemas.graph import (
    UserGraphResponse, NodeDetailResponse, EdgeDetailResponse, GraphStatsResponse,
    GraphErrorResponse,
)
from app.services.graph_service import GraphService
from app.api.dependencies.auth import get_current_user
from app.models.db_models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/graph", tags=["图谱模块"])


# ==================== REQ-GRAPH-4: 图谱统计信息（优先匹配） ====================

@router.get(
    "/stats",
    response_model=GraphStatsResponse,
    summary="图谱统计信息",
    description="""
获取用户图谱的统计信息，包括节点数量、边数量、按领域分布、增长趋势等。

**REQ-GRAPH-4**

特性：
- ✅ JWT 认证（需要登录）
- ✅ 从 Token 中获取 user_id，无需传参

返回内容：
- 总节点数、总边数
- 按节点类型统计（entity / episode）
- 按领域统计实体分布
- Top 实体（按连接数排序）
- 最近 7 天增长趋势
""",
    tags=["图谱模块"]
)
async def get_graph_stats(
    current_user: User = Depends(get_current_user),
):
    """获取图谱统计信息"""
    service = GraphService()
    try:
        return await service.get_graph_stats(user_id=current_user.user_id)
    except Exception as e:
        logger.error(f"Get graph stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph stats: {str(e)}"
        )
    finally:
        await service.close()


# ==================== REQ-GRAPH-2: 获取节点详情 ====================

@router.get(
    "/node/{node_uuid}",
    response_model=NodeDetailResponse,
    responses={
        403: {"model": GraphErrorResponse, "description": "无权访问该节点"},
        404: {"model": GraphErrorResponse, "description": "节点不存在"},
    },
    summary="获取节点详情",
    description="""
获取指定节点的详细信息，包括节点属性、邻居节点、来源 Episodes 等。

**REQ-GRAPH-2**

特性：
- ✅ JWT 认证（需要登录）
- ✅ 权限校验（只能访问自己的节点）
- ✅ 可选包含邻居节点
- ✅ 可选包含来源 Episodes

参数说明：
- **include_neighbors**: 是否包含邻居节点，默认 true
- **neighbor_depth**: 邻居深度（1-3），默认 1
- **include_episodes**: 是否包含来源 Episodes，默认 false
""",
    tags=["图谱模块"]
)
async def get_node_detail(
    node_uuid: str,
    include_neighbors: bool = Query(True, description="是否包含邻居节点"),
    neighbor_depth: int = Query(1, ge=1, le=3, description="邻居深度（1-3）"),
    include_episodes: bool = Query(False, description="是否包含来源 Episodes"),
    current_user: User = Depends(get_current_user),
):
    """获取节点详细信息"""
    service = GraphService()
    try:
        return await service.get_node_details(
            node_uuid=node_uuid,
            user_id=current_user.user_id,
            include_neighbors=include_neighbors,
            neighbor_depth=neighbor_depth,
            include_episodes=include_episodes
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NODE_NOT_FOUND",
                "message": str(e)
            }
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "ACCESS_DENIED",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Get node detail error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get node detail: {str(e)}"
        )
    finally:
        await service.close()


# ==================== REQ-GRAPH-3: 获取边详情 ====================

@router.get(
    "/edge/{edge_uuid}",
    response_model=EdgeDetailResponse,
    responses={
        403: {"model": GraphErrorResponse, "description": "无权访问该边"},
        404: {"model": GraphErrorResponse, "description": "边不存在"},
    },
    summary="获取边详情",
    description="""
获取指定边（关系）的详细信息，包括关系类型、源节点、目标节点、关系描述等。

**REQ-GRAPH-3**

特性：
- ✅ JWT 认证（需要登录）
- ✅ 权限校验（边的源节点和目标节点都必须属于当前用户）
""",
    tags=["图谱模块"]
)
async def get_edge_detail(
    edge_uuid: str,
    current_user: User = Depends(get_current_user),
):
    """获取边详细信息"""
    service = GraphService()
    try:
        return await service.get_edge_details(
            edge_uuid=edge_uuid,
            user_id=current_user.user_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "EDGE_NOT_FOUND",
                "message": str(e)
            }
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "ACCESS_DENIED",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Get edge detail error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get edge detail: {str(e)}"
        )
    finally:
        await service.close()


# ==================== REQ-GRAPH-1: 获取用户图谱（通配符路由放最后） ====================

@router.get(
    "/{user_id}",
    response_model=UserGraphResponse,
    responses={
        403: {"model": GraphErrorResponse, "description": "访问其他用户图谱"},
        404: {"model": GraphErrorResponse, "description": "用户不存在"},
    },
    summary="获取用户图谱",
    description="""
获取用户的知识图谱数据（简化版），用于前端图谱可视化渲染。

**REQ-GRAPH-1**

特性：
- ✅ JWT 认证（需要登录）
- ✅ 命名空间隔离（只能访问自己的图谱）
- ✅ 默认不包含 Episode 节点
- ✅ 默认最多返回 1000 个节点

参数说明：
- **mode**: 图谱模式，默认 simple（简化版）
- **include_episodes**: 是否包含 Episode 节点，默认 false
- **limit**: 最大节点数，默认 1000
- **node_types**: 筛选节点类型（逗号分隔，如 entity,episode）
""",
    tags=["图谱模块"]
)
async def get_user_graph(
    user_id: str,
    mode: str = Query("simple", description="图谱模式：simple（简化版）"),
    include_episodes: bool = Query(False, description="是否包含 Episode 节点"),
    limit: int = Query(1000, ge=1, le=5000, description="最大节点数"),
    node_types: Optional[str] = Query(None, description="筛选节点类型（逗号分隔）"),
    current_user: User = Depends(get_current_user),
):
    """获取用户图谱数据"""
    # 1. 权限检查：只能访问自己的图谱
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "ACCESS_DENIED",
                "message": "Cannot access other user's graph"
            }
        )
    
    # 2. 解析 node_types 参数
    node_type_list = None
    if node_types:
        node_type_list = [t.strip() for t in node_types.split(",") if t.strip()]
    
    # 3. 调用服务获取图谱数据
    service = GraphService()
    try:
        return await service.get_user_graph(
            user_id=user_id,
            include_episodes=include_episodes,
            limit=limit,
            node_types=node_type_list
        )
    except Exception as e:
        logger.error(f"Get user graph error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user graph: {str(e)}"
        )
    finally:
        await service.close()
