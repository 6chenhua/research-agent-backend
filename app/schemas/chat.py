"""
聊天相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """聊天请求"""
    user_id: str
    message: str


class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str

