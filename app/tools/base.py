"""Tool基类"""
from abc import ABC, abstractmethod
from pydantic import BaseModel

class ToolInput(BaseModel):
    """工具输入基类"""
    pass

class ToolOutput(BaseModel):
    """工具输出基类"""
    pass

class BaseTool(ABC):
    """工具基类"""
    name: str
    description: str
    
    @abstractmethod
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """执行工具"""
        pass
