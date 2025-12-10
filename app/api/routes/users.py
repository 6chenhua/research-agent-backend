"""用户API路由"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/{user_id}/profile", summary="获取用户画像")
async def get_user_profile(user_id: str):
    """获取用户的研究画像"""
    return {"user_id": user_id, "status": "TODO"}
