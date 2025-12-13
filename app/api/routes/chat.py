"""
聊天API路由
根据PRD_研究与聊天模块.md设计
提供消息发送、历史记录查询等接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_chat_service
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatSendRequest,
    ChatSendResponse,
    ChatHistoryResponse,
    ErrorResponse
)
from app.models.db_models import User

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post(
    "/send",
    response_model=ChatSendResponse,
    summary="发送消息",
    description="REQ-CHAT-3: 在研究会话中发送消息，获取Agent回复",
    responses={
        200: {"description": "发送成功", "model": ChatSendResponse},
        400: {"description": "请求参数错误", "model": ErrorResponse},
        401: {"description": "未授权"},
        404: {"description": "会话不存在", "model": ErrorResponse},
    }
)
async def send_message(
    request: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    发送消息
    
    - **session_id**: 研究会话ID
    - **message**: 用户消息内容
    - **attached_papers**: 附带的论文ID列表（可选）
    - **stream**: 是否流式响应（暂不支持）
    
    处理流程：
    1. 保存用户消息到数据库
    2. 异步将用户消息添加到知识图谱
    3. 根据是否有附带论文选择context来源
       - 有论文：从论文中提取context
       - 无论文：从知识图谱检索context
    4. 调用LLM生成回复
    5. 保存Agent消息到数据库
    
    返回：
    - **user_message**: 用户消息信息
    - **agent_message**: Agent消息信息（包含context_string和context_data）
    - **status**: 处理状态
    """
    # 验证消息不为空
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "EMPTY_MESSAGE",
                "message": "Message cannot be empty"
            }
        )
    
    try:
        result = await chat_service.send_message(
            session_id=request.session_id,
            message=request.message,
            user_id=current_user.user_id,
            attached_papers=request.attached_papers
        )
        return ChatSendResponse(**result)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "SESSION_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "SESSION_NOT_FOUND",
                    "message": "Research session does not exist"
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "BAD_REQUEST",
                "message": error_msg
            }
        )


@router.get(
    "/history/{session_id}",
    response_model=ChatHistoryResponse,
    summary="获取聊天历史",
    description="REQ-CHAT-4: 获取指定会话的聊天历史记录",
    responses={
        200: {"description": "获取成功", "model": ChatHistoryResponse},
        401: {"description": "未授权"},
        403: {"description": "无权访问", "model": ErrorResponse},
        404: {"description": "会话不存在", "model": ErrorResponse},
    }
)
async def get_chat_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=200, description="每页消息数"),
    offset: int = Query(0, ge=0, description="偏移量"),
    order: str = Query("asc", description="排序方式：asc（从旧到新）/ desc（从新到旧）"),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    获取聊天历史
    
    - **session_id**: 研究会话ID
    - **limit**: 每页消息数（默认50，最大200）
    - **offset**: 偏移量（默认0）
    - **order**: 排序方式
      - `asc`: 从旧到新（默认）
      - `desc`: 从新到旧
    
    返回：
    - **session_id**: 会话ID
    - **session_info**: 会话基本信息
    - **messages**: 消息列表（包含context信息）
    - **pagination**: 分页信息
    """
    try:
        result = await chat_service.get_history(
            session_id=session_id,
            user_id=current_user.user_id,
            limit=limit,
            offset=offset,
            order=order
        )
        return ChatHistoryResponse(**result)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "SESSION_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "SESSION_NOT_FOUND",
                    "message": "Session does not exist"
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "BAD_REQUEST",
                "message": error_msg
            }
        )
