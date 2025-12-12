"""
图谱模块单元测试
测试知识图谱的获取、节点详情、边详情、统计信息等功能
根据 PRD_图谱模块.md 设计

测试需求：
- REQ-GRAPH-1: GET /api/v1/graph/{user_id} - 获取用户图谱
- REQ-GRAPH-2: GET /api/v1/graph/node/{node_uuid} - 获取节点详情
- REQ-GRAPH-3: GET /api/v1/graph/edge/{edge_uuid} - 获取边详情
- REQ-GRAPH-4: GET /api/v1/graph/stats - 图谱统计信息
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.schemas.graph import (
    GraphNode, GraphEdge, GraphStats,
    UserGraphResponse, NodeDetailResponse, EdgeDetailResponse, GraphStatsResponse,
    NodeProperties, NeighborNode, NodeRelation, SourceEpisode,
    EdgeNodeInfo, EdgeProperties,
    GraphStatistics, TopEntity, GrowthStats,
    GraphErrorResponse,
)
from app.services.graph_service import GraphService


# ==================== 辅助函数 ====================

async def create_test_user(
    client: AsyncClient,
    username: str = "graph_test_user",
    password: str = "TestPass123"
) -> dict:
    """创建测试用户并返回注册响应"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": password,
            "email": f"{username}@test.com"
        }
    )
    return response.json()


async def login_user(
    client: AsyncClient,
    username: str = "graph_test_user",
    password: str = "TestPass123"
) -> str:
    """登录用户并返回 access_token"""
    response = await client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    return response.json().get("access_token")


class AsyncIterator:
    """异步迭代器，用于 mock Neo4j 查询结果"""
    def __init__(self, items):
        self.items = items
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


class AsyncContextManager:
    """异步上下文管理器，用于 mock Neo4j session"""
    def __init__(self, return_value):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


def create_mock_neo4j_result(records: list):
    """创建 Mock Neo4j 查询结果"""
    mock_result = MagicMock()
    mock_result.__aiter__ = lambda self: AsyncIterator(records)
    mock_result.single = AsyncMock(return_value=records[0] if records else None)
    return mock_result


# ==================== Schema 测试 ====================

class TestGraphSchemas:
    """图谱 Schema 模型测试"""
    
    def test_graph_node_creation(self):
        """测试 GraphNode 创建"""
        node = GraphNode(
            uuid="node_123",
            name="Agent Memory",
            type="entity",
            domain="AI",
            created_at=datetime.now(timezone.utc)
        )
        assert node.uuid == "node_123"
        assert node.name == "Agent Memory"
        assert node.type == "entity"
        assert node.domain == "AI"
    
    def test_graph_node_minimal(self):
        """测试 GraphNode 最小必填字段"""
        node = GraphNode(
            uuid="node_123",
            name="Test Node",
            type="entity"
        )
        assert node.uuid == "node_123"
        assert node.domain is None
        assert node.created_at is None
    
    def test_graph_edge_creation(self):
        """测试 GraphEdge 创建"""
        edge = GraphEdge(
            uuid="edge_456",
            source="node_123",
            target="node_124",
            type="RELATES_TO",
            weight=0.85
        )
        assert edge.uuid == "edge_456"
        assert edge.source == "node_123"
        assert edge.target == "node_124"
        assert edge.type == "RELATES_TO"
        assert edge.weight == 0.85
    
    def test_graph_edge_default_values(self):
        """测试 GraphEdge 默认值"""
        edge = GraphEdge(
            uuid="edge_456",
            source="node_123",
            target="node_124"
        )
        assert edge.type == "RELATES_TO"
        assert edge.weight == 1.0
    
    def test_graph_stats_default(self):
        """测试 GraphStats 默认值"""
        stats = GraphStats()
        assert stats.total_nodes == 0
        assert stats.total_edges == 0
        assert stats.entity_count == 0
        assert stats.episode_count == 0
        assert stats.community_count == 0
    
    def test_graph_stats_with_values(self):
        """测试 GraphStats 设置值"""
        stats = GraphStats(
            total_nodes=150,
            total_edges=320,
            entity_count=120,
            episode_count=30,
            community_count=0
        )
        assert stats.total_nodes == 150
        assert stats.total_edges == 320
        assert stats.entity_count == 120
    
    def test_user_graph_response(self):
        """测试 UserGraphResponse 创建"""
        response = UserGraphResponse(
            user_id="user_123",
            graph_stats=GraphStats(total_nodes=10, total_edges=5),
            nodes=[
                GraphNode(uuid="n1", name="Node 1", type="entity"),
                GraphNode(uuid="n2", name="Node 2", type="entity"),
            ],
            edges=[
                GraphEdge(uuid="e1", source="n1", target="n2"),
            ]
        )
        assert response.user_id == "user_123"
        assert response.graph_stats.total_nodes == 10
        assert len(response.nodes) == 2
        assert len(response.edges) == 1
    
    def test_node_detail_response(self):
        """测试 NodeDetailResponse 创建"""
        response = NodeDetailResponse(
            uuid="node_123",
            name="Agent Memory",
            type="entity",
            properties=NodeProperties(
                domain="AI",
                summary="A long-term memory mechanism",
                entity_type="concept"
            ),
            neighbors=[
                NeighborNode(
                    uuid="node_124",
                    name="RAG",
                    type="entity",
                    relation=NodeRelation(
                        edge_uuid="edge_456",
                        type="IMPROVED_BY",
                        direction="outgoing"
                    )
                )
            ],
            source_episodes=[
                SourceEpisode(
                    uuid="ep_1",
                    content="User asked about agent memory..."
                )
            ]
        )
        assert response.uuid == "node_123"
        assert response.properties.domain == "AI"
        assert len(response.neighbors) == 1
        assert response.neighbors[0].relation.direction == "outgoing"
    
    def test_edge_detail_response(self):
        """测试 EdgeDetailResponse 创建"""
        response = EdgeDetailResponse(
            uuid="edge_456",
            type="IMPROVED_BY",
            source=EdgeNodeInfo(uuid="node_123", name="Agent Memory", type="entity"),
            target=EdgeNodeInfo(uuid="node_124", name="RAG", type="entity"),
            properties=EdgeProperties(
                weight=0.85,
                description="RAG improves Agent Memory recall"
            )
        )
        assert response.uuid == "edge_456"
        assert response.source.name == "Agent Memory"
        assert response.target.name == "RAG"
        assert response.properties.weight == 0.85
    
    def test_graph_stats_response(self):
        """测试 GraphStatsResponse 创建"""
        response = GraphStatsResponse(
            user_id="user_123",
            statistics=GraphStatistics(
                total_nodes=150,
                total_edges=320,
                node_types={"entity": 120, "episode": 30},
                entity_domains={"AI": 60, "SE": 30},
                top_entities=[
                    TopEntity(uuid="n1", name="Agent Memory", connection_count=25),
                    TopEntity(uuid="n2", name="RAG", connection_count=20),
                ],
                growth=GrowthStats(last_7_days_nodes=15, last_7_days_edges=32)
            )
        )
        assert response.user_id == "user_123"
        assert response.statistics.total_nodes == 150
        assert len(response.statistics.top_entities) == 2
        assert response.statistics.growth.last_7_days_nodes == 15
    
    def test_graph_error_response(self):
        """测试 GraphErrorResponse 创建"""
        error = GraphErrorResponse(
            error="ACCESS_DENIED",
            message="Cannot access other user's graph"
        )
        assert error.error == "ACCESS_DENIED"
        assert "Cannot access" in error.message


# ==================== Service 层测试 ====================

class TestGraphService:
    """GraphService 测试"""
    
    @pytest.mark.asyncio
    async def test_get_user_graph_empty(self):
        """测试获取空图谱"""
        service = GraphService()
        
        # 创建 Mock Session
        mock_session = AsyncMock()
        mock_session.run = AsyncMock(return_value=create_mock_neo4j_result([]))
        
        # 创建 Mock Driver，session() 返回 async context manager
        mock_driver = MagicMock()
        mock_driver.session = MagicMock(return_value=AsyncContextManager(mock_session))
        
        # 直接设置 driver
        service._driver = mock_driver
        
        result = await service.get_user_graph(user_id="user_123")
        
        assert result.user_id == "user_123"
        assert result.graph_stats.total_nodes == 0
        assert result.graph_stats.total_edges == 0
        assert len(result.nodes) == 0
        assert len(result.edges) == 0
    
    @pytest.mark.asyncio
    async def test_get_node_details_not_found(self):
        """测试节点不存在"""
        service = GraphService()
        
        # Mock Session
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        
        # Mock Driver
        mock_driver = MagicMock()
        mock_driver.session = MagicMock(return_value=AsyncContextManager(mock_session))
        service._driver = mock_driver
        
        with pytest.raises(ValueError) as exc_info:
            await service.get_node_details(
                node_uuid="non_existent",
                user_id="user_123"
            )
        
        assert "Node not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_node_details_access_denied(self):
        """测试节点权限校验"""
        service = GraphService()
        
        # Mock 查询返回属于其他用户的节点
        mock_record = {
            "n": {"uuid": "node_123", "name": "Test", "group_id": "other_user"},
            "node_labels": ["EntityNode"]
        }
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=mock_record)
        mock_session.run = AsyncMock(return_value=mock_result)
        
        # Mock Driver
        mock_driver = MagicMock()
        mock_driver.session = MagicMock(return_value=AsyncContextManager(mock_session))
        service._driver = mock_driver
        
        with pytest.raises(PermissionError) as exc_info:
            await service.get_node_details(
                node_uuid="node_123",
                user_id="user_123"
            )
        
        assert "does not belong to user" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_edge_details_not_found(self):
        """测试边不存在"""
        service = GraphService()
        
        # Mock Session
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        
        # Mock Driver
        mock_driver = MagicMock()
        mock_driver.session = MagicMock(return_value=AsyncContextManager(mock_session))
        service._driver = mock_driver
        
        with pytest.raises(ValueError) as exc_info:
            await service.get_edge_details(
                edge_uuid="non_existent",
                user_id="user_123"
            )
        
        assert "Edge not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_determine_node_type(self):
        """测试节点类型判断"""
        service = GraphService()
        
        assert service._determine_node_type(["EntityNode"]) == "entity"
        assert service._determine_node_type(["EpisodicNode"]) == "episode"
        assert service._determine_node_type(["CommunityNode"]) == "community"
        assert service._determine_node_type(["UnknownNode"]) == "entity"
        assert service._determine_node_type([]) == "entity"
    
    @pytest.mark.asyncio
    async def test_parse_datetime(self):
        """测试时间解析"""
        service = GraphService()
        
        # None
        assert service._parse_datetime(None) is None
        
        # datetime 对象
        dt = datetime.now(timezone.utc)
        assert service._parse_datetime(dt) == dt
        
        # ISO 格式字符串
        result = service._parse_datetime("2025-12-11T10:00:00Z")
        assert result is not None
        assert result.year == 2025
        
        # 无效字符串
        assert service._parse_datetime("invalid") is None


# ==================== API 端点测试 ====================

class TestGetUserGraphAPI:
    """GET /api/v1/graph/{user_id} 测试 (REQ-GRAPH-1)"""
    
    @pytest.mark.asyncio
    async def test_get_user_graph_unauthorized(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.get("/api/v1/graph/some-user-id")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_user_graph_access_denied(self, client: AsyncClient, test_session: AsyncSession):
        """测试访问其他用户的图谱"""
        # 创建并登录用户
        await create_test_user(client, "graph_user_1", "TestPass123")
        token = await login_user(client, "graph_user_1", "TestPass123")
        
        # 尝试访问其他用户的图谱
        response = await client.get(
            "/api/v1/graph/other-user-id",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "ACCESS_DENIED"
        assert "Cannot access other user's graph" in data["detail"]["message"]
    
    @pytest.mark.asyncio
    async def test_get_user_graph_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功获取用户图谱"""
        # 创建并登录用户
        register_data = await create_test_user(client, "graph_user_2", "TestPass123")
        token = await login_user(client, "graph_user_2", "TestPass123")
        user_id = register_data["user_id"]
        
        # Mock GraphService
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_user_graph = AsyncMock(return_value=UserGraphResponse(
                user_id=user_id,
                graph_stats=GraphStats(total_nodes=10, total_edges=5, entity_count=10),
                nodes=[GraphNode(uuid="n1", name="Node 1", type="entity")],
                edges=[GraphEdge(uuid="e1", source="n1", target="n2")]
            ))
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                f"/api/v1/graph/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == user_id
        assert "graph_stats" in data
        assert data["graph_stats"]["total_nodes"] == 10
        assert len(data["nodes"]) == 1
        assert len(data["edges"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_user_graph_with_params(self, client: AsyncClient, test_session: AsyncSession):
        """测试带参数获取用户图谱"""
        # 创建并登录用户
        register_data = await create_test_user(client, "graph_user_3", "TestPass123")
        token = await login_user(client, "graph_user_3", "TestPass123")
        user_id = register_data["user_id"]
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_user_graph = AsyncMock(return_value=UserGraphResponse(
                user_id=user_id,
                graph_stats=GraphStats(),
                nodes=[],
                edges=[]
            ))
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                f"/api/v1/graph/{user_id}",
                params={
                    "mode": "simple",
                    "include_episodes": True,
                    "limit": 500,
                    "node_types": "entity,episode"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        
        # 验证参数传递
        mock_service.get_user_graph.assert_called_once()
        call_args = mock_service.get_user_graph.call_args
        assert call_args.kwargs["include_episodes"] == True
        assert call_args.kwargs["limit"] == 500
        assert call_args.kwargs["node_types"] == ["entity", "episode"]


class TestGetNodeDetailAPI:
    """GET /api/v1/graph/node/{node_uuid} 测试 (REQ-GRAPH-2)"""
    
    @pytest.mark.asyncio
    async def test_get_node_detail_unauthorized(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.get("/api/v1/graph/node/some-node-uuid")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_node_detail_not_found(self, client: AsyncClient, test_session: AsyncSession):
        """测试节点不存在"""
        await create_test_user(client, "node_user_1", "TestPass123")
        token = await login_user(client, "node_user_1", "TestPass123")
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_node_details = AsyncMock(
                side_effect=ValueError("Node not found: fake-uuid")
            )
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                "/api/v1/graph/node/fake-uuid",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "NODE_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_get_node_detail_access_denied(self, client: AsyncClient, test_session: AsyncSession):
        """测试访问其他用户的节点"""
        await create_test_user(client, "node_user_2", "TestPass123")
        token = await login_user(client, "node_user_2", "TestPass123")
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_node_details = AsyncMock(
                side_effect=PermissionError("Node does not belong to user")
            )
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                "/api/v1/graph/node/other-user-node",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "ACCESS_DENIED"
    
    @pytest.mark.asyncio
    async def test_get_node_detail_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功获取节点详情"""
        await create_test_user(client, "node_user_3", "TestPass123")
        token = await login_user(client, "node_user_3", "TestPass123")
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_node_details = AsyncMock(return_value=NodeDetailResponse(
                uuid="node_123",
                name="Agent Memory",
                type="entity",
                properties=NodeProperties(
                    domain="AI",
                    summary="A long-term memory mechanism"
                ),
                neighbors=[
                    NeighborNode(
                        uuid="node_124",
                        name="RAG",
                        type="entity",
                        relation=NodeRelation(
                            edge_uuid="edge_456",
                            type="IMPROVED_BY",
                            direction="outgoing"
                        )
                    )
                ]
            ))
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                "/api/v1/graph/node/node_123",
                params={"include_neighbors": True, "include_episodes": False},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["uuid"] == "node_123"
        assert data["name"] == "Agent Memory"
        assert data["type"] == "entity"
        assert data["properties"]["domain"] == "AI"
        assert len(data["neighbors"]) == 1
        assert data["neighbors"][0]["name"] == "RAG"


class TestGetEdgeDetailAPI:
    """GET /api/v1/graph/edge/{edge_uuid} 测试 (REQ-GRAPH-3)"""
    
    @pytest.mark.asyncio
    async def test_get_edge_detail_unauthorized(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.get("/api/v1/graph/edge/some-edge-uuid")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_edge_detail_not_found(self, client: AsyncClient, test_session: AsyncSession):
        """测试边不存在"""
        await create_test_user(client, "edge_user_1", "TestPass123")
        token = await login_user(client, "edge_user_1", "TestPass123")
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_edge_details = AsyncMock(
                side_effect=ValueError("Edge not found: fake-uuid")
            )
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                "/api/v1/graph/edge/fake-uuid",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "EDGE_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_get_edge_detail_access_denied(self, client: AsyncClient, test_session: AsyncSession):
        """测试访问其他用户的边"""
        await create_test_user(client, "edge_user_2", "TestPass123")
        token = await login_user(client, "edge_user_2", "TestPass123")
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_edge_details = AsyncMock(
                side_effect=PermissionError("Edge does not belong to user")
            )
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                "/api/v1/graph/edge/other-user-edge",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "ACCESS_DENIED"
    
    @pytest.mark.asyncio
    async def test_get_edge_detail_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功获取边详情"""
        await create_test_user(client, "edge_user_3", "TestPass123")
        token = await login_user(client, "edge_user_3", "TestPass123")
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_edge_details = AsyncMock(return_value=EdgeDetailResponse(
                uuid="edge_456",
                type="IMPROVED_BY",
                source=EdgeNodeInfo(uuid="node_123", name="Agent Memory", type="entity"),
                target=EdgeNodeInfo(uuid="node_124", name="RAG", type="entity"),
                properties=EdgeProperties(
                    weight=0.85,
                    description="RAG improves Agent Memory recall"
                )
            ))
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                "/api/v1/graph/edge/edge_456",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["uuid"] == "edge_456"
        assert data["type"] == "IMPROVED_BY"
        assert data["source"]["name"] == "Agent Memory"
        assert data["target"]["name"] == "RAG"
        assert data["properties"]["weight"] == 0.85


class TestGetGraphStatsAPI:
    """GET /api/v1/graph/stats 测试 (REQ-GRAPH-4)"""
    
    @pytest.mark.asyncio
    async def test_get_graph_stats_unauthorized(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.get("/api/v1/graph/stats")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_graph_stats_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功获取图谱统计"""
        register_data = await create_test_user(client, "stats_user_1", "TestPass123")
        token = await login_user(client, "stats_user_1", "TestPass123")
        user_id = register_data["user_id"]
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_graph_stats = AsyncMock(return_value=GraphStatsResponse(
                user_id=user_id,
                statistics=GraphStatistics(
                    total_nodes=150,
                    total_edges=320,
                    node_types={"entity": 120, "episode": 30},
                    entity_domains={"AI": 60, "SE": 30, "CV": 30},
                    top_entities=[
                        TopEntity(uuid="n1", name="Agent Memory", connection_count=25),
                        TopEntity(uuid="n2", name="RAG", connection_count=20),
                    ],
                    growth=GrowthStats(last_7_days_nodes=15, last_7_days_edges=32),
                    last_updated=datetime.now(timezone.utc)
                )
            ))
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                "/api/v1/graph/stats",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == user_id
        assert "statistics" in data
        
        stats = data["statistics"]
        assert stats["total_nodes"] == 150
        assert stats["total_edges"] == 320
        assert stats["node_types"]["entity"] == 120
        assert stats["entity_domains"]["AI"] == 60
        assert len(stats["top_entities"]) == 2
        assert stats["growth"]["last_7_days_nodes"] == 15


class TestGraphAPIRouteOrder:
    """测试路由优先级（确保具体路由优先于通配符路由）"""
    
    @pytest.mark.asyncio
    async def test_stats_route_not_matched_as_user_id(self, client: AsyncClient, test_session: AsyncSession):
        """测试 /stats 路由不被 /{user_id} 匹配"""
        await create_test_user(client, "route_user_1", "TestPass123")
        token = await login_user(client, "route_user_1", "TestPass123")
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_graph_stats = AsyncMock(return_value=GraphStatsResponse(
                user_id="test",
                statistics=GraphStatistics()
            ))
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                "/api/v1/graph/stats",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 应该返回 200（匹配 /stats 路由），而不是 403（匹配 /{user_id} 路由）
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_node_route_not_matched_as_user_id(self, client: AsyncClient, test_session: AsyncSession):
        """测试 /node/{uuid} 路由不被 /{user_id} 匹配"""
        await create_test_user(client, "route_user_2", "TestPass123")
        token = await login_user(client, "route_user_2", "TestPass123")
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.get_node_details = AsyncMock(
                side_effect=ValueError("Node not found")
            )
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            response = await client.get(
                "/api/v1/graph/node/test-uuid",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 应该返回 404（匹配 /node/{uuid} 路由），而不是 403
        assert response.status_code == 404


class TestGraphModuleIntegration:
    """图谱模块集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_graph_workflow(self, client: AsyncClient, test_session: AsyncSession):
        """测试完整的图谱操作工作流"""
        # 1. 注册并登录用户
        register_data = await create_test_user(client, "integration_user", "TestPass123")
        token = await login_user(client, "integration_user", "TestPass123")
        user_id = register_data["user_id"]
        
        with patch('app.api.routes.graph.GraphService') as MockService:
            mock_service = AsyncMock()
            mock_service.close = AsyncMock()
            MockService.return_value = mock_service
            
            # 2. 获取图谱统计
            mock_service.get_graph_stats = AsyncMock(return_value=GraphStatsResponse(
                user_id=user_id,
                statistics=GraphStatistics(total_nodes=10, total_edges=5)
            ))
            
            stats_response = await client.get(
                "/api/v1/graph/stats",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert stats_response.status_code == 200
            
            # 3. 获取用户图谱
            mock_service.get_user_graph = AsyncMock(return_value=UserGraphResponse(
                user_id=user_id,
                graph_stats=GraphStats(total_nodes=10, total_edges=5),
                nodes=[GraphNode(uuid="n1", name="Node 1", type="entity")],
                edges=[]
            ))
            
            graph_response = await client.get(
                f"/api/v1/graph/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert graph_response.status_code == 200
            
            # 4. 获取节点详情
            mock_service.get_node_details = AsyncMock(return_value=NodeDetailResponse(
                uuid="n1",
                name="Node 1",
                type="entity",
                properties=NodeProperties()
            ))
            
            node_response = await client.get(
                "/api/v1/graph/node/n1",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert node_response.status_code == 200
            
            # 5. 验证数据一致性
            graph_data = graph_response.json()
            node_data = node_response.json()
            
            assert graph_data["nodes"][0]["uuid"] == node_data["uuid"]

