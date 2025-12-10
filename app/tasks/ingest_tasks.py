from .worker import celery_app
from app.services.ingest_service import IngestService


@celery_app.task
async def ingest_pdf_task(file_path: str):
    svc = IngestService()
    return await svc.process_file(file_path)
