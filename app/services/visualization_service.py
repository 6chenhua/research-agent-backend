"""可视化服务"""

class VisualizationService:
    """图谱可视化数据导出"""
    
    async def export_graph_data(self, group_id: str, format: str = "json"):
        """导出图谱数据"""
        pass
    
    async def get_community_graph(self, community_id: str):
        """获取社区图数据"""
        pass
    
    async def get_paper_relations_graph(self, paper_id: str):
        """获取论文关系图"""
        pass
