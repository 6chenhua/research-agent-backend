"""arXiv同步任务"""
from .worker import celery_app

@celery_app.task
def sync_latest_papers(categories: list):
    """同步最新论文"""
    # TODO: 从arXiv同步最新论文
    pass

@celery_app.task
def daily_arxiv_update():
    """每日arXiv更新"""
    # TODO: 定时任务：每日更新
    pass
