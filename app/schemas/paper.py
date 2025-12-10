"""
论文相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import List, Optional


class PaperMetadata(BaseModel):
    """论文元数据"""
    title: str
    authors: List[str] = []
    year: Optional[int] = None

