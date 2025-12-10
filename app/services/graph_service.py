"""图谱服务
处理所有图谱操作的业务逻辑，包括搜索、节点查询、路径查询等
"""
import time
from typing import List, Optional, Dict, Any, Tuple
from app.core.graphiti_client import GraphitiClient
from app.services.namespace_service import NamespaceService
from app.schemas.graph import (
    GraphSearchRequest, GraphSearchResponse, SearchResult,
    NodeDetailResponse, NeighborNode, PathQueryRequest, 
    PathQueryResponse, Path, PathNode, PathEdge, RerankMode
)
from app.core.constants import DEFAULT_SEARCH_LIMIT, MAX_PATH_LENGTH, MAX_PATHS
import logging

logger = logging.getLogger(__name__)


class GraphService:
    """图谱操作服务
    
    提供知识图谱的核心功能：
    - 混合搜索（语义+BM25）
    - 双图谱Fallback机制
    - 多种重排模式
    - 节点查询
    - 路径查询
    """

    def __init__(self):
        self.graph = GraphitiClient()
        self.namespace_service = NamespaceService()

    async def search(self, req: GraphSearchRequest) -> GraphSearchResponse:
        """执行图谱搜索
        
        支持混合搜索、双图谱Fallback、多种重排模式
        
        Args:
            req: 搜索请求
            
        Returns:
            GraphSearchResponse: 搜索结果
        """
        start_time = time.time()
        fallback_triggered = False
        
        try:
            # 1. 首先在指定命名空间搜索
            results = await self._search_in_namespace(
                req.query, 
                req.group_id, 
                req.limit,
                req.center_node_uuid
            )
            
            # 2. 如果结果不足且启用了Fallback，尝试全局搜索
            if len(results) < req.limit and req.enable_fallback and req.group_id != "global":
                logger.info(f"Triggering fallback search for query: {req.query}")
                global_results = await self._search_in_namespace(
                    req.query, 
                    "global", 
                    req.limit - len(results),
                    None
                )
                results.extend(global_results)
                fallback_triggered = True
            
            # 3. 应用重排序（如果指定）
            if req.rerank_mode:
                results = await self._rerank_results(
                    results, 
                    req.rerank_mode, 
                    req.query,
                    req.center_node_uuid,
                    req.max_distance
                )
            
            # 4. 转换为响应格式
            search_results = [self._convert_to_search_result(r) for r in results[:req.limit]]
            
            search_time_ms = (time.time() - start_time) * 1000
            
            return GraphSearchResponse(
                results=search_results,
                total=len(search_results),
                query=req.query,
                rerank_mode=req.rerank_mode if req.rerank_mode else None,  # 已经是字符串，不需要.value
                search_time_ms=search_time_ms,
                fallback_triggered=fallback_triggered
            )
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return GraphSearchResponse(
                results=[],
                total=0,
                query=req.query,
                search_time_ms=(time.time() - start_time) * 1000
            )

    async def _search_in_namespace(
        self, 
        query: str, 
        group_id: Optional[str], 
        limit: int,
        center_node_uuid: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """在指定命名空间中搜索"""
        try:
            results = await self.graph.search(
                query=query, 
                group_id=group_id,
                focal_node_uuid=center_node_uuid
            )
            return results[:limit] if results else []
        except Exception as e:
            logger.error(f"Namespace search error: {str(e)}")
            return []

    async def _rerank_results(
        self, 
        results: List[Dict[str, Any]], 
        mode: RerankMode,
        query: str,
        center_node_uuid: Optional[str] = None,
        max_distance: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """应用重排序策略
        
        Args:
            results: 原始搜索结果
            mode: 重排模式
            query: 查询字符串
            center_node_uuid: 中心节点UUID（用于node_distance模式）
            max_distance: 最大距离（用于node_distance模式）
            
        Returns:
            重排后的结果
        """
        if not results:
            return results
        
        if mode == RerankMode.RRF:
            return self._rerank_rrf(results)
        elif mode == RerankMode.MMR:
            return self._rerank_mmr(results, query)
        elif mode == RerankMode.CROSS_ENCODER:
            return self._rerank_cross_encoder(results, query)
        elif mode == RerankMode.NODE_DISTANCE:
            return await self._rerank_node_distance(results, center_node_uuid, max_distance)
        else:
            return results

    def _rerank_rrf(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion重排"""
        # RRF公式: score = 1 / (k + rank)，k通常取60
        k = 60
        for i, result in enumerate(results):
            rrf_score = 1.0 / (k + i + 1)
            result['score'] = result.get('score', 0.0) * 0.5 + rrf_score * 0.5
        
        return sorted(results, key=lambda x: x.get('score', 0.0), reverse=True)

    def _rerank_mmr(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Maximal Marginal Relevance重排
        
        在保证相关性的同时增加多样性
        """
        # 简化的MMR实现：基于实体类型多样性
        if not results:
            return results
        
        reranked = []
        remaining = results.copy()
        seen_types = set()
        
        while remaining:
            # 优先选择未见过类型的结果
            best_idx = 0
            best_score = -1
            
            for i, result in enumerate(remaining):
                entity_type = result.get('entity_type', 'Unknown')
                base_score = result.get('score', 0.0)
                
                # 如果是新类型，给予奖励
                diversity_bonus = 0.2 if entity_type not in seen_types else 0.0
                final_score = base_score + diversity_bonus
                
                if final_score > best_score:
                    best_score = final_score
                    best_idx = i
            
            # 添加最佳结果
            selected = remaining.pop(best_idx)
            seen_types.add(selected.get('entity_type', 'Unknown'))
            reranked.append(selected)
        
        return reranked

    def _rerank_cross_encoder(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Cross-Encoder重排
        
        注意：实际实现需要调用Graphiti的cross_encoder，这里提供基础框架
        """
        # TODO: 集成实际的Cross-Encoder模型
        # 目前返回原始结果
        logger.info("Cross-encoder reranking requested but not fully implemented")
        return results

    async def _rerank_node_distance(
        self, 
        results: List[Dict[str, Any]], 
        center_node_uuid: Optional[str],
        max_distance: Optional[int]
    ) -> List[Dict[str, Any]]:
        """基于节点距离重排
        
        离中心节点更近的结果排名更高
        """
        if not center_node_uuid:
            return results
        
        # TODO: 实现实际的图距离计算
        # 目前返回原始结果
        logger.info(f"Node distance reranking from {center_node_uuid}")
        return results

    def _convert_to_search_result(self, raw_result: Dict[str, Any]) -> SearchResult:
        """将原始结果转换为SearchResult对象"""
        return SearchResult(
            uuid=raw_result.get('uuid', ''),
            name=raw_result.get('name', ''),
            entity_type=raw_result.get('entity_type'),
            score=raw_result.get('score', 0.0),
            summary=raw_result.get('summary'),
            properties=raw_result.get('properties', {}),
            source=raw_result.get('source', 'user')
        )

    async def get_entity(self, uuid: str) -> Dict[str, Any]:
        """获取实体详情（简单版本）
        
        Args:
            uuid: 节点UUID
            
        Returns:
            节点信息字典
        """
        try:
            return await self.graph.client.get_node(uuid)
        except Exception as e:
            logger.error(f"Get entity error: {str(e)}")
            raise

    async def get_node_detail(
        self, 
        uuid: str, 
        include_neighbors: bool = False,
        neighbor_limit: int = 10
    ) -> NodeDetailResponse:
        """获取节点详细信息
        
        Args:
            uuid: 节点UUID
            include_neighbors: 是否包含邻居节点
            neighbor_limit: 邻居节点数量限制
            
        Returns:
            NodeDetailResponse: 节点详情
        """
        try:
            # 1. 获取节点基本信息
            node = await self.graph.client.get_node(uuid)
            
            # 2. 如果需要，获取邻居节点
            neighbors = None
            neighbor_count = 0
            
            if include_neighbors:
                neighbors, neighbor_count = await self._get_neighbors(uuid, neighbor_limit)
            
            return NodeDetailResponse(
                uuid=node.get('uuid', uuid),
                name=node.get('name', ''),
                entity_type=node.get('entity_type'),
                properties=node.get('properties', {}),
                summary=node.get('summary'),
                neighbors=neighbors,
                neighbor_count=neighbor_count
            )
            
        except Exception as e:
            logger.error(f"Get node detail error: {str(e)}")
            raise

    async def _get_neighbors(
        self, 
        uuid: str, 
        limit: int = 10
    ) -> Tuple[List[NeighborNode], int]:
        """获取节点的邻居
        
        Returns:
            Tuple[List[NeighborNode], int]: (邻居列表, 总邻居数)
        """
        try:
            # TODO: 实现实际的邻居查询
            # 目前返回空列表
            return [], 0
        except Exception as e:
            logger.error(f"Get neighbors error: {str(e)}")
            return [], 0

    async def get_neighbors(
        self,
        uuid: str,
        direction: str = "both",
        node_types: Optional[List[str]] = None,
        relation_types: Optional[List[str]] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取节点的邻居（独立API）
        
        Args:
            uuid: 节点UUID
            direction: 方向（incoming/outgoing/both）
            node_types: 筛选的节点类型
            relation_types: 筛选的关系类型
            limit: 返回数量限制
            
        Returns:
            包含邻居节点和边的字典
        """
        try:
            # TODO: 实现实际的邻居查询逻辑
            return {
                "center_node": uuid,
                "neighbors": {
                    "nodes": [],
                    "edges": []
                },
                "total": 0,
                "has_more": False
            }
        except Exception as e:
            logger.error(f"Get neighbors error: {str(e)}")
            raise

    async def find_paths(self, req: PathQueryRequest) -> PathQueryResponse:
        """查找两个节点之间的路径
        
        Args:
            req: 路径查询请求
            
        Returns:
            PathQueryResponse: 路径查询结果
        """
        start_time = time.time()
        
        try:
            # TODO: 实现实际的路径查询算法
            # 这里提供基础框架
            paths = await self._find_shortest_paths(
                req.source_uuid,
                req.target_uuid,
                req.max_depth,
                req.limit,
                req.group_id
            )
            
            query_time_ms = (time.time() - start_time) * 1000
            
            shortest_length = min([p.length for p in paths]) if paths else None
            
            return PathQueryResponse(
                paths=paths,
                total_paths=len(paths),
                shortest_length=shortest_length,
                query_time_ms=query_time_ms
            )
            
        except Exception as e:
            logger.error(f"Find paths error: {str(e)}")
            return PathQueryResponse(
                paths=[],
                total_paths=0,
                query_time_ms=(time.time() - start_time) * 1000
            )

    async def _find_shortest_paths(
        self,
        source_uuid: str,
        target_uuid: str,
        max_depth: int,
        limit: int,
        group_id: Optional[str] = None
    ) -> List[Path]:
        """查找最短路径（BFS算法）
        
        TODO: 实现实际的Neo4j路径查询
        """
        # 占位实现
        return []