"""
历史记录相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List


class ChatMessage(BaseModel):
    """聊天消息"""
    user_id: str
    message: str
    response: str
    timestamp: datetime
    

class ChatHistory(BaseModel):
    """聊天历史"""
    user_id: str
    messages: List[ChatMessage]

