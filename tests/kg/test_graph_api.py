"""
测试图谱API端点
包括搜索、节点查询、路径查询等API的集成测试
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.services.graph_service import GraphService
from app.schemas.graph import SearchResult


class TestGraphSearchAPI:
    """测试图谱搜索API"""
    
    @pytest.mark.asyncio
    async def test_search_api_success(self, client: AsyncClient):
        """测试搜索API成功响应"""
        
        # Mock GraphService.search
        mock_response = Mock()
        mock_response.results = [
            SearchResult(
                uuid="paper_001",
                name="Test Paper",
                entity_type="Paper",
                score=0.95,
                summary="Test summary",
                properties={"year": 2023},
                source="user"
            )
        ]
        mock_response.total = 1
        mock_response.query = "test query"
        mock_response.rerank_mode = None
        mock_response.search_time_ms = 100.0
        mock_response.fallback_triggered = False
        
        with patch.object(GraphService, 'search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_response
            
            response = await client.post(
                "/api/graph/search",
                json={
                    "query": "test query",
                    "group_id": "user:123",
                    "limit": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert data["query"] == "test query"
            assert len(data["results"]) == 1
            assert data["results"][0]["uuid"] == "paper_001"
    
    @pytest.mark.asyncio
    async def test_search_api_with_rerank(self, client: AsyncClient):
        """测试带重排的搜索API"""
        
        mock_response = Mock()
        mock_response.results = []
        mock_response.total = 0
        mock_response.query = "test"
        mock_response.rerank_mode = "rrf"
        mock_response.search_time_ms = 50.0
        mock_response.fallback_triggered = False
        
        with patch.object(GraphService, 'search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_response
            
            response = await client.post(
                "/api/graph/search",
                json={
                    "query": "test",
                    "group_id": "user:123",
                    "limit": 10,
                    "rerank_mode": "rrf"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["rerank_mode"] == "rrf"
    
    @pytest.mark.asyncio
    async def test_search_api_invalid_request(self, client: AsyncClient):
        """测试无效的搜索请求"""
        
        # 缺少必填字段query
        response = await client.post(
            "/api/graph/search",
            json={
                "group_id": "user:123",
                "limit": 10
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_search_api_empty_query(self, client: AsyncClient):
        """测试空查询字符串"""
        
        response = await client.post(
            "/api/graph/search",
            json={
                "query": "",  # 空查询
                "group_id": "user:123",
                "limit": 10
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_search_api_with_fallback(self, client: AsyncClient):
        """测试启用Fallback的搜索"""
        
        mock_response = Mock()
        mock_response.results = []
        mock_response.total = 0
        mock_response.query = "test"
        mock_response.rerank_mode = None
        mock_response.search_time_ms = 100.0
        mock_response.fallback_triggered = True
        
        with patch.object(GraphService, 'search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_response
            
            response = await client.post(
                "/api/graph/search",
                json={
                    "query": "test",
                    "group_id": "user:123",
                    "limit": 10,
                    "enable_fallback": True
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["fallback_triggered"] is True


class TestNodeDetailAPI:
    """测试节点详情API"""
    
    @pytest.mark.asyncio
    async def test_get_node_api_success(self, client: AsyncClient):
        """测试获取节点API成功响应"""
        
        mock_node = Mock()
        mock_node.uuid = "paper_001"
        mock_node.name = "Test Paper"
        mock_node.entity_type = "Paper"
        mock_node.properties = {"year": 2023}
        mock_node.summary = "Test summary"
        mock_node.neighbors = None
        mock_node.neighbor_count = 0
        
        with patch.object(GraphService, 'get_node_detail', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_node
            
            response = await client.get("/api/graph/node/paper_001")
            
            assert response.status_code == 200
            data = response.json()
            assert data["uuid"] == "paper_001"
            assert data["name"] == "Test Paper"
            assert data["entity_type"] == "Paper"
    
    @pytest.mark.asyncio
    async def test_get_node_api_with_neighbors(self, client: AsyncClient):
        """测试获取节点及邻居"""
        
        mock_neighbor = Mock()
        mock_neighbor.uuid = "method_001"
        mock_neighbor.name = "Test Method"
        mock_neighbor.entity_type = "Method"
        mock_neighbor.relation_type = "PROPOSES"
        mock_neighbor.direction = "outgoing"
        
        mock_node = Mock()
        mock_node.uuid = "paper_001"
        mock_node.name = "Test Paper"
        mock_node.entity_type = "Paper"
        mock_node.properties = {}
        mock_node.summary = "Test"
        mock_node.neighbors = [mock_neighbor]
        mock_node.neighbor_count = 1
        
        with patch.object(GraphService, 'get_node_detail', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_node
            
            response = await client.get(
                "/api/graph/node/paper_001",
                params={"include_neighbors": True, "neighbor_limit": 10}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["uuid"] == "paper_001"
            assert data["neighbors"] is not None
            assert len(data["neighbors"]) == 1
            assert data["neighbor_count"] == 1
    
    @pytest.mark.asyncio
    async def test_get_node_api_not_found(self, client: AsyncClient):
        """测试节点不存在"""
        
        with patch.object(GraphService, 'get_node_detail', side_effect=Exception("Not found")):
            response = await client.get("/api/graph/node/nonexistent")
            
            assert response.status_code == 404


class TestNeighborsAPI:
    """测试邻居查询API"""
    
    @pytest.mark.asyncio
    async def test_get_neighbors_api_success(self, client: AsyncClient):
        """测试获取邻居API成功响应"""
        
        mock_result = {
            "center_node": "paper_001",
            "neighbors": {
                "nodes": [
                    {
                        "uuid": "method_001",
                        "name": "Test Method",
                        "entity_type": "Method"
                    }
                ],
                "edges": [
                    {
                        "uuid": "edge_001",
                        "source_uuid": "paper_001",
                        "target_uuid": "method_001",
                        "relation_type": "PROPOSES"
                    }
                ]
            },
            "total": 1,
            "has_more": False
        }
        
        with patch.object(GraphService, 'get_neighbors', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_result
            
            response = await client.get("/api/graph/node/paper_001/neighbors")
            
            assert response.status_code == 200
            data = response.json()
            assert data["center_node"] == "paper_001"
            assert data["total"] == 1
            assert len(data["neighbors"]["nodes"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_neighbors_api_with_filters(self, client: AsyncClient):
        """测试带筛选的邻居查询"""
        
        mock_result = {
            "center_node": "paper_001",
            "neighbors": {"nodes": [], "edges": []},
            "total": 0,
            "has_more": False
        }
        
        with patch.object(GraphService, 'get_neighbors', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_result
            
            response = await client.get(
                "/api/graph/node/paper_001/neighbors",
                params={
                    "direction": "outgoing",
                    "node_types": "Method,Dataset",
                    "relation_types": "PROPOSES",
                    "limit": 20
                }
            )
            
            assert response.status_code == 200
            # 验证调用参数
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["direction"] == "outgoing"
            assert call_kwargs["node_types"] == ["Method", "Dataset"]
            assert call_kwargs["relation_types"] == ["PROPOSES"]
            assert call_kwargs["limit"] == 20
    
    @pytest.mark.asyncio
    async def test_get_neighbors_api_error(self, client: AsyncClient):
        """测试邻居查询API错误"""
        
        with patch.object(GraphService, 'get_neighbors', side_effect=Exception("Error")):
            response = await client.get("/api/graph/node/paper_001/neighbors")
            
            assert response.status_code == 500


class TestPathQueryAPI:
    """测试路径查询API"""
    
    @pytest.mark.asyncio
    async def test_find_path_api_success(self, client: AsyncClient):
        """测试路径查询API成功响应"""
        
        mock_response = Mock()
        mock_response.paths = []
        mock_response.total_paths = 0
        mock_response.shortest_length = None
        mock_response.query_time_ms = 50.0
        
        with patch.object(GraphService, 'find_paths', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_response
            
            response = await client.post(
                "/api/graph/path",
                json={
                    "source_uuid": "paper_001",
                    "target_uuid": "paper_002",
                    "max_depth": 5,
                    "limit": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "paths" in data
            assert "total_paths" in data
            assert "query_time_ms" in data
    
    @pytest.mark.asyncio
    async def test_find_path_api_with_results(self, client: AsyncClient):
        """测试找到路径的情况"""
        
        from app.schemas.graph import PathQueryResponse, Path as PathSchema, PathNode, PathEdge
        
        mock_response = PathQueryResponse(
            paths=[
                PathSchema(
                    nodes=[
                        PathNode(uuid="p1", name="Paper 1", entity_type="Paper"),
                        PathNode(uuid="p2", name="Paper 2", entity_type="Paper")
                    ],
                    edges=[
                        PathEdge(source_uuid="p1", target_uuid="p2", relation_type="CITES")
                    ],
                    length=1
                )
            ],
            total_paths=1,
            shortest_length=1,
            query_time_ms=100.0
        )
        
        with patch.object(GraphService, 'find_paths', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_response
            
            response = await client.post(
                "/api/graph/path",
                json={
                    "source_uuid": "paper_001",
                    "target_uuid": "paper_002",
                    "max_depth": 5,
                    "limit": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_paths"] == 1
            assert data["shortest_length"] == 1
    
    @pytest.mark.asyncio
    async def test_find_path_api_invalid_request(self, client: AsyncClient):
        """测试无效的路径查询请求"""
        
        # 缺少source_uuid
        response = await client.post(
            "/api/graph/path",
            json={
                "target_uuid": "paper_002",
                "max_depth": 5
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_find_path_api_error(self, client: AsyncClient):
        """测试路径查询API错误"""
        
        with patch.object(GraphService, 'find_paths', side_effect=Exception("Path error")):
            response = await client.post(
                "/api/graph/path",
                json={
                    "source_uuid": "paper_001",
                    "target_uuid": "paper_002",
                    "max_depth": 5,
                    "limit": 10
                }
            )
            
            assert response.status_code == 500


class TestDeprecatedEntityAPI:
    """测试已废弃的实体API"""
    
    @pytest.mark.asyncio
    async def test_get_entity_api_backward_compatible(self, client: AsyncClient):
        """测试向后兼容的实体API"""
        
        mock_entity = {"uuid": "paper_001", "name": "Test Paper"}
        
        with patch.object(GraphService, 'get_entity', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_entity
            
            response = await client.get("/api/graph/entity/paper_001")
            
            assert response.status_code == 200
            data = response.json()
            assert data["uuid"] == "paper_001"
    
    @pytest.mark.asyncio
    async def test_get_entity_api_not_found(self, client: AsyncClient):
        """测试实体不存在"""
        
        with patch.object(GraphService, 'get_entity', side_effect=Exception("Not found")):
            response = await client.get("/api/graph/entity/nonexistent")
            
            assert response.status_code == 404


class TestAPIValidation:
    """测试API参数验证"""
    
    @pytest.mark.asyncio
    async def test_search_limit_validation(self, client: AsyncClient):
        """测试搜索limit参数验证"""
        
        # limit超过最大值
        response = await client.post(
            "/api/graph/search",
            json={
                "query": "test",
                "group_id": "user:123",
                "limit": 101  # 超过最大值100
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_search_limit_too_small(self, client: AsyncClient):
        """测试limit太小"""
        
        response = await client.post(
            "/api/graph/search",
            json={
                "query": "test",
                "group_id": "user:123",
                "limit": 0  # 最小值是1
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_path_max_depth_validation(self, client: AsyncClient):
        """测试路径查询max_depth参数验证"""
        
        # max_depth超过最大值
        response = await client.post(
            "/api/graph/path",
            json={
                "source_uuid": "p1",
                "target_uuid": "p2",
                "max_depth": 11  # 超过最大值10
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_neighbor_limit_validation(self, client: AsyncClient):
        """测试邻居查询limit参数验证"""
        
        mock_result = {
            "center_node": "p1",
            "neighbors": {"nodes": [], "edges": []},
            "total": 0,
            "has_more": False
        }
        
        with patch.object(GraphService, 'get_neighbors', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_result
            
            # limit超过最大值
            response = await client.get(
                "/api/graph/node/paper_001/neighbors",
                params={"limit": 101}  # 超过最大值100
            )
            
            assert response.status_code == 422


class TestAPIErrorHandling:
    """测试API错误处理"""
    
    @pytest.mark.asyncio
    async def test_search_service_error(self, client: AsyncClient):
        """测试搜索服务错误"""
        
        with patch.object(GraphService, 'search', side_effect=Exception("Service error")):
            response = await client.post(
                "/api/graph/search",
                json={
                    "query": "test",
                    "group_id": "user:123",
                    "limit": 10
                }
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_malformed_json(self, client: AsyncClient):
        """测试错误的JSON格式"""
        
        response = await client.post(
            "/api/graph/search",
            content="not a json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422


class TestAPIIntegration:
    """测试API集成场景"""
    
    @pytest.mark.asyncio
    async def test_search_and_get_node_workflow(self, client: AsyncClient):
        """测试搜索后获取节点详情的工作流"""
        
        # 1. 搜索
        mock_search_response = Mock()
        mock_search_response.results = [
            SearchResult(
                uuid="paper_001",
                name="Test Paper",
                entity_type="Paper",
                score=0.95,
                summary="Test",
                properties={},
                source="user"
            )
        ]
        mock_search_response.total = 1
        mock_search_response.query = "test"
        mock_search_response.rerank_mode = None
        mock_search_response.search_time_ms = 100.0
        mock_search_response.fallback_triggered = False
        
        with patch.object(GraphService, 'search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_search_response
            
            search_response = await client.post(
                "/api/graph/search",
                json={"query": "test", "limit": 10}
            )
            
            assert search_response.status_code == 200
            search_data = search_response.json()
            paper_uuid = search_data["results"][0]["uuid"]
        
        # 2. 获取节点详情
        mock_node = Mock()
        mock_node.uuid = paper_uuid
        mock_node.name = "Test Paper"
        mock_node.entity_type = "Paper"
        mock_node.properties = {}
        mock_node.summary = "Test"
        mock_node.neighbors = None
        mock_node.neighbor_count = 0
        
        with patch.object(GraphService, 'get_node_detail', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_node
            
            node_response = await client.get(f"/api/graph/node/{paper_uuid}")
            
            assert node_response.status_code == 200
            node_data = node_response.json()
            assert node_data["uuid"] == paper_uuid


# Mock类用于测试
from unittest.mock import Mock

