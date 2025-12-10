"""历史记录API路由"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/chat/{user_id}", summary="获取聊天历史")
async def get_chat_history(user_id: str, limit: int = 50):
    """获取用户的聊天历史"""
    return {"user_id": user_id, "history": [], "status": "TODO"}
