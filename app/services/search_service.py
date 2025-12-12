"""
搜索服务
提供对图谱搜索功能的简单包装

优化后使用增强版 Graphiti 客户端：
- ✅ 全局单例
- ✅ 并发控制
- ✅ 超时保护
- ✅ 性能监控
"""
from app.core.graphiti_enhanced import enhanced_graphiti


class SearchService:
    """搜索服务（使用增强版 Graphiti 客户端）
    
    提供简单的搜索接口包装
    """

    def __init__(self):
        # 使用增强版全局单例客户端
        self.graph = enhanced_graphiti

    async def search(
        self, 
        query: str, 
        user_id: str,  # ← 新增：用于并发控制
        group_id: str,
        limit: int = 10
    ):
        """执行搜索
        
        Args:
            query: 搜索查询
            user_id: 用户ID（用于并发控制和监控）
            group_id: 命名空间ID
            limit: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        return await self.graph.search(
            query=query,
            user_id=user_id,
            group_id=group_id,
            limit=limit
        )