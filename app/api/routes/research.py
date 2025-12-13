"""
研究会话API路由
根据PRD_研究与聊天模块.md设计
提供研究会话的创建、查询等接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_research_service
from app.services.research_service import ResearchService
from app.schemas.chat import (
    CreateResearchRequest,
    CreateResearchResponse,
    ResearchSessionListResponse,
    ErrorResponse
)
from app.models.db_models import User

router = APIRouter(prefix="/research", tags=["研究会话"])


@router.post(
    "/create",
    response_model=CreateResearchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建研究会话",
    description="REQ-CHAT-1: 用户创建新的研究会话，指定研究领域",
    responses={
        201: {"description": "创建成功", "model": CreateResearchResponse},
        400: {"description": "请求参数错误", "model": ErrorResponse},
        401: {"description": "未授权"},
    }
)
async def create_research_session(
    request: CreateResearchRequest,
    current_user: User = Depends(get_current_user),
    research_service: ResearchService = Depends(get_research_service)
):
    """
    创建研究会话
    
    - **title**: 会话标题（可选，默认自动生成）
    - **domains**: 研究领域列表（至少1个，如 ["AI", "SE"]）
    - **description**: 研究描述（可选）
    
    创建成功后会异步触发社区构建任务。
    
    返回：
    - **session_id**: 会话UUID
    - **title**: 会话标题
    - **domains**: 研究领域
    - **created_at**: 创建时间
    - **community_build_triggered**: 是否触发社区构建
    """
    try:
        result = await research_service.create_session(
            user_id=current_user.user_id,
            domains=request.domains,
            title=request.title,
            description=request.description
        )
        return CreateResearchResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_DOMAINS",
                "message": str(e)
            }
        )


@router.get(
    "/list",
    response_model=ResearchSessionListResponse,
    summary="获取研究会话列表",
    description="REQ-CHAT-2: 获取当前用户的所有研究会话列表",
    responses={
        200: {"description": "获取成功", "model": ResearchSessionListResponse},
        401: {"description": "未授权"},
    }
)
async def list_research_sessions(
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    sort: str = Query("created_desc", description="排序方式：created_desc / updated_desc"),
    current_user: User = Depends(get_current_user),
    research_service: ResearchService = Depends(get_research_service)
):
    """
    获取研究会话列表
    
    - **limit**: 每页数量（默认20，最大100）
    - **offset**: 偏移量（默认0）
    - **sort**: 排序方式
      - `created_desc`: 按创建时间倒序（默认）
      - `updated_desc`: 按更新时间倒序
    
    返回：
    - **sessions**: 会话列表
    - **pagination**: 分页信息
    """
    result = await research_service.list_sessions(
        user_id=current_user.user_id,
        limit=limit,
        offset=offset,
        sort=sort
    )
    return ResearchSessionListResponse(**result)
