"""论文对比工具"""
from .base import BaseTool, ToolInput, ToolOutput
from typing import List

class PaperCompareInput(ToolInput):
    paper_ids: List[str]

class PaperCompareOutput(ToolOutput):
    comparison: dict

class PaperCompareTool(BaseTool):
    """论文对比工具"""
    name = "paper_compare"
    description = "对比多篇论文的异同"
    
    async def execute(self, input_data: PaperCompareInput) -> PaperCompareOutput:
        # TODO: 实现论文对比
        return PaperCompareOutput(comparison={})
