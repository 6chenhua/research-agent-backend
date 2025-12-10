"""
图谱相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import List, Optional


class GraphSearchRequest(BaseModel):
    """图谱搜索请求"""
    query: str
    group_id: str


class GraphSearchResponse(BaseModel):
    """图谱搜索响应"""
    results: List[dict]

