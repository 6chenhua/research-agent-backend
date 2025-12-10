"""可视化API路由"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/graph/user/{user_id}", summary="获取用户知识图谱数据")
async def get_user_graph_data(user_id: str):
    """导出用户知识图谱可视化数据"""
    return {"nodes": [], "edges": [], "status": "TODO"}
