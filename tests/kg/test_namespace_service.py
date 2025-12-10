"""
测试命名空间服务
包括用户命名空间、全局命名空间、Fallback机制等
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock

from app.services.namespace_service import NamespaceService


class TestGetUserNamespace:
    """测试获取用户命名空间"""
    
    def test_get_user_namespace(self):
        """测试获取用户命名空间"""
        service = NamespaceService()
        namespace = service.get_user_namespace("123")
        assert namespace == "user:123"
    
    def test_get_user_namespace_with_different_ids(self):
        """测试不同用户ID"""
        service = NamespaceService()
        assert service.get_user_namespace("123") == "user:123"
        assert service.get_user_namespace("456") == "user:456"
        assert service.get_user_namespace("abc") == "user:abc"
    
    def test_get_user_namespace_with_empty_id_fails(self):
        """测试空用户ID应该失败"""
        service = NamespaceService()
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            service.get_user_namespace("")


class TestGetGlobalNamespace:
    """测试获取全局命名空间"""
    
    def test_get_global_namespace(self):
        """测试获取全局命名空间"""
        service = NamespaceService()
        namespace = service.get_global_namespace()
        assert namespace == "global"


class TestParseNamespace:
    """测试解析命名空间"""
    
    def test_parse_global_namespace(self):
        """测试解析全局命名空间"""
        service = NamespaceService()
        result = service.parse_namespace("global")
        assert result["type"] == "global"
        assert result["user_id"] is None
    
    def test_parse_user_namespace(self):
        """测试解析用户命名空间"""
        service = NamespaceService()
        result = service.parse_namespace("user:123")
        assert result["type"] == "user"
        assert result["user_id"] == "123"
    
    def test_parse_user_namespace_with_various_ids(self):
        """测试解析各种用户ID"""
        service = NamespaceService()
        
        result1 = service.parse_namespace("user:abc")
        assert result1["user_id"] == "abc"
        
        result2 = service.parse_namespace("user:123-456")
        assert result2["user_id"] == "123-456"
    
    def test_parse_invalid_namespace_fails(self):
        """测试解析无效命名空间应该失败"""
        service = NamespaceService()
        
        with pytest.raises(ValueError, match="Invalid namespace format"):
            service.parse_namespace("invalid_format")
        
        with pytest.raises(ValueError, match="Invalid namespace format"):
            service.parse_namespace("user")
        
        with pytest.raises(ValueError, match="Invalid namespace format"):
            service.parse_namespace("admin:123")


class TestIsUserNamespace:
    """测试检查是否为用户命名空间"""
    
    def test_is_user_namespace_true(self):
        """测试用户命名空间返回True"""
        service = NamespaceService()
        assert service.is_user_namespace("user:123") is True
        assert service.is_user_namespace("user:abc") is True
    
    def test_is_user_namespace_false(self):
        """测试非用户命名空间返回False"""
        service = NamespaceService()
        assert service.is_user_namespace("global") is False
        assert service.is_user_namespace("invalid") is False


class TestIsGlobalNamespace:
    """测试检查是否为全局命名空间"""
    
    def test_is_global_namespace_true(self):
        """测试全局命名空间返回True"""
        service = NamespaceService()
        assert service.is_global_namespace("global") is True
    
    def test_is_global_namespace_false(self):
        """测试非全局命名空间返回False"""
        service = NamespaceService()
        assert service.is_global_namespace("user:123") is False
        assert service.is_global_namespace("invalid") is False


class TestGetFallbackChain:
    """测试获取Fallback搜索链"""
    
    def test_fallback_chain_with_user_id(self):
        """测试有用户ID的Fallback链"""
        service = NamespaceService()
        chain = service.get_fallback_chain("123")
        assert len(chain) == 2
        assert chain[0] == "user:123"
        assert chain[1] == "global"
    
    def test_fallback_chain_without_user_id(self):
        """测试没有用户ID的Fallback链"""
        service = NamespaceService()
        chain = service.get_fallback_chain(None)
        assert len(chain) == 1
        assert chain[0] == "global"
    
    def test_fallback_chain_order(self):
        """测试Fallback链的顺序"""
        service = NamespaceService()
        chain = service.get_fallback_chain("456")
        # 应该先搜索用户图谱，再搜索全局图谱
        assert chain[0] == "user:456"
        assert chain[1] == "global"


class TestSearchWithFallback:
    """测试多层级搜索"""
    
    @pytest.mark.asyncio
    async def test_search_with_fallback_user_results_sufficient(self):
        """测试用户图谱结果充足时不触发Fallback"""
        service = NamespaceService()
        
        # Mock搜索函数：用户图谱返回足够结果
        async def mock_search(query, group_id):
            if group_id == "user:123":
                return [
                    {"uuid": "u1", "name": "Result 1"},
                    {"uuid": "u2", "name": "Result 2"},
                    {"uuid": "u3", "name": "Result 3"},
                    {"uuid": "u4", "name": "Result 4"},
                    {"uuid": "u5", "name": "Result 5"},
                ]
            return []
        
        results = await service.search_with_fallback(
            query="test query",
            user_id="123",
            search_func=mock_search,
            min_results=5
        )
        
        assert len(results) == 5
        # 所有结果都来自用户图谱
        for result in results:
            assert result["source_namespace"] == "user:123"
    
    @pytest.mark.asyncio
    async def test_search_with_fallback_triggers_global_search(self):
        """测试用户图谱结果不足时触发全局搜索"""
        service = NamespaceService()
        
        # Mock搜索函数：用户图谱结果不足，需要全局图谱
        async def mock_search(query, group_id):
            if group_id == "user:123":
                return [
                    {"uuid": "u1", "name": "User Result 1"},
                    {"uuid": "u2", "name": "User Result 2"},
                ]
            elif group_id == "global":
                return [
                    {"uuid": "g1", "name": "Global Result 1"},
                    {"uuid": "g2", "name": "Global Result 2"},
                    {"uuid": "g3", "name": "Global Result 3"},
                ]
            return []
        
        results = await service.search_with_fallback(
            query="test query",
            user_id="123",
            search_func=mock_search,
            min_results=5
        )
        
        assert len(results) == 5
        # 前2个来自用户图谱，后3个来自全局图谱
        assert results[0]["source_namespace"] == "user:123"
        assert results[1]["source_namespace"] == "user:123"
        assert results[2]["source_namespace"] == "global"
        assert results[3]["source_namespace"] == "global"
        assert results[4]["source_namespace"] == "global"
    
    @pytest.mark.asyncio
    async def test_search_with_fallback_no_user_id(self):
        """测试没有用户ID时直接搜索全局图谱"""
        service = NamespaceService()
        
        async def mock_search(query, group_id):
            if group_id == "global":
                return [{"uuid": "g1", "name": "Global Result"}]
            return []
        
        results = await service.search_with_fallback(
            query="test query",
            user_id=None,
            search_func=mock_search,
            min_results=1
        )
        
        assert len(results) == 1
        assert results[0]["source_namespace"] == "global"
    
    @pytest.mark.asyncio
    async def test_search_with_fallback_handles_errors(self):
        """测试搜索出错时继续Fallback"""
        service = NamespaceService()
        
        async def mock_search(query, group_id):
            if group_id == "user:123":
                raise Exception("User namespace error")
            elif group_id == "global":
                return [{"uuid": "g1", "name": "Global Result"}]
            return []
        
        results = await service.search_with_fallback(
            query="test query",
            user_id="123",
            search_func=mock_search,
            min_results=1
        )
        
        # 用户图谱出错，但全局图谱成功
        assert len(results) == 1
        assert results[0]["source_namespace"] == "global"


class TestValidateNamespaceAccess:
    """测试命名空间访问权限验证"""
    
    def test_access_own_namespace(self):
        """测试访问自己的命名空间"""
        service = NamespaceService()
        assert service.validate_namespace_access("user:123", "123") is True
    
    def test_access_other_user_namespace_denied(self):
        """测试访问其他用户命名空间被拒绝"""
        service = NamespaceService()
        assert service.validate_namespace_access("user:456", "123") is False
    
    def test_access_global_namespace_allowed(self):
        """测试访问全局命名空间总是允许"""
        service = NamespaceService()
        assert service.validate_namespace_access("global", "123") is True
        assert service.validate_namespace_access("global", "456") is True
        assert service.validate_namespace_access("global", "any_user") is True
    
    def test_access_invalid_namespace(self):
        """测试访问无效命名空间"""
        service = NamespaceService()
        assert service.validate_namespace_access("invalid_format", "123") is False


class TestNamespaceServiceIntegration:
    """测试命名空间服务集成场景"""
    
    def test_complete_user_workflow(self):
        """测试完整的用户工作流"""
        service = NamespaceService()
        user_id = "test_user_123"
        
        # 1. 获取用户命名空间
        user_ns = service.get_user_namespace(user_id)
        assert user_ns == f"user:{user_id}"
        
        # 2. 验证命名空间类型
        assert service.is_user_namespace(user_ns) is True
        assert service.is_global_namespace(user_ns) is False
        
        # 3. 解析命名空间
        parsed = service.parse_namespace(user_ns)
        assert parsed["type"] == "user"
        assert parsed["user_id"] == user_id
        
        # 4. 验证访问权限
        assert service.validate_namespace_access(user_ns, user_id) is True
        assert service.validate_namespace_access(user_ns, "other_user") is False
    
    def test_fallback_chain_generation(self):
        """测试Fallback链生成"""
        service = NamespaceService()
        
        # 有用户ID的场景
        chain_with_user = service.get_fallback_chain("user123")
        assert len(chain_with_user) == 2
        assert chain_with_user[0].startswith("user:")
        assert chain_with_user[1] == "global"
        
        # 没有用户ID的场景
        chain_without_user = service.get_fallback_chain(None)
        assert len(chain_without_user) == 1
        assert chain_without_user[0] == "global"


class TestEdgeCases:
    """测试边界情况"""
    
    def test_special_characters_in_user_id(self):
        """测试用户ID中的特殊字符"""
        service = NamespaceService()
        
        # 包含连字符
        ns1 = service.get_user_namespace("user-123-456")
        assert ns1 == "user:user-123-456"
        parsed1 = service.parse_namespace(ns1)
        assert parsed1["user_id"] == "user-123-456"
        
        # 包含下划线
        ns2 = service.get_user_namespace("user_abc_def")
        assert ns2 == "user:user_abc_def"
    
    def test_very_long_user_id(self):
        """测试很长的用户ID"""
        service = NamespaceService()
        long_id = "a" * 100
        ns = service.get_user_namespace(long_id)
        assert ns == f"user:{long_id}"
        
        parsed = service.parse_namespace(ns)
        assert parsed["user_id"] == long_id
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self):
        """测试搜索结果为空的情况"""
        service = NamespaceService()
        
        async def mock_search_empty(query, group_id):
            return []
        
        results = await service.search_with_fallback(
            query="test",
            user_id="123",
            search_func=mock_search_empty,
            min_results=5
        )
        
        assert len(results) == 0

