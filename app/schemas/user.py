"""
用户相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import List, Optional


class UserProfile(BaseModel):
    """用户画像"""
    user_id: str
    interests: List[str] = []
    research_direction: Optional[str] = None
    

class UserInterest(BaseModel):
    """用户兴趣"""
    topic: str
    weight: float

