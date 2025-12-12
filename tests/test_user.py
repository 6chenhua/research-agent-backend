"""
用户模块单元测试
测试用户资料的获取和更新功能
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.db_models import User, ResearchSession, ChatMessage, Paper, PaperStatus
from app.schemas.user import (
    UserProfileResponse, UpdateProfileResponse, UpdateProfileRequest,
    GraphStats, ResearchStats, PaperStats, UserPreferences
)
from app.services.user_profile_service import UserProfileService


# ==================== 辅助函数 ====================

async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "TestPass123!"
) -> dict:
    """创建测试用户并返回注册响应"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    return response.json()


async def create_research_session(
    session: AsyncSession,
    user_id: str,
    title: str = "Test Session",
    domains: list = None
) -> ResearchSession:
    """创建测试研究会话"""
    if domains is None:
        domains = ["AI", "SE"]
    
    import uuid
    rs = ResearchSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        domains=domains,
        message_count=0
    )
    session.add(rs)
    await session.flush()
    return rs


async def create_chat_message(
    session: AsyncSession,
    session_id: str,
    role: str = "user",
    content: str = "Test message"
) -> ChatMessage:
    """创建测试聊天消息"""
    import uuid
    from app.models.db_models import MessageRole
    
    msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=MessageRole.USER if role == "user" else MessageRole.AGENT,
        content=content
    )
    session.add(msg)
    await session.flush()
    return msg


async def create_paper(
    session: AsyncSession,
    user_id: str,
    filename: str = "test.pdf",
    status: PaperStatus = PaperStatus.UPLOADED,
    added_to_graph: bool = False
) -> Paper:
    """创建测试论文"""
    import uuid
    
    paper = Paper(
        id=str(uuid.uuid4()),
        user_id=user_id,
        filename=filename,
        file_path=f"/tmp/{filename}",
        file_size=1024,
        status=status,
        added_to_graph=added_to_graph
    )
    session.add(paper)
    await session.flush()
    return paper


# ==================== Schema测试 ====================

class TestUserSchemas:
    """用户Schema模型测试"""
    
    def test_graph_stats_default(self):
        """测试GraphStats默认值"""
        stats = GraphStats()
        assert stats.total_entities == 0
        assert stats.total_episodes == 0
        assert stats.total_edges == 0
    
    def test_graph_stats_with_values(self):
        """测试GraphStats设置值"""
        stats = GraphStats(total_entities=100, total_episodes=50, total_edges=200)
        assert stats.total_entities == 100
        assert stats.total_episodes == 50
        assert stats.total_edges == 200
    
    def test_research_stats_default(self):
        """测试ResearchStats默认值"""
        stats = ResearchStats()
        assert stats.total_sessions == 0
        assert stats.total_messages == 0
        assert stats.domains == []
    
    def test_paper_stats_default(self):
        """测试PaperStats默认值"""
        stats = PaperStats()
        assert stats.total_uploaded == 0
        assert stats.total_parsed == 0
        assert stats.added_to_graph == 0
    
    def test_user_preferences_default(self):
        """测试UserPreferences默认值"""
        prefs = UserPreferences()
        assert prefs.default_domains == []
        assert prefs.theme == "light"
        assert prefs.language == "zh-CN"
        assert prefs.graph_settings is None
        assert prefs.chat_settings is None
        assert prefs.paper_settings is None
    
    def test_user_preferences_custom(self):
        """测试UserPreferences自定义值"""
        prefs = UserPreferences(
            default_domains=["AI", "CV"],
            theme="dark",
            language="en-US"
        )
        assert prefs.default_domains == ["AI", "CV"]
        assert prefs.theme == "dark"
        assert prefs.language == "en-US"
    
    def test_update_profile_request_email_only(self):
        """测试只更新邮箱的请求"""
        request = UpdateProfileRequest(email="new@example.com")
        assert request.email == "new@example.com"
        assert request.preferences is None
    
    def test_update_profile_request_preferences_only(self):
        """测试只更新偏好设置的请求"""
        prefs = UserPreferences(theme="dark")
        request = UpdateProfileRequest(preferences=prefs)
        assert request.email is None
        assert request.preferences.theme == "dark"
    
    def test_update_profile_request_invalid_email(self):
        """测试无效邮箱格式"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            UpdateProfileRequest(email="invalid-email")
    
    def test_user_profile_response(self):
        """测试UserProfileResponse创建"""
        response = UserProfileResponse(
            user_id="test-uuid",
            username="testuser",
            email="test@example.com",
            created_at="2025-12-01T10:00:00Z"
        )
        assert response.user_id == "test-uuid"
        assert response.username == "testuser"
        assert response.graph_stats.total_entities == 0
        assert response.research_stats.total_sessions == 0
        assert response.paper_stats.total_uploaded == 0


# ==================== Service层测试 ====================

class TestUserProfileService:
    """UserProfileService测试"""
    
    @pytest.mark.asyncio
    async def test_get_profile_user_not_found(self, test_session: AsyncSession):
        """测试获取不存在用户的资料"""
        service = UserProfileService()
        
        with pytest.raises(Exception) as exc_info:
            await service.get_profile("non-existent-user-id", test_session)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_profile_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功获取用户资料"""
        # 创建用户
        register_data = await create_test_user(client)
        user_id = register_data["user"]["user_id"]
        
        # Mock Neo4j查询
        service = UserProfileService()
        
        with patch.object(service, '_get_graph_stats', return_value=GraphStats(
            total_entities=10, total_episodes=5, total_edges=20
        )):
            result = await service.get_profile(user_id, test_session)
        
        assert result.user_id == user_id
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert result.created_at is not None
    
    @pytest.mark.asyncio
    async def test_get_research_stats(self, client: AsyncClient, test_session: AsyncSession):
        """测试获取研究统计"""
        # 创建用户
        register_data = await create_test_user(client)
        user_id = register_data["user"]["user_id"]
        
        # 创建研究会话和消息
        rs1 = await create_research_session(test_session, user_id, "Session 1", ["AI"])
        rs2 = await create_research_session(test_session, user_id, "Session 2", ["SE", "CV"])
        await create_chat_message(test_session, rs1.id, "user", "Hello")
        await create_chat_message(test_session, rs1.id, "agent", "Hi there")
        await create_chat_message(test_session, rs2.id, "user", "Question")
        
        await test_session.commit()
        
        service = UserProfileService()
        stats = await service._get_research_stats(user_id, test_session)
        
        assert stats.total_sessions == 2
        assert stats.total_messages == 3
        assert set(stats.domains) == {"AI", "SE", "CV"}
    
    @pytest.mark.asyncio
    async def test_get_paper_stats(self, client: AsyncClient, test_session: AsyncSession):
        """测试获取论文统计"""
        # 创建用户
        register_data = await create_test_user(client)
        user_id = register_data["user"]["user_id"]
        
        # 创建论文
        await create_paper(test_session, user_id, "paper1.pdf", PaperStatus.UPLOADED)
        await create_paper(test_session, user_id, "paper2.pdf", PaperStatus.PARSED)
        await create_paper(test_session, user_id, "paper3.pdf", PaperStatus.PARSED, added_to_graph=True)
        await create_paper(test_session, user_id, "paper4.pdf", PaperStatus.FAILED)
        
        await test_session.commit()
        
        service = UserProfileService()
        stats = await service._get_paper_stats(user_id, test_session)
        
        assert stats.total_uploaded == 4
        assert stats.total_parsed == 2
        assert stats.added_to_graph == 1
    
    @pytest.mark.asyncio
    async def test_update_profile_email(self, client: AsyncClient, test_session: AsyncSession):
        """测试更新邮箱"""
        # 创建用户
        register_data = await create_test_user(client)
        user_id = register_data["user"]["user_id"]
        
        service = UserProfileService()
        request = UpdateProfileRequest(email="newemail@example.com")
        
        result = await service.update_profile(user_id, request, test_session)
        
        assert result.email == "newemail@example.com"
        assert result.message == "Profile updated successfully"
    
    @pytest.mark.asyncio
    async def test_update_profile_email_conflict(self, client: AsyncClient, test_session: AsyncSession):
        """测试更新邮箱冲突"""
        # 创建两个用户
        await create_test_user(client, "user1", "user1@example.com")
        register_data2 = await create_test_user(client, "user2", "user2@example.com")
        user2_id = register_data2["user"]["user_id"]
        
        service = UserProfileService()
        request = UpdateProfileRequest(email="user1@example.com")  # 尝试使用user1的邮箱
        
        with pytest.raises(Exception) as exc_info:
            await service.update_profile(user2_id, request, test_session)
        
        assert exc_info.value.status_code == 409
    
    @pytest.mark.asyncio
    async def test_update_profile_preferences(self, client: AsyncClient, test_session: AsyncSession):
        """测试更新偏好设置"""
        # 创建用户
        register_data = await create_test_user(client)
        user_id = register_data["user"]["user_id"]
        
        service = UserProfileService()
        prefs = UserPreferences(
            default_domains=["AI", "CV"],
            theme="dark",
            language="en-US"
        )
        request = UpdateProfileRequest(preferences=prefs)
        
        result = await service.update_profile(user_id, request, test_session)
        
        assert result.preferences is not None
        assert result.preferences.theme == "dark"
        assert result.preferences.language == "en-US"
        assert "AI" in result.preferences.default_domains
    
    @pytest.mark.asyncio
    async def test_update_profile_user_not_found(self, test_session: AsyncSession):
        """测试更新不存在用户的资料"""
        service = UserProfileService()
        request = UpdateProfileRequest(email="new@example.com")
        
        with pytest.raises(Exception) as exc_info:
            await service.update_profile("non-existent-user-id", request, test_session)
        
        assert exc_info.value.status_code == 404
    
    def test_format_datetime(self):
        """测试日期时间格式化"""
        service = UserProfileService()
        
        # 测试None输入
        assert service._format_datetime(None) is None
        
        # 测试正常日期
        dt = datetime(2025, 12, 11, 10, 30, 0)
        formatted = service._format_datetime(dt)
        assert formatted.endswith("Z")
        assert "2025-12-11" in formatted


# ==================== API端点测试 ====================

class TestGetUserProfileAPI:
    """GET /api/v1/user/profile 测试"""
    
    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.get("/api/user/profile")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_profile_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功获取用户资料"""
        # 创建用户
        register_data = await create_test_user(client)
        access_token = register_data["access_token"]
        
        # Mock Graphiti客户端
        mock_client = MagicMock()
        mock_driver = MagicMock()
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_record = {"entities": 10, "episodes": 5}
        mock_edge_record = {"edges": 20}
        
        mock_result.single = AsyncMock(side_effect=[mock_record, mock_edge_record])
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_driver.session = MagicMock(return_value=mock_session)
        mock_client.driver = mock_driver
        
        with patch('app.services.user_profile_service.enhanced_graphiti') as mock_singleton:
            mock_singleton._initialized = True
            mock_singleton.client = mock_client
            
            response = await client.get(
                "/api/user/profile",
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user_id" in data
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "graph_stats" in data
        assert "research_stats" in data
        assert "paper_stats" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_get_profile_with_stats(self, client: AsyncClient, test_session: AsyncSession):
        """测试获取包含统计数据的用户资料"""
        # 创建用户
        register_data = await create_test_user(client)
        access_token = register_data["access_token"]
        user_id = register_data["user"]["user_id"]
        
        # 创建研究会话和论文
        rs = await create_research_session(test_session, user_id, "Test Session", ["AI"])
        await create_chat_message(test_session, rs.id, "user", "Hello")
        await create_paper(test_session, user_id, "test.pdf", PaperStatus.PARSED)
        await test_session.commit()
        
        # Mock Graphiti
        with patch('app.services.user_profile_service.enhanced_graphiti') as mock_singleton:
            mock_singleton._initialized = False
            
            response = await client.get(
                "/api/user/profile",
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["research_stats"]["total_sessions"] == 1
        assert data["research_stats"]["total_messages"] == 1
        assert "AI" in data["research_stats"]["domains"]
        assert data["paper_stats"]["total_uploaded"] == 1
        assert data["paper_stats"]["total_parsed"] == 1


class TestUpdateUserProfileAPI:
    """PUT /api/v1/user/profile 测试"""
    
    @pytest.mark.asyncio
    async def test_update_profile_unauthorized(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.put(
            "/api/user/profile",
            json={"email": "new@example.com"}
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_update_profile_email_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功更新邮箱"""
        # 创建用户
        register_data = await create_test_user(client)
        access_token = register_data["access_token"]
        
        response = await client.put(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"email": "newemail@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "newemail@example.com"
        assert data["message"] == "Profile updated successfully"
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_update_profile_preferences_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功更新偏好设置"""
        # 创建用户
        register_data = await create_test_user(client)
        access_token = register_data["access_token"]
        
        response = await client.put(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "preferences": {
                    "default_domains": ["AI", "CV"],
                    "theme": "dark",
                    "language": "en-US"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["preferences"]["theme"] == "dark"
        assert data["preferences"]["language"] == "en-US"
        assert "AI" in data["preferences"]["default_domains"]
    
    @pytest.mark.asyncio
    async def test_update_profile_email_conflict(self, client: AsyncClient, test_session: AsyncSession):
        """测试邮箱冲突"""
        # 创建两个用户
        await create_test_user(client, "user1", "user1@example.com")
        register_data2 = await create_test_user(client, "user2", "user2@example.com")
        access_token2 = register_data2["access_token"]
        
        # 尝试将user2的邮箱改为user1的邮箱
        response = await client.put(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {access_token2}"},
            json={"email": "user1@example.com"}
        )
        
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "EMAIL_EXISTS"
    
    @pytest.mark.asyncio
    async def test_update_profile_invalid_email(self, client: AsyncClient, test_session: AsyncSession):
        """测试无效邮箱格式"""
        # 创建用户
        register_data = await create_test_user(client)
        access_token = register_data["access_token"]
        
        response = await client.put(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"email": "invalid-email-format"}
        )
        
        # Pydantic验证错误返回422
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_profile_empty_request(self, client: AsyncClient, test_session: AsyncSession):
        """测试空请求（不更新任何内容）"""
        # 创建用户
        register_data = await create_test_user(client)
        access_token = register_data["access_token"]
        
        response = await client.put(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {access_token}"},
            json={}
        )
        
        # 空请求应该成功，只是不更新任何内容
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Profile updated successfully"
    
    @pytest.mark.asyncio
    async def test_update_profile_with_graph_settings(self, client: AsyncClient, test_session: AsyncSession):
        """测试更新图谱可视化设置"""
        # 创建用户
        register_data = await create_test_user(client)
        access_token = register_data["access_token"]
        
        response = await client.put(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "preferences": {
                    "graph_settings": {
                        "default_layout": "hierarchical",
                        "show_episodes": True,
                        "show_labels": False
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["preferences"]["graph_settings"]["default_layout"] == "hierarchical"
        assert data["preferences"]["graph_settings"]["show_episodes"] is True
        assert data["preferences"]["graph_settings"]["show_labels"] is False


class TestUserProfileIntegration:
    """用户资料集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_profile_workflow(self, client: AsyncClient, test_session: AsyncSession):
        """测试完整的用户资料工作流"""
        # 1. 注册用户
        register_data = await create_test_user(client, "integrationuser", "integration@example.com")
        access_token = register_data["access_token"]
        user_id = register_data["user"]["user_id"]
        
        # 2. 创建一些数据
        rs = await create_research_session(test_session, user_id, "My Research", ["AI", "ML"])
        await create_chat_message(test_session, rs.id, "user", "Question 1")
        await create_chat_message(test_session, rs.id, "agent", "Answer 1")
        await create_paper(test_session, user_id, "paper1.pdf", PaperStatus.PARSED, True)
        await create_paper(test_session, user_id, "paper2.pdf", PaperStatus.UPLOADED)
        await test_session.commit()
        
        # 3. 获取用户资料
        with patch('app.services.user_profile_service.enhanced_graphiti') as mock_singleton:
            mock_singleton._initialized = False
            
            get_response = await client.get(
                "/api/user/profile",
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        assert get_response.status_code == 200
        profile_data = get_response.json()
        
        assert profile_data["username"] == "integrationuser"
        assert profile_data["research_stats"]["total_sessions"] == 1
        assert profile_data["research_stats"]["total_messages"] == 2
        assert profile_data["paper_stats"]["total_uploaded"] == 2
        assert profile_data["paper_stats"]["total_parsed"] == 1
        assert profile_data["paper_stats"]["added_to_graph"] == 1
        
        # 4. 更新用户资料
        update_response = await client.put(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "email": "updated@example.com",
                "preferences": {
                    "theme": "dark",
                    "default_domains": ["AI", "ML", "DL"]
                }
            }
        )
        
        assert update_response.status_code == 200
        updated_data = update_response.json()
        
        assert updated_data["email"] == "updated@example.com"
        assert updated_data["preferences"]["theme"] == "dark"
        assert "AI" in updated_data["preferences"]["default_domains"]
        
        # 5. 再次获取资料验证更新
        with patch('app.services.user_profile_service.enhanced_graphiti') as mock_singleton:
            mock_singleton._initialized = False
            
            verify_response = await client.get(
                "/api/user/profile",
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        
        assert verify_data["email"] == "updated@example.com"

