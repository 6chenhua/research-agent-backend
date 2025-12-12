"""
图谱服务
处理所有图谱操作的业务逻辑

根据 PRD_图谱模块.md 实现：
- REQ-GRAPH-1: 获取用户图谱
- REQ-GRAPH-2: 获取节点详情
- REQ-GRAPH-3: 获取边详情
- REQ-GRAPH-4: 图谱统计信息

使用 Neo4j 异步驱动直接查询图数据库
通过 group_id = user_id 实现命名空间隔离
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Any
from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import Neo4jError

from app.schemas.graph import (
    UserGraphResponse, GraphNode, GraphEdge, GraphStats,
    NodeDetailResponse, NodeProperties, NeighborNode, NodeRelation, SourceEpisode,
    EdgeDetailResponse, EdgeNodeInfo, EdgeProperties,
    GraphStatsResponse, GraphStatistics, TopEntity, GrowthStats,
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class GraphService:
    """图谱操作服务
    
    提供知识图谱的核心功能：
    - 获取用户图谱（REQ-GRAPH-1）
    - 获取节点详情（REQ-GRAPH-2）
    - 获取边详情（REQ-GRAPH-3）
    - 图谱统计信息（REQ-GRAPH-4）
    
    使用 Neo4j 异步驱动直接查询图数据库
    通过 group_id = user_id 确保命名空间隔离
    """

    def __init__(self, driver: Optional[AsyncDriver] = None):
        """初始化服务
        
        Args:
            driver: Neo4j 异步驱动，如果不提供则懒加载创建
        """
        self._driver = driver
        self._owns_driver = driver is None  # 是否由本服务创建驱动（决定是否需要关闭）

    async def _get_driver(self) -> AsyncDriver:
        """获取 Neo4j 异步驱动（懒加载）"""
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        return self._driver

    async def close(self):
        """关闭 Neo4j 驱动连接（仅当驱动由本服务创建时）"""
        if self._driver and self._owns_driver:
            await self._driver.close()
            self._driver = None

    # ==================== REQ-GRAPH-1: 获取用户图谱 ====================

    async def get_user_graph(
        self, 
        user_id: str,
        include_episodes: bool = False,
        limit: int = 1000,
        node_types: Optional[List[str]] = None
    ) -> UserGraphResponse:
        """
        获取用户的图谱数据（简化版）
        
        Args:
            user_id: 用户ID（作为 group_id 进行命名空间隔离）
            include_episodes: 是否包含 Episode 节点，默认 false
            limit: 最大节点数，默认 1000
            node_types: 筛选节点类型，默认 None 表示全部
            
        Returns:
            UserGraphResponse: 用户图谱数据，包含节点、边和统计信息
        """
        driver = await self._get_driver()
        
        try:
            async with driver.session() as session:
                # 1. 构建节点标签过滤条件
                node_labels = ["EntityNode"]
                if include_episodes:
                    node_labels.append("EpisodicNode")
                
                # 如果指定了 node_types，进行筛选
                if node_types:
                    type_mapping = {
                        "entity": "EntityNode",
                        "episode": "EpisodicNode",
                        "community": "CommunityNode"
                    }
                    node_labels = [
                        type_mapping.get(t, t) 
                        for t in node_types 
                        if t in type_mapping
                    ]
                
                # 2. 查询节点
                query_nodes = """
                MATCH (n)
                WHERE n.group_id = $user_id
                  AND any(label IN labels(n) WHERE label IN $node_labels)
                RETURN n, labels(n) as node_labels
                LIMIT $limit
                """
                
                result_nodes = await session.run(
                    query_nodes,
                    user_id=user_id,
                    node_labels=node_labels,
                    limit=limit
                )
                
                nodes = []
                node_uuids = set()
                async for record in result_nodes:
                    node = record["n"]
                    labels = record["node_labels"]
                    formatted_node = self._format_node(node, labels)
                    nodes.append(formatted_node)
                    node_uuids.add(formatted_node.uuid)
                
                # 3. 查询边（只查询已查出节点之间的边）
                edges = []
                if node_uuids:
                    query_edges = """
                    MATCH (source)-[r]->(target)
                    WHERE source.group_id = $user_id
                      AND target.group_id = $user_id
                      AND source.uuid IN $node_uuids
                      AND target.uuid IN $node_uuids
                    RETURN r, source.uuid as source_uuid, target.uuid as target_uuid, type(r) as rel_type
                    LIMIT $limit
                    """
                    
                    result_edges = await session.run(
                        query_edges,
                        user_id=user_id,
                        node_uuids=list(node_uuids),
                        limit=limit
                    )
                    
                    async for record in result_edges:
                        formatted_edge = self._format_edge(record)
                        edges.append(formatted_edge)
                
                # 4. 计算统计信息
                entity_count = sum(1 for n in nodes if n.type == "entity")
                episode_count = sum(1 for n in nodes if n.type == "episode")
                community_count = sum(1 for n in nodes if n.type == "community")
                
                graph_stats = GraphStats(
                    total_nodes=len(nodes),
                    total_edges=len(edges),
                    entity_count=entity_count,
                    episode_count=episode_count,
                    community_count=community_count
                )
                
                return UserGraphResponse(
                    user_id=user_id,
                    graph_stats=graph_stats,
                    nodes=nodes,
                    edges=edges
                )
                
        except Neo4jError as e:
            logger.error(f"Neo4j error getting user graph: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting user graph: {str(e)}")
            raise

    def _format_node(self, node: Any, labels: List[str]) -> GraphNode:
        """格式化节点信息（简化版）"""
        # 根据标签确定节点类型
        node_type = "entity"
        if "EpisodicNode" in labels:
            node_type = "episode"
        elif "CommunityNode" in labels:
            node_type = "community"
        
        return GraphNode(
            uuid=node.get("uuid", ""),
            name=node.get("name", "Unknown"),
            type=node_type,
            domain=node.get("domain"),
            created_at=self._parse_datetime(node.get("created_at"))
        )

    def _format_edge(self, record: Any) -> GraphEdge:
        """格式化边信息（简化版）"""
        rel = record["r"]
        
        return GraphEdge(
            uuid=rel.get("uuid", ""),
            source=record["source_uuid"],
            target=record["target_uuid"],
            type=record.get("rel_type", "RELATES_TO"),
            weight=float(rel.get("weight", 1.0)),
            created_at=self._parse_datetime(rel.get("created_at"))
        )

    # ==================== REQ-GRAPH-2: 获取节点详情 ====================

    async def get_node_details(
        self, 
        node_uuid: str,
        user_id: str,
        include_neighbors: bool = True,
        neighbor_depth: int = 1,
        include_episodes: bool = False
    ) -> NodeDetailResponse:
        """
        获取节点详细信息
        
        Args:
            node_uuid: 节点 UUID
            user_id: 用户 ID（用于权限校验）
            include_neighbors: 是否包含邻居节点，默认 true
            neighbor_depth: 邻居深度（1-3），默认 1（当前实现仅支持 1 跳）
            include_episodes: 是否包含来源 Episodes，默认 false
            
        Returns:
            NodeDetailResponse: 节点详情
            
        Raises:
            ValueError: 节点不存在
            PermissionError: 无权访问（节点不属于该用户）
        """
        driver = await self._get_driver()
        
        try:
            async with driver.session() as session:
                # 1. 查询节点
                query_node = """
                MATCH (n {uuid: $node_uuid})
                RETURN n, labels(n) as node_labels
                """
                
                result = await session.run(query_node, node_uuid=node_uuid)
                record = await result.single()
                
                if not record:
                    raise ValueError(f"Node not found: {node_uuid}")
                
                node = record["n"]
                node_labels = record["node_labels"]
                
                # 2. 检查权限（命名空间隔离）
                if node.get("group_id") != user_id:
                    raise PermissionError("Node does not belong to user")
                
                # 3. 确定节点类型
                node_type = self._determine_node_type(node_labels)
                
                # 4. 构建节点属性
                properties = NodeProperties(
                    domain=node.get("domain"),
                    summary=node.get("summary"),
                    entity_type=node.get("entity_type"),
                    created_at=self._parse_datetime(node.get("created_at")),
                    updated_at=self._parse_datetime(node.get("updated_at"))
                )
                
                # 5. 查询邻居节点
                neighbors = None
                if include_neighbors:
                    neighbors = await self._get_node_neighbors(
                        session, node_uuid, user_id, limit=50
                    )
                
                # 6. 查询来源 Episodes（仅对 entity 类型有意义）
                source_episodes = None
                if include_episodes and node_type == "entity":
                    source_episodes = await self._get_source_episodes(
                        session, node_uuid, user_id
                    )
                
                return NodeDetailResponse(
                    uuid=node.get("uuid", node_uuid),
                    name=node.get("name", "Unknown"),
                    type=node_type,
                    properties=properties,
                    neighbors=neighbors,
                    source_episodes=source_episodes
                )
                
        except ValueError:
            raise
        except PermissionError:
            raise
        except Neo4jError as e:
            logger.error(f"Neo4j error getting node details: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting node details: {str(e)}")
            raise

    async def _get_node_neighbors(
        self,
        session,
        node_uuid: str,
        user_id: str,
        limit: int = 50
    ) -> List[NeighborNode]:
        """查询节点的邻居"""
        query = """
        MATCH (source {uuid: $node_uuid})-[r]-(neighbor)
        WHERE neighbor.group_id = $user_id
        RETURN neighbor, r, labels(neighbor) as neighbor_labels,
               CASE WHEN startNode(r).uuid = $node_uuid 
                    THEN 'outgoing' 
                    ELSE 'incoming' 
               END as direction,
               type(r) as rel_type
        LIMIT $limit
        """
        
        result = await session.run(
            query,
            node_uuid=node_uuid,
            user_id=user_id,
            limit=limit
        )
        
        neighbors = []
        async for record in result:
            neighbor_node = record["neighbor"]
            rel = record["r"]
            neighbor_labels = record["neighbor_labels"]
            
            neighbors.append(NeighborNode(
                uuid=neighbor_node.get("uuid", ""),
                name=neighbor_node.get("name", "Unknown"),
                type=self._determine_node_type(neighbor_labels),
                relation=NodeRelation(
                    edge_uuid=rel.get("uuid", ""),
                    type=record.get("rel_type", "RELATES_TO"),
                    direction=record["direction"]
                )
            ))
        
        return neighbors

    async def _get_source_episodes(
        self, 
        session,
        node_uuid: str,
        user_id: str,
        limit: int = 10
    ) -> List[SourceEpisode]:
        """查询实体节点的来源 Episodes"""
        query = """
        MATCH (entity {uuid: $node_uuid})<-[:MENTIONS]-(episode:EpisodicNode)
        WHERE episode.group_id = $user_id
        RETURN episode
        ORDER BY episode.created_at DESC
        LIMIT $limit
        """
        
        result = await session.run(
            query,
            node_uuid=node_uuid,
            user_id=user_id,
            limit=limit
        )
        
        episodes = []
        async for record in result:
            ep = record["episode"]
            content = ep.get("content", ep.get("episode_body", ""))
            # 截取前200字符
            if len(content) > 200:
                content = content[:200] + "..."
            
            episodes.append(SourceEpisode(
                uuid=ep.get("uuid", ""),
                content=content,
                created_at=self._parse_datetime(ep.get("created_at"))
            ))
        
        return episodes

    # ==================== REQ-GRAPH-3: 获取边详情 ====================

    async def get_edge_details(
        self,
        edge_uuid: str,
        user_id: str
    ) -> EdgeDetailResponse:
        """
        获取边的详细信息
        
        Args:
            edge_uuid: 边 UUID
            user_id: 用户 ID（用于权限校验）
            
        Returns:
            EdgeDetailResponse: 边详情
            
        Raises:
            ValueError: 边不存在
            PermissionError: 无权访问（边的源节点或目标节点不属于该用户）
        """
        driver = await self._get_driver()
        
        try:
            async with driver.session() as session:
                # 1. 查询边及其连接的节点
                query = """
                MATCH (source)-[r {uuid: $edge_uuid}]->(target)
                RETURN r, source, target, 
                       labels(source) as source_labels, 
                       labels(target) as target_labels,
                       type(r) as rel_type
                """
                
                result = await session.run(query, edge_uuid=edge_uuid)
                record = await result.single()
                
                if not record:
                    raise ValueError(f"Edge not found: {edge_uuid}")
                
                rel = record["r"]
                source_node = record["source"]
                target_node = record["target"]
                source_labels = record["source_labels"]
                target_labels = record["target_labels"]
                
                # 2. 检查权限（源节点和目标节点都必须属于该用户）
                if source_node.get("group_id") != user_id or target_node.get("group_id") != user_id:
                    raise PermissionError("Edge does not belong to user")
                
                # 3. 构建响应
                return EdgeDetailResponse(
                    uuid=rel.get("uuid", edge_uuid),
                    type=record.get("rel_type", "RELATES_TO"),
                    source=EdgeNodeInfo(
                        uuid=source_node.get("uuid", ""),
                        name=source_node.get("name", "Unknown"),
                        type=self._determine_node_type(source_labels)
                    ),
                    target=EdgeNodeInfo(
                        uuid=target_node.get("uuid", ""),
                        name=target_node.get("name", "Unknown"),
                        type=self._determine_node_type(target_labels)
                    ),
                    properties=EdgeProperties(
                        weight=float(rel.get("weight", 1.0)),
                        description=rel.get("fact", rel.get("description", "")),
                        created_at=self._parse_datetime(rel.get("created_at")),
                        updated_at=self._parse_datetime(rel.get("updated_at"))
                    ),
                    source_episodes=None  # 可选扩展：查询生成此边的 Episode
                )
                
        except ValueError:
            raise
        except PermissionError:
            raise
        except Neo4jError as e:
            logger.error(f"Neo4j error getting edge details: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting edge details: {str(e)}")
            raise

    # ==================== REQ-GRAPH-4: 图谱统计信息 ====================

    async def get_graph_stats(self, user_id: str) -> GraphStatsResponse:
        """
        获取图谱统计信息
        
        Args:
            user_id: 用户 ID（从 Token 中获取）
            
        Returns:
            GraphStatsResponse: 图谱统计数据，包含：
                - 总节点数、总边数
                - 按类型统计节点数
                - 按领域统计实体数
                - Top 实体（按连接数排序）
                - 最近 7 天增长趋势
        """
        driver = await self._get_driver()
        
        try:
            async with driver.session() as session:
                # 1. 统计节点数量
                query_nodes = """
                MATCH (n)
                WHERE n.group_id = $user_id
                RETURN 
                    count(n) as total,
                    count(CASE WHEN 'EntityNode' IN labels(n) THEN 1 END) as entities,
                    count(CASE WHEN 'EpisodicNode' IN labels(n) THEN 1 END) as episodes,
                    count(CASE WHEN 'CommunityNode' IN labels(n) THEN 1 END) as communities
                """
                result = await session.run(query_nodes, user_id=user_id)
                node_stats = await result.single()
                
                # 2. 统计边数量
                query_edges = """
                MATCH (source)-[r]->(target)
                WHERE source.group_id = $user_id AND target.group_id = $user_id
                RETURN count(r) as total_edges
                """
                result = await session.run(query_edges, user_id=user_id)
                edge_stats = await result.single()
                
                # 3. 按 Domain 统计
                query_domains = """
                MATCH (n:EntityNode)
                WHERE n.group_id = $user_id AND n.domain IS NOT NULL
                RETURN n.domain as domain, count(n) as count
                ORDER BY count DESC
                """
                result = await session.run(query_domains, user_id=user_id)
                domains = {}
                async for record in result:
                    domains[record["domain"]] = record["count"]
                
                # 4. Top 实体（按连接数）
                query_top = """
                MATCH (n:EntityNode)-[r]-()
                WHERE n.group_id = $user_id
                WITH n, count(r) as degree
                ORDER BY degree DESC
                LIMIT 5
                RETURN n.uuid as uuid, n.name as name, degree
                """
                result = await session.run(query_top, user_id=user_id)
                top_entities = []
                async for record in result:
                    top_entities.append(TopEntity(
                        uuid=record["uuid"] or "",
                        name=record["name"] or "Unknown",
                        connection_count=record["degree"]
                    ))
                
                # 5. 增长趋势（最近 7 天）
                seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
                
                query_growth_nodes = """
                MATCH (n)
                WHERE n.group_id = $user_id 
                  AND n.created_at > $since
                RETURN count(n) as new_nodes
                """
                result = await session.run(
                    query_growth_nodes,
                    user_id=user_id,
                    since=seven_days_ago.isoformat()
                )
                growth_nodes = await result.single()
                
                query_growth_edges = """
                MATCH (source)-[r]->(target)
                WHERE source.group_id = $user_id 
                  AND target.group_id = $user_id
                  AND r.created_at > $since
                RETURN count(r) as new_edges
                """
                result = await session.run(
                    query_growth_edges,
                    user_id=user_id,
                    since=seven_days_ago.isoformat()
                )
                growth_edges = await result.single()
                
                # 6. 构建响应
                statistics = GraphStatistics(
                    total_nodes=node_stats["total"] if node_stats else 0,
                    total_edges=edge_stats["total_edges"] if edge_stats else 0,
                    node_types={
                        "entity": node_stats["entities"] if node_stats else 0,
                        "episode": node_stats["episodes"] if node_stats else 0,
                        "community": node_stats["communities"] if node_stats else 0
                    },
                    entity_domains=domains,
                    top_entities=top_entities,
                    growth=GrowthStats(
                        last_7_days_nodes=growth_nodes["new_nodes"] if growth_nodes else 0,
                        last_7_days_edges=growth_edges["new_edges"] if growth_edges else 0
                    ),
                    last_updated=datetime.now(timezone.utc)
                )
                
                return GraphStatsResponse(
                    user_id=user_id,
                    statistics=statistics
                )
                
        except Neo4jError as e:
            logger.error(f"Neo4j error getting graph stats: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting graph stats: {str(e)}")
            raise

    # ==================== 辅助方法 ====================

    def _determine_node_type(self, labels: List[str]) -> str:
        """根据标签确定节点类型"""
        if "EpisodicNode" in labels:
            return "episode"
        elif "CommunityNode" in labels:
            return "community"
        return "entity"

    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        """解析时间字段"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return None
        return None
