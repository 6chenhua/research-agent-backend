"""
推荐相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import List


class PaperRecommendation(BaseModel):
    """论文推荐"""
    paper_id: str
    title: str
    score: float
    reason: str
    

class DirectionRecommendation(BaseModel):
    """研究方向推荐"""
    direction: str
    relevance: float
    papers: List[str]

