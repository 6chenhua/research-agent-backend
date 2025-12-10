"""社区相关异步任务"""
from .worker import celery_app

@celery_app.task
def detect_communities_task(group_id: str):
    """异步社区检测任务"""
    # TODO: 实现异步社区检测
    pass

@celery_app.task
def rebuild_all_communities():
    """重建所有社区"""
    # TODO: 重建所有命名空间的社区
    pass
