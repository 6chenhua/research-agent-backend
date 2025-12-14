"""
Paper API router.
Handles uploading and management of research papers.

API端点：
- POST /api/papers/upload - 上传论文PDF（只上传，不解析）
- POST /api/papers/{paper_id}/add-to-graph - 将论文添加到图谱

注意：
- 上传时只保存文件到磁盘并记录到数据库
- 解析在用户发送消息时按需进行（_generate_paper_context）
- 添加到图谱是用户主动触发的操作
"""
import logging

from fastapi import APIRouter, UploadFile, Depends, HTTPException, File

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_ingest_service
from app.schemas.paper import PaperUploadResponse
from app.models.db_models import User
from app.services.ingest_service import IngestService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Papers"])


@router.post(
    "/upload",
    response_model=PaperUploadResponse,
    summary="Upload Research Paper (PDF)",
    description="""
    Upload a PDF research paper.
    
    This endpoint ONLY:
    1. Validates the file (format, size)
    2. Saves the file to disk
    3. Creates a database record with status='uploaded'
    
    PDF parsing happens later when:
    - User sends a message with attached papers
    - User triggers 'add-to-graph'
    
    Limits:
    - File size: < 50MB
    - Format: PDF only
    """
)
async def upload_paper(
    file: UploadFile = File(..., description="PDF file to upload"),
    current_user: User = Depends(get_current_user),
    ingest_service: IngestService = Depends(get_ingest_service)
):
    """
    Upload a PDF file (no parsing).

    Args:
        file: PDF document
        current_user: Current authenticated user
        ingest_service: 论文摄入服务

    Returns:
        PaperUploadResponse with paper_id, filename, status
    
    Raises:
        400: Invalid file format or size
        500: Upload failed
    """
    try:
        result = await ingest_service.upload_paper(
            file=file,
            user_id=current_user.user_id
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload paper: {str(e)}"
        )
