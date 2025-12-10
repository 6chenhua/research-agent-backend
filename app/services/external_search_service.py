"""外部搜索服务"""

class ExternalSearchService:
    """外部论文搜索服务（arXiv + Semantic Scholar）"""
    
    def __init__(self):
        # TODO: 初始化外部API客户端
        pass
    
    async def search(self, query: str, source: str = "arxiv", max_results: int = 10):
        """
        外部搜索
        :param query: 搜索关键词
        :param source: 数据源 (arxiv/s2)
        :param max_results: 最大结果数
        """
        # TODO: 实现外部搜索
        pass
    
    async def search_and_ingest(self, query: str, user_id: str):
        """搜索并自动摄入图谱"""
        # TODO: 搜索 -> 下载PDF -> 摄入
        pass
