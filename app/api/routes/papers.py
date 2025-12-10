"""Paper ingestion API router.
Handles uploading, parsing, and ingestion of research papers.
"""
from fastapi import APIRouter, UploadFile, Depends
from app.services.ingest_service import IngestService

router = APIRouter()

@router.post(
    "/upload",
    summary="Upload Research Paper (PDF)",
    description="Upload a PDF research paper; it will be parsed, chunked, converted into Graphiti Episodes, and added to the knowledge graph."
)
async def upload_paper(file: UploadFile, svc: IngestService = Depends()):
    """
    Upload and ingest a PDF for graph construction.

    Body:
    - **file**: PDF document

    Returns:
    - **status**: Parsing / ingestion status
    - **paper**: Extracted metadata (title, authors, etc.)
    """
    return await svc.ingest_pdf(file)