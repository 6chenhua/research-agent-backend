from typing import Optional

from pydantic import BaseModel


class AddToNotesRequest(BaseModel):
    """添加到笔记的请求"""
    note: Optional[str] = None


class AddToNotesResponse(BaseModel):
    """添加到笔记的响应"""
    message_id: str
    status: str
    episode_name: str