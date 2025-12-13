"""
CRUD Repository 层单元测试
测试 Repository Pattern 是否正确工作
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import UserRepository
from app.crud.session import SessionRepository
from app.crud.message import MessageRepository
from app.crud.paper import PaperRepository
from app.models.db_models import User, ResearchSession, ChatMessage, MessageRole, Paper, PaperStatus


class TestUserRepository:
    """用户 Repository 测试"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, test_session: AsyncSession):
        """测试创建用户"""
        repo = UserRepository(test_session)
        
        user = await repo.create_user(
            user_id="test-user-123",
            username="testuser",
            password_hash="hashed_password",
            email="test@example.com"
        )
        
        assert user is not None
        assert user.user_id == "test-user-123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.created_at is not None
    
    @pytest.mark.asyncio
    async def test_get_by_username(self, test_session: AsyncSession):
        """测试根据用户名查询"""
        repo = UserRepository(test_session)
        
        # 先创建用户
        await repo.create_user(
            user_id="user-456",
            username="findme",
            password_hash="hashed"
        )
        
        # 查询
        user = await repo.get_by_username("findme")
        
        assert user is not None
        assert user.username == "findme"
        
        # 查询不存在的用户
        not_found = await repo.get_by_username("nonexistent")
        assert not_found is None
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, test_session: AsyncSession):
        """测试根据ID查询"""
        repo = UserRepository(test_session)
        
        await repo.create_user(
            user_id="user-789",
            username="idtest",
            password_hash="hashed"
        )
        
        user = await repo.get_by_id("user-789")
        
        assert user is not None
        assert user.user_id == "user-789"
    
    @pytest.mark.asyncio
    async def test_exists_by_username(self, test_session: AsyncSession):
        """测试用户名是否存在"""
        repo = UserRepository(test_session)
        
        await repo.create_user(
            user_id="user-exists",
            username="existsuser",
            password_hash="hashed"
        )
        
        assert await repo.exists_by_username("existsuser") is True
        assert await repo.exists_by_username("notexists") is False
    
    @pytest.mark.asyncio
    async def test_update_last_login(self, test_session: AsyncSession):
        """测试更新最后登录时间"""
        repo = UserRepository(test_session)
        
        user = await repo.create_user(
            user_id="user-login",
            username="loginuser",
            password_hash="hashed"
        )
        
        assert user.last_login_at is None
        
        updated_user = await repo.update_last_login(user)
        
        assert updated_user.last_login_at is not None
    
    @pytest.mark.asyncio
    async def test_update_password(self, test_session: AsyncSession):
        """测试更新密码"""
        repo = UserRepository(test_session)
        
        user = await repo.create_user(
            user_id="user-pwd",
            username="pwduser",
            password_hash="old_hash"
        )
        
        updated_user = await repo.update_password(user, "new_hash")
        
        assert updated_user.password_hash == "new_hash"


class TestSessionRepository:
    """会话 Repository 测试"""
    
    @pytest_asyncio.fixture
    async def user_for_session(self, test_session: AsyncSession):
        """创建测试用户"""
        user_repo = UserRepository(test_session)
        user = await user_repo.create_user(
            user_id="session-test-user",
            username="sessionuser",
            password_hash="hashed"
        )
        return user
    
    @pytest.mark.asyncio
    async def test_create_session(self, test_session: AsyncSession, user_for_session):
        """测试创建会话"""
        repo = SessionRepository(test_session)
        
        session = await repo.create_session(
            session_id="session-123",
            user_id=user_for_session.user_id,
            title="测试会话",
            domains=["AI", "ML"]
        )
        
        assert session is not None
        assert session.id == "session-123"
        assert session.title == "测试会话"
        assert session.message_count == 0
    
    @pytest.mark.asyncio
    async def test_get_by_id_and_user(self, test_session: AsyncSession, user_for_session):
        """测试根据ID和用户ID查询"""
        repo = SessionRepository(test_session)
        
        await repo.create_session(
            session_id="session-456",
            user_id=user_for_session.user_id,
            title="查询测试",
            domains=["SE"]
        )
        
        # 正确的用户ID
        session = await repo.get_by_id_and_user("session-456", user_for_session.user_id)
        assert session is not None
        
        # 错误的用户ID
        session = await repo.get_by_id_and_user("session-456", "wrong-user-id")
        assert session is None
    
    @pytest.mark.asyncio
    async def test_list_by_user(self, test_session: AsyncSession, user_for_session):
        """测试列表查询"""
        repo = SessionRepository(test_session)
        
        # 创建3个会话
        for i in range(3):
            await repo.create_session(
                session_id=f"list-session-{i}",
                user_id=user_for_session.user_id,
                title=f"列表测试会话{i}",
                domains=["AI"]
            )
        
        sessions, total = await repo.list_by_user(
            user_id=user_for_session.user_id,
            limit=10,
            offset=0
        )
        
        assert len(sessions) == 3
        assert total == 3
    
    @pytest.mark.asyncio
    async def test_parse_domains(self, test_session: AsyncSession):
        """测试 domains 解析"""
        # 列表输入
        result = SessionRepository.parse_domains(["AI", "ML"])
        assert result == ["AI", "ML"]
        
        # JSON 字符串输入
        result = SessionRepository.parse_domains('["AI", "ML"]')
        assert result == ["AI", "ML"]
        
        # 空值
        result = SessionRepository.parse_domains(None)
        assert result == []


class TestMessageRepository:
    """消息 Repository 测试"""
    
    @pytest_asyncio.fixture
    async def session_for_message(self, test_session: AsyncSession):
        """创建测试会话"""
        user_repo = UserRepository(test_session)
        user = await user_repo.create_user(
            user_id="msg-test-user",
            username="msguser",
            password_hash="hashed"
        )
        
        session_repo = SessionRepository(test_session)
        session = await session_repo.create_session(
            session_id="msg-test-session",
            user_id=user.user_id,
            title="消息测试会话",
            domains=["AI"]
        )
        
        return session
    
    @pytest.mark.asyncio
    async def test_create_message(self, test_session: AsyncSession, session_for_message):
        """测试创建消息"""
        repo = MessageRepository(test_session)
        
        message = await repo.create_message(
            message_id="msg-123",
            session_id=session_for_message.id,
            role=MessageRole.USER,
            content="测试消息内容"
        )
        
        assert message is not None
        assert message.id == "msg-123"
        assert message.role == MessageRole.USER
        assert message.content == "测试消息内容"
    
    @pytest.mark.asyncio
    async def test_get_by_session(self, test_session: AsyncSession, session_for_message):
        """测试获取会话消息"""
        repo = MessageRepository(test_session)
        
        # 创建3条消息
        for i in range(3):
            await repo.create_message(
                message_id=f"msg-list-{i}",
                session_id=session_for_message.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.AGENT,
                content=f"消息{i}"
            )
        
        messages, total = await repo.get_by_session(session_for_message.id)
        
        assert len(messages) == 3
        assert total == 3
    
    @pytest.mark.asyncio
    async def test_get_recent(self, test_session: AsyncSession, session_for_message):
        """测试获取最近消息"""
        repo = MessageRepository(test_session)
        
        # 创建5条消息
        for i in range(5):
            await repo.create_message(
                message_id=f"msg-recent-{i}",
                session_id=session_for_message.id,
                role=MessageRole.USER,
                content=f"消息{i}"
            )
        
        # 获取最近3条
        recent = await repo.get_recent(session_for_message.id, limit=3)
        
        assert len(recent) == 3
    
    @pytest.mark.asyncio
    async def test_format_message(self, test_session: AsyncSession, session_for_message):
        """测试消息格式化"""
        repo = MessageRepository(test_session)
        
        message = await repo.create_message(
            message_id="msg-format",
            session_id=session_for_message.id,
            role=MessageRole.AGENT,
            content="格式化测试",
            context_string="测试context",
            context_data={"source": "test"}
        )
        
        formatted = MessageRepository.format_message(message)
        
        assert formatted["message_id"] == "msg-format"
        assert formatted["role"] == "agent"
        assert formatted["content"] == "格式化测试"
        assert formatted["context_string"] == "测试context"
        assert formatted["context_data"]["source"] == "test"
    
    @pytest.mark.asyncio
    async def test_to_history_format(self, test_session: AsyncSession, session_for_message):
        """测试转换为历史格式"""
        repo = MessageRepository(test_session)
        
        msg1 = await repo.create_message(
            message_id="msg-hist-1",
            session_id=session_for_message.id,
            role=MessageRole.USER,
            content="用户消息"
        )
        
        msg2 = await repo.create_message(
            message_id="msg-hist-2",
            session_id=session_for_message.id,
            role=MessageRole.AGENT,
            content="AI回复"
        )
        
        history = MessageRepository.to_history_format([msg1, msg2])
        
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "用户消息"
        assert history[1]["role"] == "agent"
        assert history[1]["content"] == "AI回复"


class TestPaperRepository:
    """论文 Repository 测试"""
    
    @pytest_asyncio.fixture
    async def user_for_paper(self, test_session: AsyncSession):
        """创建测试用户"""
        user_repo = UserRepository(test_session)
        user = await user_repo.create_user(
            user_id="paper-test-user",
            username="paperuser",
            password_hash="hashed"
        )
        return user
    
    @pytest_asyncio.fixture
    async def paper_in_db(self, test_session: AsyncSession, user_for_paper):
        """在数据库中创建论文"""
        paper = Paper(
            id="paper-123",
            user_id=user_for_paper.user_id,
            filename="test_paper.pdf",
            file_path="/path/to/paper.pdf",
            file_size=1024000,
            status=PaperStatus.UPLOADED
        )
        test_session.add(paper)
        await test_session.flush()
        return paper
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, test_session: AsyncSession, paper_in_db):
        """测试根据ID查询论文"""
        repo = PaperRepository(test_session)
        
        paper = await repo.get_by_id("paper-123")
        
        assert paper is not None
        assert paper.id == "paper-123"
        assert paper.filename == "test_paper.pdf"
    
    @pytest.mark.asyncio
    async def test_get_by_ids(self, test_session: AsyncSession, user_for_paper, paper_in_db):
        """测试根据ID列表查询"""
        repo = PaperRepository(test_session)
        
        # 创建另一个论文
        paper2 = Paper(
            id="paper-456",
            user_id=user_for_paper.user_id,
            filename="test_paper2.pdf",
            file_path="/path/to/paper2.pdf",
            file_size=2048000,
            status=PaperStatus.UPLOADED
        )
        test_session.add(paper2)
        await test_session.flush()
        
        papers = await repo.get_by_ids(
            paper_ids=["paper-123", "paper-456"],
            user_id=user_for_paper.user_id
        )
        
        assert len(papers) == 2
    
    @pytest.mark.asyncio
    async def test_update_parsed_content(self, test_session: AsyncSession, paper_in_db):
        """测试更新解析内容"""
        repo = PaperRepository(test_session)
        
        parsed_data = {
            "title": "Test Paper Title",
            "sections": [{"heading": "Introduction", "content": "..."}]
        }
        
        updated = await repo.update_parsed_content(
            paper_id="paper-123",
            parsed_content=parsed_data,
            status=PaperStatus.PARSED
        )
        
        assert updated is not None
        assert updated.status == PaperStatus.PARSED
        assert updated.parsed_content == parsed_data
        assert updated.parsed_at is not None
    
    @pytest.mark.asyncio
    async def test_update_graph_status(self, test_session: AsyncSession, paper_in_db):
        """测试更新图谱状态"""
        repo = PaperRepository(test_session)
        
        updated = await repo.update_graph_status(
            paper_id="paper-123",
            added_to_graph=True,
            episode_ids=["ep-1", "ep-2"]
        )
        
        assert updated is not None
        assert updated.added_to_graph is True
        assert updated.graph_episode_ids == ["ep-1", "ep-2"]
        assert updated.added_to_graph_at is not None

