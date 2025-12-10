"""图谱查询工具"""
from .base import BaseTool, ToolInput, ToolOutput

class GraphQueryInput(ToolInput):
    query: str
    user_id: str

class GraphQueryOutput(ToolOutput):
    results: list

class GraphQueryTool(BaseTool):
    """图谱查询工具"""
    name = "graph_query"
    description = "在知识图谱中搜索相关信息"
    
    async def execute(self, input_data: GraphQueryInput) -> GraphQueryOutput:
        # TODO: 实现图谱查询
        return GraphQueryOutput(results=[])
