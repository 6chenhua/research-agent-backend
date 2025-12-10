"""工具注册器"""
from typing import Dict
from .base import BaseTool

class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """注册工具"""
        self._tools[tool.name] = tool
    
    def get(self, tool_name: str) -> BaseTool:
        """获取工具"""
        return self._tools.get(tool_name)
    
    def list_tools(self):
        """列出所有工具"""
        return list(self._tools.keys())

# 全局工具注册器
tool_registry = ToolRegistry()
