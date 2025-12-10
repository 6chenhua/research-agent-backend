"""命名空间管理服务
管理知识图谱的命名空间，支持用户私有图谱和全局共享图谱
"""
from typing import List, Dict, Any, Optional
from app.core.constants import GLOBAL_NAMESPACE, USER_NAMESPACE_PREFIX
import logging

logger = logging.getLogger(__name__)


class NamespaceService:
    """图谱命名空间管理
    
    提供用户私有图谱和全局图谱的隔离和Fallback机制
    """
    
    def get_user_namespace(self, user_id: str) -> str:
        """获取用户命名空间
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户命名空间字符串（格式：user:<user_id>）
            
        Example:
            >>> ns = NamespaceService()
            >>> ns.get_user_namespace("123")
            'user:123'
        """
        if not user_id:
            raise ValueError("User ID cannot be empty")
        return f"{USER_NAMESPACE_PREFIX}{user_id}"
    
    def get_global_namespace(self) -> str:
        """获取全局命名空间
        
        Returns:
            全局命名空间字符串
        """
        return GLOBAL_NAMESPACE
    
    def parse_namespace(self, namespace: str) -> Dict[str, Any]:
        """解析命名空间字符串
        
        Args:
            namespace: 命名空间字符串
            
        Returns:
            解析后的命名空间信息
            
        Example:
            >>> ns = NamespaceService()
            >>> ns.parse_namespace("user:123")
            {'type': 'user', 'user_id': '123'}
            >>> ns.parse_namespace("global")
            {'type': 'global', 'user_id': None}
        """
        if namespace == GLOBAL_NAMESPACE:
            return {
                'type': 'global',
                'user_id': None
            }
        elif namespace.startswith(USER_NAMESPACE_PREFIX):
            user_id = namespace[len(USER_NAMESPACE_PREFIX):]
            return {
                'type': 'user',
                'user_id': user_id
            }
        else:
            raise ValueError(f"Invalid namespace format: {namespace}")
    
    def is_user_namespace(self, namespace: str) -> bool:
        """检查是否为用户命名空间
        
        Args:
            namespace: 命名空间字符串
            
        Returns:
            是否为用户命名空间
        """
        return namespace.startswith(USER_NAMESPACE_PREFIX)
    
    def is_global_namespace(self, namespace: str) -> bool:
        """检查是否为全局命名空间
        
        Args:
            namespace: 命名空间字符串
            
        Returns:
            是否为全局命名空间
        """
        return namespace == GLOBAL_NAMESPACE
    
    def get_fallback_chain(self, user_id: Optional[str] = None) -> List[str]:
        """获取Fallback搜索链
        
        定义搜索的优先级顺序：
        1. 用户私有图谱（如果提供了user_id）
        2. 全局共享图谱
        
        Args:
            user_id: 用户ID（可选）
            
        Returns:
            命名空间列表，按优先级排序
            
        Example:
            >>> ns = NamespaceService()
            >>> ns.get_fallback_chain("123")
            ['user:123', 'global']
            >>> ns.get_fallback_chain()
            ['global']
        """
        chain = []
        
        if user_id:
            chain.append(self.get_user_namespace(user_id))
        
        chain.append(self.get_global_namespace())
        
        return chain
    
    async def search_with_fallback(
        self, 
        query: str, 
        user_id: Optional[str],
        search_func,
        min_results: int = 5
    ) -> List[Dict[str, Any]]:
        """多层级搜索：用户图谱 -> 全局图谱
        
        实现智能Fallback机制，当用户图谱结果不足时自动搜索全局图谱
        
        Args:
            query: 搜索查询
            user_id: 用户ID
            search_func: 搜索函数（接收query和group_id参数）
            min_results: 最小结果数量，低于此值触发Fallback
            
        Returns:
            搜索结果列表
            
        Example:
            >>> async def my_search(query, group_id):
            ...     return [...]
            >>> results = await ns.search_with_fallback("transformer", "123", my_search)
        """
        all_results = []
        fallback_chain = self.get_fallback_chain(user_id)
        
        for namespace in fallback_chain:
            try:
                logger.info(f"Searching in namespace: {namespace}")
                results = await search_func(query, namespace)
                
                # 标记结果来源
                for result in results:
                    result['source_namespace'] = namespace
                
                all_results.extend(results)
                
                # 如果结果充足，停止Fallback
                if len(all_results) >= min_results:
                    break
                    
            except Exception as e:
                logger.error(f"Search error in namespace {namespace}: {str(e)}")
                continue
        
        return all_results
    
    def validate_namespace_access(self, namespace: str, current_user_id: str) -> bool:
        """验证用户是否有权访问指定命名空间
        
        Args:
            namespace: 命名空间字符串
            current_user_id: 当前用户ID
            
        Returns:
            是否有权限访问
            
        Example:
            >>> ns = NamespaceService()
            >>> ns.validate_namespace_access("user:123", "123")
            True
            >>> ns.validate_namespace_access("user:456", "123")
            False
            >>> ns.validate_namespace_access("global", "123")
            True
        """
        # 全局命名空间所有人都能访问
        if self.is_global_namespace(namespace):
            return True
        
        # 用户只能访问自己的命名空间
        if self.is_user_namespace(namespace):
            namespace_info = self.parse_namespace(namespace)
            return namespace_info['user_id'] == current_user_id
        
        return False
