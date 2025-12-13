"""
服务依赖注入
提供 FastAPI 路由层使用的 Service 工厂函数

使用 Repository Pattern，Service 通过构造函数接收 Repository
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.crud.user import UserRepository
from app.crud.session import SessionRepository
from app.crud.message import MessageRepository
from app.crud.paper import PaperRepository
from app.services.graph_service import GraphService
from app.services.auth_service import AuthService
from app.services.research_service import ResearchService
from app.services.chat_service import ChatService
from app.services.ingest_service import IngestService


# ==================== Repository 工厂函数 ====================

async def get_user_repository(
    session: AsyncSession = Depends(get_session)
) -> UserRepository:
    """获取用户 Repository"""
    return UserRepository(session)


async def get_session_repository(
    session: AsyncSession = Depends(get_session)
) -> SessionRepository:
    """获取会话 Repository"""
    return SessionRepository(session)


async def get_message_repository(
    session: AsyncSession = Depends(get_session)
) -> MessageRepository:
    """获取消息 Repository"""
    return MessageRepository(session)


async def get_paper_repository(
    session: AsyncSession = Depends(get_session)
) -> PaperRepository:
    """获取论文 Repository"""
    return PaperRepository(session)


# ==================== Service 工厂函数 ====================

def get_graph_service() -> GraphService:
    """
    获取图谱服务实例
    
    GraphService 不依赖 MySQL，使用 Neo4j 驱动
    """
    return GraphService()


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """
    获取认证服务实例
    
    使用示例:
    ```python
    @router.post("/register")
    async def register(
        request: RegisterRequest,
        auth_service: AuthService = Depends(get_auth_service)
    ):
        return await auth_service.register(request)
    ```
    """
    return AuthService(user_repo)


async def get_research_service(
    session_repo: SessionRepository = Depends(get_session_repository)
) -> ResearchService:
    """
    获取研究会话服务实例
    
    使用示例:
    ```python
    @router.post("/sessions")
    async def create_session(
        request: CreateSessionRequest,
        research_service: ResearchService = Depends(get_research_service)
    ):
        return await research_service.create_session(...)
    ```
    """
    return ResearchService(session_repo)


async def get_chat_service(
    session_repo: SessionRepository = Depends(get_session_repository),
    message_repo: MessageRepository = Depends(get_message_repository),
    paper_repo: PaperRepository = Depends(get_paper_repository)
) -> ChatService:
    """
    获取聊天服务实例
    
    使用示例:
    ```python
    @router.post("/sessions/{session_id}/messages")
    async def send_message(
        session_id: str,
        request: SendMessageRequest,
        chat_service: ChatService = Depends(get_chat_service)
    ):
        return await chat_service.send_message(...)
    ```
    """
    return ChatService(session_repo, message_repo, paper_repo)


async def get_ingest_service(
    paper_repo: PaperRepository = Depends(get_paper_repository)
) -> IngestService:
    """
    获取论文摄入服务实例
    
    使用示例:
    ```python
    @router.post("/papers/upload")
    async def upload_paper(
        file: UploadFile,
        ingest_service: IngestService = Depends(get_ingest_service)
    ):
        return await ingest_service.ingest_pdf(file, user_id)
    ```
    """
    return IngestService(paper_repo)
