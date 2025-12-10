"""
认证模块单元测试
测试用户注册、登录、Token管理等功能
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.db_models import User
from app.core.security import hash_password, verify_password, decode_token
from app.core.redis_client import is_token_blacklisted, get_failed_login_count


class TestUserRegistration:
    """用户注册测试"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功注册"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # 验证响应数据
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["username"] == "testuser"
        assert data["token_type"] == "Bearer"
        
        # 验证数据库中创建了用户
        result = await test_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_session: AsyncSession):
        """测试重复邮箱注册"""
        # 第一次注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "user1",
                "email": "duplicate@example.com",
                "password": "TestPass123!"
            }
        )
        
        # 第二次注册相同邮箱
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "user2",
                "email": "duplicate@example.com",
                "password": "TestPass456!"
            }
        )
        
        assert response.status_code == 400
        assert "邮箱已被注册" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """测试弱密码（长度不足）"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "weak"
            }
        )
        
        # Pydantic 验证失败返回 422 (密码长度不足)
        assert response.status_code == 422
        # 422 错误的响应格式不同，是 detail 数组
        assert response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_password_missing_requirements(self, client: AsyncClient):
        """测试密码不符合强度要求"""
        # 长度够了，但缺少特殊字符、大写字母等
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "weakpassword123"  # 缺少大写字母和特殊字符
            }
        )
        
        # 业务逻辑验证失败返回 400
        assert response.status_code == 400
        assert "密码" in response.json()["detail"]


class TestUserLogin:
    """用户登录测试"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功登录"""
        # 先注册用户
        await client.post(
            "/api/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "LoginPass123!"
            }
        )
        
        # 登录
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "login@example.com",
                "password": "LoginPass123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "login@example.com"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """测试错误密码"""
        # 先注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "CorrectPass123!"
            }
        )
        
        # 使用错误密码登录
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPass123!"
            }
        )
        
        assert response.status_code == 401
        assert "邮箱或密码错误" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """测试不存在的用户"""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePass123!"
            }
        )
        
        assert response.status_code == 401
        assert "邮箱或密码错误" in response.json()["detail"]


class TestTokenRefresh:
    """Token刷新测试"""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient):
        """测试成功刷新Token"""
        # 注册并获取refresh_token
        register_response = await client.post(
            "/api/auth/register",
            json={
                "username": "refreshuser",
                "email": "refresh@example.com",
                "password": "RefreshPass123!"
            }
        )
        
        refresh_token = register_response.json()["refresh_token"]
        
        # 刷新Token
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "Bearer"
        assert "expires_in" in data
    
    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """测试使用无效Token刷新"""
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token_here"}
        )
        
        assert response.status_code == 401


class TestUserLogout:
    """用户登出测试"""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient):
        """测试成功登出"""
        # 注册并获取access_token
        register_response = await client.post(
            "/api/auth/register",
            json={
                "username": "logoutuser",
                "email": "logout@example.com",
                "password": "LogoutPass123!"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # 登出
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "登出成功"
        
        # 验证Token已加入黑名单
        is_blacklisted = await is_token_blacklisted(access_token)
        assert is_blacklisted is True


class TestGetCurrentUser:
    """获取当前用户信息测试"""
    
    @pytest.mark.asyncio
    async def test_get_me_success(self, client: AsyncClient):
        """测试成功获取用户信息"""
        # 注册
        register_response = await client.post(
            "/api/auth/register",
            json={
                "username": "meuser",
                "email": "me@example.com",
                "password": "MePass123!"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # 获取用户信息
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "me@example.com"
        assert data["username"] == "meuser"
        assert "user_id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_get_me_without_token(self, client: AsyncClient):
        """测试未提供Token"""
        response = await client.get("/api/auth/me")
        
        # 未提供 token 应该返回 401 Unauthorized，而不是 403
        assert response.status_code == 401


class TestChangePassword:
    """修改密码测试"""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功修改密码"""
        # 注册
        register_response = await client.post(
            "/api/auth/register",
            json={
                "username": "changeuser",
                "email": "change@example.com",
                "password": "OldPass123!"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # 修改密码
        response = await client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": "OldPass123!",
                "new_password": "NewPass456!"
            }
        )
        
        assert response.status_code == 200
        assert "密码修改成功" in response.json()["message"]
        
        # 验证可以用新密码登录
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": "change@example.com",
                "password": "NewPass456!"
            }
        )
        
        assert login_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, client: AsyncClient):
        """测试旧密码错误"""
        # 注册
        register_response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "CorrectPass123!"
            }
        )
        
        access_token = register_response.json()["access_token"]
        
        # 使用错误的旧密码
        response = await client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": "WrongPass123!",
                "new_password": "NewPass456!"
            }
        )
        
        assert response.status_code == 400
        assert "旧密码错误" in response.json()["detail"]


class TestSecurityFunctions:
    """安全函数测试"""
    
    def test_password_hashing(self):
        """测试密码加密"""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        # 验证加密后的密码不等于原密码
        assert hashed != password
        
        # 验证可以正确验证密码
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
    
    def test_jwt_token_decode(self):
        """测试JWT Token解码"""
        from app.core.security import create_access_token
        
        token = create_access_token({
            "sub": "test_user_id",
            "email": "test@example.com"
        })
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test_user_id"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload
        assert "iat" in payload

