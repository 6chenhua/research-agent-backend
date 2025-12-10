"""社区API路由"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="获取社区列表")
async def get_communities(group_id: str = "global"):
    """获取图谱中的社区列表"""
    return {"communities": [], "status": "TODO"}
