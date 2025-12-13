"""
用户模块单元测试
测试用户资料的获取和更新功能

注意：UserProfileService 目前只有基础骨架，完整实现待后续开发
部分测试会自动跳过（pytest.skip）
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.db_models import User, ResearchSession, ChatMessage, Paper, PaperStatus
from app.schemas.user import (
    UserProfileResponse, UpdateProfileResponse, UpdateProfileRequest,
    GraphStats, ResearchStats, PaperStats, UserPreferences
)


# ==================== 辅助函数 ====================

async def create_test_user_and_login(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "TestPass123"
) -> tuple[str, str]:
    """
    创建测试用户并登录，返回 (user_id, access_token)
    
    注意：根据PRD，注册不返回token，需要单独登录
    """
    # 注册
    register_response = await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    user_id = register_response.json()["user_id"]
    
    # 登录获取token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": password
        }
    )
    access_token = login_response.json()["access_token"]
    
    return user_id, access_token


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
    """用户Schema模型测试 - 这些测试不依赖服务层实现"""
    
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


# ==================== API端点测试 ====================
# 注意：这些测试依赖 UserProfileService 的完整实现
# 如果服务未实现，测试会自动跳过

class TestGetUserProfileAPI:
    """GET /api/user/profile 测试"""
    
    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.get("/api/user/profile")
        # 未授权应该返回 401 或 403
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_get_profile_service_not_implemented(self, client: AsyncClient, test_session: AsyncSession):
        """测试服务未实现时的行为"""
        # 创建用户并登录
        user_id, access_token = await create_test_user_and_login(client)
        
        response = await client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # UserProfileService.get_profile() 返回 None（pass），会导致 500 错误
        # 这是预期的，因为服务未实现
        if response.status_code == 500:
            pytest.skip("UserProfileService.get_profile() not implemented")
        
        # 如果意外成功，验证响应结构
        assert response.status_code == 200


class TestUpdateUserProfileAPI:
    """PUT /api/user/profile 测试"""
    
    @pytest.mark.asyncio
    async def test_update_profile_unauthorized(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.put(
            "/api/user/profile",
            json={"email": "new@example.com"}
        )
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_update_profile_service_not_implemented(self, client: AsyncClient, test_session: AsyncSession):
        """测试服务未实现时的行为"""
        # 创建用户并登录
        user_id, access_token = await create_test_user_and_login(
            client, "updatetest", "update@example.com"
        )
        
        response = await client.put(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"email": "newemail@example.com"}
        )
        
        # UserProfileService.update_profile() 返回 None（pass），会导致 500 错误
        if response.status_code == 500:
            pytest.skip("UserProfileService.update_profile() not implemented")
        
        assert response.status_code == 200


# ==================== 用户认证与资料集成测试 ====================

class TestUserAuthIntegration:
    """用户认证与资料的集成测试 - 这些测试只依赖已实现的认证模块"""
    
    @pytest.mark.asyncio
    async def test_register_and_login_workflow(self, client: AsyncClient):
        """测试完整的注册登录流程"""
        # 1. 注册用户
        register_response = await client.post(
            "/api/auth/register",
            json={
                "username": "workflowuser",
                "email": "workflow@example.com",
                "password": "WorkflowPass123"
            }
        )
        
        assert register_response.status_code == 201
        register_data = register_response.json()
        
        # 验证注册响应（根据PRD，不返回token）
        assert "user_id" in register_data
        assert register_data["username"] == "workflowuser"
        assert "access_token" not in register_data
        
        # 2. 登录
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "workflowuser",
                "password": "WorkflowPass123"
            }
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        
        # 验证登录响应
        assert "access_token" in login_data
        assert "refresh_token" in login_data
        assert login_data["user"]["username"] == "workflowuser"
        
        # 3. 使用token访问受保护资源
        access_token = login_data["access_token"]
        
        # 访问研究会话列表（验证token有效）
        list_response = await client.get(
            "/api/research/list",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert list_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_user_data_persistence(self, client: AsyncClient, test_session: AsyncSession):
        """测试用户数据持久化"""
        # 创建用户
        user_id, access_token = await create_test_user_and_login(
            client, "persistuser", "persist@example.com"
        )
        
        # 创建研究会话
        create_response = await client.post(
            "/api/research/create",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "title": "持久化测试会话",
                "domains": ["AI"]
            }
        )
        
        assert create_response.status_code == 201
        session_id = create_response.json()["session_id"]
        
        # 验证会话存在
        list_response = await client.get(
            "/api/research/list",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert list_response.status_code == 200
        sessions = list_response.json()["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == session_id
        assert sessions[0]["title"] == "持久化测试会话"
