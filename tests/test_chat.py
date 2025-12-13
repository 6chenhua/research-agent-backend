"""
聊天模块测试
测试消息发送、历史记录查询等功能
根据PRD_研究与聊天模块.md设计
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from tests.conftest import auth_header


class TestSendMessage:
    """发送消息测试 REQ-CHAT-3"""
    
    @pytest.fixture
    async def session_with_research(self, authenticated_client):
        """创建带有研究会话的fixture"""
        client, access_token, user_id = authenticated_client
        
        # 创建研究会话
        response = await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={
                "title": "聊天测试会话",
                "domains": ["AI"]
            }
        )
        session_id = response.json()["session_id"]
        
        return client, access_token, user_id, session_id
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, session_with_research):
        """测试成功发送消息"""
        client, access_token, user_id, session_id = session_with_research
        
        # Mock LLM 客户端和 Graphiti
        with patch('app.services.chat_service.LLMClient') as mock_llm_class, \
             patch('app.services.chat_service.get_enhanced_graphiti') as mock_graphiti:
            
            # 设置 Mock 返回值
            mock_llm_instance = MagicMock()
            mock_llm_instance.chat_with_context = AsyncMock(return_value="这是AI的回复")
            mock_llm_class.return_value = mock_llm_instance
            
            mock_graphiti_instance = AsyncMock()
            mock_graphiti_instance.search = AsyncMock(return_value=[])
            mock_graphiti_instance.add_episode = AsyncMock()
            mock_graphiti.return_value = mock_graphiti_instance
            
            response = await client.post(
                "/api/chat/send",
                headers=auth_header(access_token),
                json={
                    "session_id": session_id,
                    "message": "什么是机器学习？"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应结构
            assert "user_message" in data
            assert "agent_message" in data
            assert "status" in data
            
            # 验证用户消息
            assert data["user_message"]["role"] == "user"
            assert data["user_message"]["content"] == "什么是机器学习？"
            assert "message_id" in data["user_message"]
            assert "created_at" in data["user_message"]
            
            # 验证Agent消息
            assert data["agent_message"]["role"] == "agent"
            assert data["agent_message"]["content"] == "这是AI的回复"
            assert "message_id" in data["agent_message"]
            assert "context_string" in data["agent_message"]
            assert "context_data" in data["agent_message"]
    
    @pytest.mark.asyncio
    async def test_send_message_empty_content(self, session_with_research):
        """测试发送空消息"""
        client, access_token, user_id, session_id = session_with_research
        
        response = await client.post(
            "/api/chat/send",
            headers=auth_header(access_token),
            json={
                "session_id": session_id,
                "message": ""
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "EMPTY_MESSAGE"
    
    @pytest.mark.asyncio
    async def test_send_message_whitespace_only(self, session_with_research):
        """测试发送仅空格的消息"""
        client, access_token, user_id, session_id = session_with_research
        
        response = await client.post(
            "/api/chat/send",
            headers=auth_header(access_token),
            json={
                "session_id": session_id,
                "message": "   "
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "EMPTY_MESSAGE"
    
    @pytest.mark.asyncio
    async def test_send_message_invalid_session(self, authenticated_client):
        """测试发送到不存在的会话"""
        client, access_token, user_id = authenticated_client
        
        with patch('app.services.chat_service.LLMClient'):
            response = await client.post(
                "/api/chat/send",
                headers=auth_header(access_token),
                json={
                    "session_id": "non-existent-session-id",
                    "message": "测试消息"
                }
            )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "SESSION_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_send_message_unauthorized(self, client: AsyncClient):
        """测试未认证用户无法发送消息"""
        response = await client.post(
            "/api/chat/send",
            json={
                "session_id": "some-session-id",
                "message": "测试消息"
            }
        )
        
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_send_message_with_attached_papers(self, session_with_research):
        """测试发送带论文附件的消息"""
        client, access_token, user_id, session_id = session_with_research
        
        with patch('app.services.chat_service.LLMClient') as mock_llm_class, \
             patch('app.services.chat_service.get_enhanced_graphiti') as mock_graphiti:
            
            mock_llm_instance = MagicMock()
            mock_llm_instance.chat_with_context = AsyncMock(return_value="基于论文的回复")
            mock_llm_class.return_value = mock_llm_instance
            
            mock_graphiti_instance = AsyncMock()
            mock_graphiti_instance.add_episode = AsyncMock()
            mock_graphiti.return_value = mock_graphiti_instance
            
            response = await client.post(
                "/api/chat/send",
                headers=auth_header(access_token),
                json={
                    "session_id": session_id,
                    "message": "分析这篇论文",
                    "attached_papers": ["paper_id_1", "paper_id_2"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证附件论文被记录
            assert data["user_message"]["attached_papers"] == ["paper_id_1", "paper_id_2"]


class TestChatHistory:
    """获取聊天历史测试 REQ-CHAT-4"""
    
    @pytest.fixture
    async def session_with_messages(self, authenticated_client):
        """创建带有消息的会话fixture"""
        client, access_token, user_id = authenticated_client
        
        # 创建研究会话
        create_response = await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={
                "title": "历史记录测试会话",
                "domains": ["AI"]
            }
        )
        session_id = create_response.json()["session_id"]
        
        # 发送几条消息
        with patch('app.services.chat_service.LLMClient') as mock_llm_class, \
             patch('app.services.chat_service.get_enhanced_graphiti') as mock_graphiti:
            
            mock_llm_instance = MagicMock()
            mock_llm_instance.chat_with_context = AsyncMock(return_value="AI回复")
            mock_llm_class.return_value = mock_llm_instance
            
            mock_graphiti_instance = AsyncMock()
            mock_graphiti_instance.search = AsyncMock(return_value=[])
            mock_graphiti_instance.add_episode = AsyncMock()
            mock_graphiti.return_value = mock_graphiti_instance
            
            for i in range(3):
                await client.post(
                    "/api/chat/send",
                    headers=auth_header(access_token),
                    json={
                        "session_id": session_id,
                        "message": f"测试消息{i+1}"
                    }
                )
        
        return client, access_token, user_id, session_id
    
    @pytest.mark.asyncio
    async def test_get_history_success(self, session_with_messages):
        """测试成功获取聊天历史"""
        client, access_token, user_id, session_id = session_with_messages
        
        response = await client.get(
            f"/api/chat/history/{session_id}",
            headers=auth_header(access_token)
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert data["session_id"] == session_id
        assert "session_info" in data
        assert "messages" in data
        assert "pagination" in data
        
        # 验证会话信息
        assert data["session_info"]["title"] == "历史记录测试会话"
        assert "domains" in data["session_info"]
        
        # 验证消息（3条用户消息 + 3条AI回复 = 6条）
        assert len(data["messages"]) == 6
        
        # 验证消息结构
        msg = data["messages"][0]
        assert "message_id" in msg
        assert "role" in msg
        assert "content" in msg
        assert "created_at" in msg
    
    @pytest.mark.asyncio
    async def test_get_history_empty(self, authenticated_client):
        """测试空会话的历史记录"""
        client, access_token, user_id = authenticated_client
        
        # 创建空会话
        create_response = await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={
                "title": "空会话",
                "domains": ["AI"]
            }
        )
        session_id = create_response.json()["session_id"]
        
        response = await client.get(
            f"/api/chat/history/{session_id}",
            headers=auth_header(access_token)
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["messages"] == []
        assert data["pagination"]["total"] == 0
    
    @pytest.mark.asyncio
    async def test_get_history_pagination(self, session_with_messages):
        """测试历史记录分页"""
        client, access_token, user_id, session_id = session_with_messages
        
        # 获取前2条
        response = await client.get(
            f"/api/chat/history/{session_id}",
            headers=auth_header(access_token),
            params={"limit": 2, "offset": 0}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["messages"]) == 2
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert data["pagination"]["has_more"] is True
    
    @pytest.mark.asyncio
    async def test_get_history_order_asc(self, session_with_messages):
        """测试历史记录升序排列"""
        client, access_token, user_id, session_id = session_with_messages
        
        response = await client.get(
            f"/api/chat/history/{session_id}",
            headers=auth_header(access_token),
            params={"order": "asc"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证按时间升序（第一条消息在前）
        if len(data["messages"]) >= 2:
            first_time = data["messages"][0]["created_at"]
            second_time = data["messages"][1]["created_at"]
            assert first_time <= second_time
    
    @pytest.mark.asyncio
    async def test_get_history_order_desc(self, session_with_messages):
        """测试历史记录降序排列"""
        client, access_token, user_id, session_id = session_with_messages
        
        response = await client.get(
            f"/api/chat/history/{session_id}",
            headers=auth_header(access_token),
            params={"order": "desc"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证按时间降序（最新消息在前）
        if len(data["messages"]) >= 2:
            first_time = data["messages"][0]["created_at"]
            second_time = data["messages"][1]["created_at"]
            assert first_time >= second_time
    
    @pytest.mark.asyncio
    async def test_get_history_invalid_session(self, authenticated_client):
        """测试获取不存在会话的历史"""
        client, access_token, user_id = authenticated_client
        
        response = await client.get(
            "/api/chat/history/non-existent-session-id",
            headers=auth_header(access_token)
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "SESSION_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_get_history_unauthorized(self, client: AsyncClient):
        """测试未认证用户无法获取历史"""
        response = await client.get("/api/chat/history/some-session-id")
        
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_get_history_other_user_session(self, client: AsyncClient, authenticated_client):
        """测试无法获取其他用户的会话历史"""
        # 用户A创建会话
        client_a, token_a, user_id_a = authenticated_client
        
        create_response = await client_a.post(
            "/api/research/create",
            headers=auth_header(token_a),
            json={
                "title": "用户A的会话",
                "domains": ["AI"]
            }
        )
        session_id = create_response.json()["session_id"]
        
        # 创建用户B
        await client.post(
            "/api/auth/register",
            json={"username": "userB_chat", "password": "UserBPass123"}
        )
        login_b = await client.post(
            "/api/auth/login",
            json={"username": "userB_chat", "password": "UserBPass123"}
        )
        token_b = login_b.json()["access_token"]
        
        # 用户B尝试获取用户A的会话历史
        response = await client.get(
            f"/api/chat/history/{session_id}",
            headers=auth_header(token_b)
        )
        
        # 应该返回404（会话不属于用户B）
        assert response.status_code == 404

