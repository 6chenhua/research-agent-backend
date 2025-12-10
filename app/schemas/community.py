"""
社区相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import List, Optional


class Community(BaseModel):
    """社区信息"""
    community_id: str
    name: Optional[str] = None
    summary: Optional[str] = None
    node_count: int
    

class CommunityNode(BaseModel):
    """社区节点"""
    node_id: str
    node_type: str
    name: str

