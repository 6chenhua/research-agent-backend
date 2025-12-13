"""
端到端集成测试
测试完整的用户流程
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from tests.conftest import auth_header


class TestFullUserJourney:
    """完整用户流程测试"""
    
    @pytest.mark.asyncio
    async def test_complete_research_flow(self, client: AsyncClient):
        """
        测试完整的研究流程:
        1. 用户注册
        2. 用户登录
        3. 创建研究会话
        4. 发送消息
        5. 获取聊天历史
        6. 查看会话列表
        7. 修改密码
        8. 登出
        """
        # 1. 用户注册
        register_response = await client.post(
            "/api/auth/register",
            json={
                "username": "journey_user",
                "password": "JourneyPass123",
                "email": "journey@example.com"
            }
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["user_id"]
        
        # 2. 用户登录
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "journey_user",
                "password": "JourneyPass123"
            }
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # 验证token结构
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["user"]["username"] == "journey_user"
        
        # 3. 创建研究会话
        create_session_response = await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={
                "title": "AI 论文研究",
                "domains": ["Artificial Intelligence", "Machine Learning"],
                "description": "研究深度学习相关论文"
            }
        )
        assert create_session_response.status_code == 201
        session_data = create_session_response.json()
        session_id = session_data["session_id"]
        
        assert session_data["title"] == "AI 论文研究"
        assert session_data["domains"] == ["Artificial Intelligence", "Machine Learning"]
        
        # 4. 发送消息
        with patch('app.services.chat_service.LLMClient') as mock_llm_class, \
             patch('app.services.chat_service.get_enhanced_graphiti') as mock_graphiti:
            
            mock_llm_instance = MagicMock()
            mock_llm_instance.chat_with_context = AsyncMock(
                return_value="深度学习是机器学习的一个子领域，它使用神经网络来学习数据表示。"
            )
            mock_llm_class.return_value = mock_llm_instance
            
            mock_graphiti_instance = AsyncMock()
            mock_graphiti_instance.search = AsyncMock(return_value=[])
            mock_graphiti_instance.add_episode = AsyncMock()
            mock_graphiti.return_value = mock_graphiti_instance
            
            send_message_response = await client.post(
                "/api/chat/send",
                headers=auth_header(access_token),
                json={
                    "session_id": session_id,
                    "message": "什么是深度学习？"
                }
            )
            assert send_message_response.status_code == 200
            message_data = send_message_response.json()
            
            assert message_data["user_message"]["content"] == "什么是深度学习？"
            assert "深度学习" in message_data["agent_message"]["content"]
        
        # 5. 获取聊天历史
        history_response = await client.get(
            f"/api/chat/history/{session_id}",
            headers=auth_header(access_token)
        )
        assert history_response.status_code == 200
        history_data = history_response.json()
        
        assert history_data["session_id"] == session_id
        assert len(history_data["messages"]) == 2  # 用户消息 + AI回复
        assert history_data["session_info"]["title"] == "AI 论文研究"
        
        # 6. 查看会话列表
        list_response = await client.get(
            "/api/research/list",
            headers=auth_header(access_token)
        )
        assert list_response.status_code == 200
        list_data = list_response.json()
        
        assert len(list_data["sessions"]) == 1
        assert list_data["sessions"][0]["session_id"] == session_id
        assert list_data["sessions"][0]["message_count"] == 2
        
        # 7. 刷新Token
        refresh_response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_access_token = refresh_response.json()["access_token"]
        
        # 使用新token验证仍然有效
        verify_response = await client.get(
            "/api/research/list",
            headers=auth_header(new_access_token)
        )
        assert verify_response.status_code == 200
        
        # 8. 修改密码
        change_pwd_response = await client.post(
            "/api/auth/change-password",
            headers=auth_header(new_access_token),
            json={
                "old_password": "JourneyPass123",
                "new_password": "NewJourneyPass456"
            }
        )
        assert change_pwd_response.status_code == 200
        assert change_pwd_response.json()["require_relogin"] is True
        
        # 验证新密码可以登录
        new_login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "journey_user",
                "password": "NewJourneyPass456"
            }
        )
        assert new_login_response.status_code == 200
        
        # 9. 登出
        final_token = new_login_response.json()["access_token"]
        logout_response = await client.post(
            "/api/auth/logout",
            headers=auth_header(final_token)
        )
        assert logout_response.status_code == 200
        assert logout_response.json()["message"] == "Logged out successfully"
    
    @pytest.mark.asyncio
    async def test_multi_session_research(self, authenticated_client):
        """测试多会话研究场景"""
        client, access_token, user_id = authenticated_client
        
        # 创建多个研究会话
        sessions = []
        domains_list = [
            ["AI", "Deep Learning"],
            ["Software Engineering", "Agile"],
            ["Data Science", "Statistics"]
        ]
        
        for i, domains in enumerate(domains_list):
            response = await client.post(
                "/api/research/create",
                headers=auth_header(access_token),
                json={
                    "title": f"研究会话 {i+1}",
                    "domains": domains
                }
            )
            assert response.status_code == 201
            sessions.append(response.json()["session_id"])
        
        # 获取列表验证
        list_response = await client.get(
            "/api/research/list",
            headers=auth_header(access_token)
        )
        assert list_response.status_code == 200
        assert len(list_response.json()["sessions"]) == 3
        
        # 在每个会话中发送消息
        with patch('app.services.chat_service.LLMClient') as mock_llm_class, \
             patch('app.services.chat_service.get_enhanced_graphiti') as mock_graphiti:
            
            mock_llm_instance = MagicMock()
            mock_llm_instance.chat_with_context = AsyncMock(return_value="回复")
            mock_llm_class.return_value = mock_llm_instance
            
            mock_graphiti_instance = AsyncMock()
            mock_graphiti_instance.search = AsyncMock(return_value=[])
            mock_graphiti_instance.add_episode = AsyncMock()
            mock_graphiti.return_value = mock_graphiti_instance
            
            for i, session_id in enumerate(sessions):
                send_response = await client.post(
                    "/api/chat/send",
                    headers=auth_header(access_token),
                    json={
                        "session_id": session_id,
                        "message": f"会话{i+1}的问题"
                    }
                )
                assert send_response.status_code == 200
        
        # 验证每个会话都有消息
        for session_id in sessions:
            history_response = await client.get(
                f"/api/chat/history/{session_id}",
                headers=auth_header(access_token)
            )
            assert history_response.status_code == 200
            assert len(history_response.json()["messages"]) == 2


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_invalid_token(self, client: AsyncClient):
        """测试无效Token"""
        response = await client.get(
            "/api/research/list",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_expired_token(self, client: AsyncClient):
        """测试过期Token（模拟）"""
        # 一个格式正确但已过期的token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdCIsImV4cCI6MTYwMDAwMDAwMH0.test"
        
        response = await client.get(
            "/api/research/list",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_malformed_request(self, client: AsyncClient):
        """测试格式错误的请求"""
        response = await client.post(
            "/api/auth/register",
            json={
                # 缺少 username
                "password": "TestPass123"
            }
        )
        
        assert response.status_code == 422  # Pydantic 验证错误
    
    @pytest.mark.asyncio
    async def test_rate_limit_simulation(self, client: AsyncClient):
        """测试登录限流（需要多次失败登录）"""
        # 注册用户
        await client.post(
            "/api/auth/register",
            json={
                "username": "ratelimit_user",
                "password": "RateLimit123"
            }
        )
        
        # 多次使用错误密码登录（模拟限流）
        # 注意：实际限流需要6次才会触发（15分钟内5次）
        for i in range(3):
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": "ratelimit_user",
                    "password": "WrongPassword"
                }
            )
            assert response.status_code == 401


class TestDataIsolation:
    """数据隔离测试"""
    
    @pytest.mark.asyncio
    async def test_user_data_isolation(self, client: AsyncClient):
        """测试不同用户数据隔离"""
        # 创建用户A
        await client.post(
            "/api/auth/register",
            json={"username": "userA", "password": "UserAPass123"}
        )
        login_a = await client.post(
            "/api/auth/login",
            json={"username": "userA", "password": "UserAPass123"}
        )
        token_a = login_a.json()["access_token"]
        
        # 创建用户B
        await client.post(
            "/api/auth/register",
            json={"username": "userB", "password": "UserBPass123"}
        )
        login_b = await client.post(
            "/api/auth/login",
            json={"username": "userB", "password": "UserBPass123"}
        )
        token_b = login_b.json()["access_token"]
        
        # 用户A创建会话
        session_a = await client.post(
            "/api/research/create",
            headers=auth_header(token_a),
            json={"title": "用户A的会话", "domains": ["AI"]}
        )
        session_id_a = session_a.json()["session_id"]
        
        # 用户B创建会话
        session_b = await client.post(
            "/api/research/create",
            headers=auth_header(token_b),
            json={"title": "用户B的会话", "domains": ["SE"]}
        )
        
        # 用户A只能看到自己的会话
        list_a = await client.get(
            "/api/research/list",
            headers=auth_header(token_a)
        )
        assert len(list_a.json()["sessions"]) == 1
        assert list_a.json()["sessions"][0]["title"] == "用户A的会话"
        
        # 用户B只能看到自己的会话
        list_b = await client.get(
            "/api/research/list",
            headers=auth_header(token_b)
        )
        assert len(list_b.json()["sessions"]) == 1
        assert list_b.json()["sessions"][0]["title"] == "用户B的会话"
        
        # 用户B无法访问用户A的会话历史
        history_response = await client.get(
            f"/api/chat/history/{session_id_a}",
            headers=auth_header(token_b)
        )
        assert history_response.status_code == 404

