"""自定义异常类"""

class GraphitiError(Exception):
    """Graphiti操作异常"""
    pass

class PDFParseError(Exception):
    """PDF解析异常"""
    pass

class EntityExtractionError(Exception):
    """实体抽取异常"""
    pass

class ExternalSearchError(Exception):
    """外部搜索异常"""
    pass
