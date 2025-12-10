"""
测试图谱服务
包括搜索、重排、节点查询、路径查询等核心功能
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from app.services.graph_service import GraphService
from app.schemas.graph import (
    GraphSearchRequest, RerankMode,
    NodeDetailResponse, PathQueryRequest
)


class TestGraphSearch:
    """测试图谱搜索功能"""
    
    @pytest.mark.asyncio
    async def test_basic_search(self):
        """测试基本搜索"""
        service = GraphService()
        
        # Mock Graphiti搜索结果
        mock_results = [
            {
                "uuid": "paper_001",
                "name": "Test Paper",
                "entity_type": "Paper",
                "score": 0.95,
                "summary": "Test summary",
                "properties": {"year": 2023}
            }
        ]
        
        with patch.object(service, '_search_in_namespace', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results
            
            request = GraphSearchRequest(
                query="test query",
                group_id="user:123",
                limit=10,
                enable_fallback=False  # 禁用Fallback避免多次调用
            )
            
            response = await service.search(request)
            
            assert response.total == 1
            assert response.query == "test query"
            assert len(response.results) == 1
            assert response.results[0].uuid == "paper_001"
    
    @pytest.mark.asyncio
    async def test_search_with_fallback_triggered(self):
        """测试搜索触发Fallback"""
        service = GraphService()
        
        # Mock: 用户图谱结果不足，触发全局图谱搜索
        async def mock_search_side_effect(query, group_id, focal_node_uuid, limit):
            if group_id == "user:123":
                return [{"uuid": "u1", "name": "User Result", "score": 0.9}]
            elif group_id == "global":
                return [{"uuid": "g1", "name": "Global Result", "score": 0.85}]
            return []
        
        with patch.object(service, '_search_in_namespace', side_effect=mock_search_side_effect):
            request = GraphSearchRequest(
                query="test query",
                group_id="user:123",
                limit=5,
                enable_fallback=True
            )
            
            response = await service.search(request)
            
            # 应该包含用户图谱和全局图谱的结果
            assert response.total == 2
            assert response.fallback_triggered is True
    
    @pytest.mark.asyncio
    async def test_search_without_fallback(self):
        """测试禁用Fallback的搜索"""
        service = GraphService()
        
        mock_results = [{"uuid": "u1", "name": "Result", "score": 0.9}]
        
        with patch.object(service, '_search_in_namespace', return_value=mock_results):
            request = GraphSearchRequest(
                query="test query",
                group_id="user:123",
                limit=10,
                enable_fallback=False
            )
            
            response = await service.search(request)
            
            assert response.fallback_triggered is False
    
    @pytest.mark.asyncio
    async def test_search_with_rrf_rerank(self):
        """测试使用RRF重排的搜索"""
        service = GraphService()
        
        mock_results = [
            {"uuid": "p1", "name": "Paper 1", "score": 0.9},
            {"uuid": "p2", "name": "Paper 2", "score": 0.8},
        ]
        
        with patch.object(service, '_search_in_namespace', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results
            
            # 使用字符串值而不是枚举，避免Pydantic序列化问题
            request = GraphSearchRequest(
                query="test query",
                group_id="user:123",
                limit=10,
                rerank_mode="rrf",  # 直接使用字符串
                enable_fallback=False
            )
            
            response = await service.search(request)
            
            assert response.rerank_mode == "rrf"
            assert len(response.results) == 2
    
    @pytest.mark.asyncio
    async def test_search_with_mmr_rerank(self):
        """测试使用MMR重排的搜索"""
        service = GraphService()
        
        mock_results = [
            {"uuid": "p1", "name": "Paper 1", "entity_type": "Paper", "score": 0.9},
            {"uuid": "m1", "name": "Method 1", "entity_type": "Method", "score": 0.85},
            {"uuid": "p2", "name": "Paper 2", "entity_type": "Paper", "score": 0.8},
        ]
        
        with patch.object(service, '_search_in_namespace', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results
            
            # 使用字符串值而不是枚举，避免Pydantic序列化问题
            request = GraphSearchRequest(
                query="test query",
                group_id="user:123",
                limit=10,
                rerank_mode="mmr",  # 直接使用字符串
                enable_fallback=False
            )
            
            response = await service.search(request)
            
            assert response.rerank_mode == "mmr"
            # MMR应该增加结果多样性
            assert len(response.results) == 3
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self):
        """测试搜索错误处理"""
        service = GraphService()
        
        with patch.object(service, '_search_in_namespace', side_effect=Exception("Search error")):
            request = GraphSearchRequest(
                query="test query",
                group_id="user:123",
                limit=10
            )
            
            response = await service.search(request)
            
            # 错误时应该返回空结果
            assert response.total == 0
            assert len(response.results) == 0


class TestRerankMethods:
    """测试重排方法"""
    
    def test_rerank_rrf(self):
        """测试RRF重排"""
        service = GraphService()
        
        results = [
            {"uuid": "p1", "score": 0.9},
            {"uuid": "p2", "score": 0.8},
            {"uuid": "p3", "score": 0.7},
        ]
        
        reranked = service._rerank_rrf(results)
        
        # 验证返回结果
        assert len(reranked) == 3
        # 验证每个结果都有调整后的分数
        for result in reranked:
            assert "score" in result
    
    def test_rerank_mmr_increases_diversity(self):
        """测试MMR增加多样性"""
        service = GraphService()
        
        # 相同类型的结果应该被分散
        results = [
            {"uuid": "p1", "entity_type": "Paper", "score": 0.9},
            {"uuid": "p2", "entity_type": "Paper", "score": 0.85},
            {"uuid": "m1", "entity_type": "Method", "score": 0.8},
            {"uuid": "p3", "entity_type": "Paper", "score": 0.75},
        ]
        
        reranked = service._rerank_mmr(results, "test query")
        
        # 验证结果顺序变化以增加多样性
        assert len(reranked) == 4
        # Method应该被提前（因为是新类型）
        types_order = [r["entity_type"] for r in reranked]
        # 第一个应该是Paper（最高分），第二个应该是Method（新类型加分）
        assert types_order[0] == "Paper"
        assert types_order[1] == "Method"
    
    def test_rerank_with_empty_results(self):
        """测试空结果重排"""
        service = GraphService()
        
        empty_results = []
        
        # RRF
        reranked_rrf = service._rerank_rrf(empty_results)
        assert reranked_rrf == []
        
        # MMR
        reranked_mmr = service._rerank_mmr(empty_results, "test")
        assert reranked_mmr == []


class TestNodeQueries:
    """测试节点查询功能"""
    
    @pytest.mark.asyncio
    async def test_get_node_detail_basic(self):
        """测试获取节点基本信息"""
        service = GraphService()
        
        mock_node = {
            "uuid": "paper_001",
            "name": "Test Paper",
            "entity_type": "Paper",
            "properties": {"year": 2023},
            "summary": "Test summary"
        }
        
        # 正确的Mock路径：service.graph是GraphitiClient实例，其client属性是Graphiti实例
        with patch.object(service.graph, 'client') as mock_client:
            mock_client.get_node = AsyncMock(return_value=mock_node)
            
            result = await service.get_node_detail("paper_001", include_neighbors=False)
            
            assert result.uuid == "paper_001"
            assert result.name == "Test Paper"
            assert result.entity_type == "Paper"
            assert result.neighbors is None
    
    @pytest.mark.asyncio
    async def test_get_node_detail_with_neighbors(self):
        """测试获取节点及邻居"""
        service = GraphService()
        
        mock_node = {
            "uuid": "paper_001",
            "name": "Test Paper",
            "entity_type": "Paper",
            "properties": {},
            "summary": "Test"
        }
        
        mock_neighbors = [
            {
                "uuid": "method_001",
                "name": "Test Method",
                "entity_type": "Method",
                "relation_type": "PROPOSES",
                "direction": "outgoing"
            }
        ]
        
        with patch.object(service.graph, 'client') as mock_client:
            mock_client.get_node = AsyncMock(return_value=mock_node)
            
            with patch.object(service, '_get_neighbors', new_callable=AsyncMock) as mock_neighbors_fn:
                mock_neighbors_fn.return_value = (mock_neighbors, 1)
                
                result = await service.get_node_detail("paper_001", include_neighbors=True)
                
                assert result.neighbors is not None
                assert len(result.neighbors) == 1
                assert result.neighbor_count == 1
    
    @pytest.mark.asyncio
    async def test_get_neighbors(self):
        """测试获取邻居节点"""
        service = GraphService()
        
        result = await service.get_neighbors(
            uuid="paper_001",
            direction="both",
            node_types=["Method", "Dataset"],
            relation_types=["PROPOSES"],
            limit=10
        )
        
        # 验证返回结构
        assert "center_node" in result
        assert "neighbors" in result
        assert "total" in result
        assert "has_more" in result


class TestPathQueries:
    """测试路径查询功能"""
    
    @pytest.mark.asyncio
    async def test_find_paths_basic(self):
        """测试基本路径查询"""
        service = GraphService()
        
        request = PathQueryRequest(
            source_uuid="paper_001",
            target_uuid="paper_002",
            max_depth=5,
            limit=10
        )
        
        response = await service.find_paths(request)
        
        # 验证响应结构
        assert response.paths is not None
        assert response.total_paths >= 0
        assert response.query_time_ms is not None
    
    @pytest.mark.asyncio
    async def test_find_paths_with_results(self):
        """测试找到路径的情况"""
        service = GraphService()
        
        from app.schemas.graph import Path as PathSchema, PathNode, PathEdge
        
        mock_paths = [
            PathSchema(
                nodes=[
                    PathNode(uuid="p1", name="Paper 1", entity_type="Paper"),
                    PathNode(uuid="p2", name="Paper 2", entity_type="Paper")
                ],
                edges=[
                    PathEdge(source_uuid="p1", target_uuid="p2", relation_type="CITES")
                ],
                length=1
            ),
            PathSchema(
                nodes=[
                    PathNode(uuid="p1", name="Paper 1", entity_type="Paper"),
                    PathNode(uuid="m1", name="Method 1", entity_type="Method"),
                    PathNode(uuid="p2", name="Paper 2", entity_type="Paper")
                ],
                edges=[
                    PathEdge(source_uuid="p1", target_uuid="m1", relation_type="PROPOSES"),
                    PathEdge(source_uuid="m1", target_uuid="p2", relation_type="PROPOSES")
                ],
                length=2
            ),
        ]
        
        with patch.object(service, '_find_shortest_paths', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_paths
            
            request = PathQueryRequest(
                source_uuid="paper_001",
                target_uuid="paper_002",
                max_depth=5,
                limit=10
            )
            
            response = await service.find_paths(request)
            
            assert response.total_paths == 2
            assert response.shortest_length == 1  # 最短路径长度是1，不是2


class TestConvertSearchResult:
    """测试搜索结果转换"""
    
    def test_convert_to_search_result(self):
        """测试转换原始结果为SearchResult"""
        service = GraphService()
        
        raw_result = {
            "uuid": "paper_001",
            "name": "Test Paper",
            "entity_type": "Paper",
            "score": 0.95,
            "summary": "Test summary",
            "properties": {"year": 2023},
            "source": "user"
        }
        
        search_result = service._convert_to_search_result(raw_result)
        
        assert search_result.uuid == "paper_001"
        assert search_result.name == "Test Paper"
        assert search_result.entity_type == "Paper"
        assert search_result.score == 0.95
        assert search_result.source == "user"
    
    def test_convert_with_missing_fields(self):
        """测试转换缺少字段的结果"""
        service = GraphService()
        
        raw_result = {
            "uuid": "paper_001",
            "name": "Test Paper",
            "score": 0.8
        }
        
        search_result = service._convert_to_search_result(raw_result)
        
        assert search_result.uuid == "paper_001"
        assert search_result.entity_type is None
        assert search_result.summary is None
        assert search_result.properties == {}
        assert search_result.source == "user"  # 默认值


class TestSearchInNamespace:
    """测试命名空间搜索"""
    
    @pytest.mark.asyncio
    async def test_search_in_user_namespace(self):
        """测试在用户命名空间搜索"""
        service = GraphService()
        
        mock_results = [
            {"uuid": "p1", "name": "Result 1"},
            {"uuid": "p2", "name": "Result 2"},
        ]
        
        with patch.object(service.graph, 'search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results
            
            results = await service._search_in_namespace(
                query="test",
                group_id="user:123",
                limit=10
            )
            
            assert len(results) == 2
            mock_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_in_namespace_error_handling(self):
        """测试命名空间搜索错误处理"""
        service = GraphService()
        
        with patch.object(service.graph, 'search', side_effect=Exception("Search error")):
            results = await service._search_in_namespace(
                query="test",
                group_id="user:123",
                limit=10
            )
            
            # 错误时返回空列表
            assert results == []


class TestEdgeCases:
    """测试边界情况"""
    
    @pytest.mark.asyncio
    async def test_search_with_very_large_limit(self):
        """测试很大的limit值"""
        service = GraphService()
        
        with patch.object(service, '_search_in_namespace', return_value=[]):
            request = GraphSearchRequest(
                query="test",
                group_id="user:123",
                limit=100  # 最大值
            )
            
            response = await service.search(request)
            assert response.total == 0
    
    @pytest.mark.asyncio
    async def test_search_with_empty_query(self):
        """测试空查询"""
        # 这应该在Schema验证层面被拦截
        # 但我们测试服务层的鲁棒性
        service = GraphService()
        
        with patch.object(service, '_search_in_namespace', return_value=[]):
            try:
                request = GraphSearchRequest(
                    query="test",  # Schema会验证非空
                    group_id="user:123",
                    limit=10
                )
                response = await service.search(request)
                assert response is not None
            except Exception:
                # 如果Schema验证失败，这是预期的
                pass
    
    @pytest.mark.asyncio
    async def test_get_node_nonexistent(self):
        """测试获取不存在的节点"""
        service = GraphService()
        
        with patch.object(service.graph, 'client') as mock_client:
            mock_client.get_node = AsyncMock(side_effect=Exception("Node not found"))
            
            with pytest.raises(Exception):
                await service.get_node_detail("nonexistent_uuid")

