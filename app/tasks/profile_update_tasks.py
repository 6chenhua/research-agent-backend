"""用户画像更新任务"""
from .worker import celery_app

@celery_app.task
def update_user_profile_task(user_id: str):
    """更新用户画像"""
    # TODO: 异步更新用户画像
    pass
