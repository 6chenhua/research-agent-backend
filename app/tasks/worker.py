from celery import Celery

celery_app = Celery(
    "worker", backend="redis://localhost", broker="redis://localhost"
)
