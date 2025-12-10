"""外部搜索工具"""
from .base import BaseTool, ToolInput, ToolOutput

class ExternalSearchInput(ToolInput):
    query: str

class ExternalSearchOutput(ToolOutput):
    papers: list

class ExternalSearchTool(BaseTool):
    """外部搜索工具"""
    name = "external_search"
    description = "在arXiv等外部数据源搜索论文"
    
    async def execute(self, input_data: ExternalSearchInput) -> ExternalSearchOutput:
        # TODO: 实现外部搜索
        return ExternalSearchOutput(papers=[])
