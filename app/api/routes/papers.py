"""
Paper ingestion API router.
Handles uploading, parsing, and ingestion of research papers.

API端点：
- POST /api/papers/upload - 上传论文PDF
- GET /api/papers/{paper_id} - 获取论文详情
"""
from fastapi import APIRouter, UploadFile, Depends, HTTPException, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.services.ingest_service import IngestService
from app.api.dependencies.auth import get_current_user
from app.core.database import get_session
from app.schemas.paper import PaperUploadResponse, PaperDetailResponse
from app.models.db_models import User

router = APIRouter(tags=["Papers"])


@router.post(
    "/upload",
    response_model=PaperUploadResponse,
    summary="Upload Research Paper (PDF)",
    description="""
    Upload a PDF research paper for ingestion into knowledge graph.
    
    Process:
    1. Parse PDF using deepdoc
    2. Extract metadata, sections, references
    3. Add sections as Episodes to Graphiti
    4. Graphiti automatically extracts entities and relationships
    5. Save metadata to database
    
    Limits:
    - File size: < 50MB
    - Format: PDF only
    """
)
async def upload_paper(
    file: UploadFile = File(..., description="PDF file to upload"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Upload and ingest a PDF for graph construction.

    Args:
        file: PDF document
        current_user: Current authenticated user
        db: Database session

    Returns:
        PaperUploadResponse with paper_id, title, status, etc.
    
    Raises:
        400: Invalid file format or size
        500: Ingestion failed
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"📄 Uploading paper: {file.filename} for user: {current_user.user_id}")
        
        # 创建摄入服务
        ingest_service = IngestService(db=db)
        
        # 摄入PDF
        result = await ingest_service.ingest_pdf(
            file=file,
            user_id=current_user.user_id
        )
        
        logger.info(f"✅ Paper uploaded successfully: {result.get('paper_id')}")
        return result
        
    except HTTPException:
        # 重新抛出HTTPException
        raise
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload paper: {str(e)}"
        )


@router.get(
    "/{paper_id}",
    response_model=PaperDetailResponse,
    summary="Get Paper Details",
    description="""
    Retrieve complete information about a paper.
    
    Includes:
    - Metadata (title, authors, abstract, etc.)
    - Extracted entities from knowledge graph
    - Related papers recommendations
    """
)
async def get_paper_detail(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get detailed information about a specific paper.

    Args:
        paper_id: Paper ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        PaperDetailResponse with full paper information
    
    Raises:
        404: Paper not found
        500: Failed to retrieve details
    """
    # 创建摄入服务
    ingest_service = IngestService(db=db)
    
    # 获取论文详情
    paper_detail = await ingest_service.get_paper_detail(
        paper_id=paper_id,
        user_id=current_user.user_id
    )
    
    return paper_detail