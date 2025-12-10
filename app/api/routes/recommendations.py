"""推荐API路由"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/papers/{user_id}", summary="论文推荐")
async def recommend_papers(user_id: str, limit: int = 10):
    """为用户推荐相关论文"""
    return {"recommendations": [], "status": "TODO"}
