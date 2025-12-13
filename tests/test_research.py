"""
研究会话模块测试
测试研究会话的创建、列表查询等功能
根据PRD_研究与聊天模块.md设计
"""
import pytest
from httpx import AsyncClient

from tests.conftest import auth_header


class TestCreateResearchSession:
    """创建研究会话测试 REQ-CHAT-1"""
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, authenticated_client):
        """测试成功创建研究会话"""
        client, access_token, user_id = authenticated_client
        
        response = await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={
                "title": "AI研究会话",
                "domains": ["AI", "Machine Learning"],
                "description": "研究人工智能相关论文"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "session_id" in data
        assert data["title"] == "AI研究会话"
        assert data["domains"] == ["AI", "Machine Learning"]
        assert "created_at" in data
        assert data["message"] == "Research session created successfully"
        assert data["community_build_triggered"] is True
    
    @pytest.mark.asyncio
    async def test_create_session_with_default_title(self, authenticated_client):
        """测试不提供标题时自动生成"""
        client, access_token, user_id = authenticated_client
        
        response = await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={
                "domains": ["Software Engineering"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # 标题应该自动生成，包含domain和日期
        assert "session_id" in data
        assert "Software Engineering" in data["title"]
        assert data["domains"] == ["Software Engineering"]
    
    @pytest.mark.asyncio
    async def test_create_session_without_domains(self, authenticated_client):
        """测试不提供domains报错"""
        client, access_token, user_id = authenticated_client
        
        response = await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={
                "title": "无领域会话",
                "domains": []  # 空数组
            }
        )
        
        # Pydantic schema 验证 min_length=1，空数组返回 422
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_session_unauthorized(self, client: AsyncClient):
        """测试未认证用户无法创建会话"""
        response = await client.post(
            "/api/research/create",
            json={
                "title": "测试会话",
                "domains": ["AI"]
            }
        )
        
        # 未提供token应返回401或403
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_create_multiple_sessions(self, authenticated_client):
        """测试同一用户可创建多个会话"""
        client, access_token, user_id = authenticated_client
        
        # 创建第一个会话
        response1 = await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={
                "title": "会话1",
                "domains": ["AI"]
            }
        )
        assert response1.status_code == 201
        
        # 创建第二个会话
        response2 = await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={
                "title": "会话2",
                "domains": ["SE"]
            }
        )
        assert response2.status_code == 201
        
        # 确认是不同的会话
        assert response1.json()["session_id"] != response2.json()["session_id"]


class TestListResearchSessions:
    """获取研究会话列表测试 REQ-CHAT-2"""
    
    @pytest.mark.asyncio
    async def test_list_sessions_empty(self, authenticated_client):
        """测试空列表返回"""
        client, access_token, user_id = authenticated_client
        
        response = await client.get(
            "/api/research/list",
            headers=auth_header(access_token)
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["sessions"] == []
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["has_more"] is False
    
    @pytest.mark.asyncio
    async def test_list_sessions_with_data(self, authenticated_client):
        """测试有数据时的列表返回"""
        client, access_token, user_id = authenticated_client
        
        # 创建3个会话
        for i in range(3):
            await client.post(
                "/api/research/create",
                headers=auth_header(access_token),
                json={
                    "title": f"测试会话{i+1}",
                    "domains": ["AI"]
                }
            )
        
        # 获取列表
        response = await client.get(
            "/api/research/list",
            headers=auth_header(access_token)
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["sessions"]) == 3
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["has_more"] is False
        
        # 验证会话结构
        session = data["sessions"][0]
        assert "session_id" in session
        assert "title" in session
        assert "domains" in session
        assert "message_count" in session
        assert "created_at" in session
    
    @pytest.mark.asyncio
    async def test_list_sessions_pagination(self, authenticated_client):
        """测试分页功能"""
        client, access_token, user_id = authenticated_client
        
        # 创建5个会话
        for i in range(5):
            await client.post(
                "/api/research/create",
                headers=auth_header(access_token),
                json={
                    "title": f"分页测试会话{i+1}",
                    "domains": ["AI"]
                }
            )
        
        # 获取第一页（每页2个）
        response = await client.get(
            "/api/research/list",
            headers=auth_header(access_token),
            params={"limit": 2, "offset": 0}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["sessions"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert data["pagination"]["has_more"] is True
        
        # 获取第二页
        response2 = await client.get(
            "/api/research/list",
            headers=auth_header(access_token),
            params={"limit": 2, "offset": 2}
        )
        
        data2 = response2.json()
        assert len(data2["sessions"]) == 2
        assert data2["pagination"]["offset"] == 2
        assert data2["pagination"]["has_more"] is True
    
    @pytest.mark.asyncio
    async def test_list_sessions_sort_by_created(self, authenticated_client):
        """测试按创建时间排序"""
        import asyncio
        client, access_token, user_id = authenticated_client
        
        # 创建会话（添加短暂延迟确保时间戳不同）
        await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={"title": "第一个会话", "domains": ["AI"]}
        )
        await asyncio.sleep(0.1)  # 确保时间戳不同
        await client.post(
            "/api/research/create",
            headers=auth_header(access_token),
            json={"title": "第二个会话", "domains": ["SE"]}
        )
        
        # 默认按创建时间倒序
        response = await client.get(
            "/api/research/list",
            headers=auth_header(access_token),
            params={"sort": "created_desc"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 最新创建的应该在前面
        assert len(data["sessions"]) == 2
        # 验证是倒序排列（最新的在前）
        first_time = data["sessions"][0]["created_at"]
        second_time = data["sessions"][1]["created_at"]
        assert first_time >= second_time
    
    @pytest.mark.asyncio
    async def test_list_sessions_unauthorized(self, client: AsyncClient):
        """测试未认证用户无法获取列表"""
        response = await client.get("/api/research/list")
        
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_list_sessions_isolation(self, client: AsyncClient, authenticated_client):
        """测试用户数据隔离（用户只能看到自己的会话）"""
        # 用户A创建会话
        client_a, token_a, user_id_a = authenticated_client
        
        await client_a.post(
            "/api/research/create",
            headers=auth_header(token_a),
            json={"title": "用户A的会话", "domains": ["AI"]}
        )
        
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
        
        # 用户B获取列表应该为空
        response = await client.get(
            "/api/research/list",
            headers=auth_header(token_b)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 0

