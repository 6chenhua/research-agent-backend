"""
认证模块单元测试
测试用户注册、登录、Token管理等功能
根据PRD_认证模块.md设计
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.db_models import User
from app.core.security import hash_password, verify_password, decode_token
from app.core.redis_client import is_token_blacklisted, get_failed_login_count


class TestUserRegistration:
    """用户注册测试 REQ-AUTH-1"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功注册"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "researcher001",
                "password": "Password123",
                "email": "researcher@example.com"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # PRD要求：只返回 user_id, username, created_at, message
        assert "user_id" in data
        assert data["username"] == "researcher001"
        assert "created_at" in data
        assert data["message"] == "Registration successful"
        
        # PRD要求：注册不返回token
        assert "access_token" not in data
        assert "refresh_token" not in data
        
        # 验证数据库中创建了用户
        result = await test_session.execute(
            select(User).where(User.username == "researcher001")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == "researcher@example.com"
    
    @pytest.mark.asyncio
    async def test_register_without_email(self, client: AsyncClient, test_session: AsyncSession):
        """测试不提供邮箱注册（email是可选的）"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser_no_email",
                "password": "Password123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "user_id" in data
        assert data["username"] == "testuser_no_email"
        assert data["message"] == "Registration successful"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_session: AsyncSession):
        """测试重复用户名注册"""
        # 第一次注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "duplicate_user",
                "password": "Password123"
            }
        )
        
        # 第二次注册相同用户名
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "duplicate_user",
                "password": "Password456"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_INPUT"
        assert "Username already exists" in data["detail"]["message"]
    
    @pytest.mark.asyncio
    async def test_register_invalid_username(self, client: AsyncClient):
        """测试无效用户名（含特殊字符）"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "invalid@user",  # 包含@，不符合正则
                "password": "Password123"
            }
        )
        
        # Pydantic 验证失败返回 422
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_username_too_short(self, client: AsyncClient):
        """测试用户名太短（少于3字符）"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "ab",  # 只有2字符
                "password": "Password123"
            }
        )
        
        # Pydantic 验证失败返回 422
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """测试弱密码（长度不足）"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "weak"
            }
        )
        
        # Pydantic 验证失败返回 422
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_password_missing_uppercase(self, client: AsyncClient):
        """测试密码缺少大写字母"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123"  # 缺少大写字母
            }
        )
        
        # Pydantic validator 验证失败返回 422
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_password_missing_lowercase(self, client: AsyncClient):
        """测试密码缺少小写字母"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "PASSWORD123"  # 缺少小写字母
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_password_missing_number(self, client: AsyncClient):
        """测试密码缺少数字"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "PasswordOnly"  # 缺少数字
            }
        )
        
        assert response.status_code == 422


class TestUserLogin:
    """用户登录测试 REQ-AUTH-2"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功登录"""
        # 先注册用户
        await client.post(
            "/api/auth/register",
            json={
                "username": "loginuser",
                "password": "Password123"
            }
        )
        
        # 使用用户名登录
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "loginuser",
                "password": "Password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # PRD要求的响应结构
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"  # 小写
        assert data["expires_in"] == 1800  # 30分钟
        assert "user" in data
        assert "user_id" in data["user"]
        assert data["user"]["username"] == "loginuser"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """测试错误密码"""
        # 先注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "testuser_pwd",
                "password": "CorrectPass123"
            }
        )
        
        # 使用错误密码登录
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser_pwd",
                "password": "WrongPass123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"] == "INVALID_CREDENTIALS"
        assert "Invalid username or password" in data["detail"]["message"]
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """测试不存在的用户"""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent_user",
                "password": "SomePass123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"] == "INVALID_CREDENTIALS"


class TestTokenRefresh:
    """Token刷新测试 REQ-AUTH-3"""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient):
        """测试成功刷新Token"""
        # 注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "refreshuser",
                "password": "RefreshPass123"
            }
        )
        
        # 登录获取refresh_token
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "refreshuser",
                "password": "RefreshPass123"
            }
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # 刷新Token
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"  # 小写
        assert data["expires_in"] == 1800  # 30分钟
    
    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """测试使用无效Token刷新"""
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token_here"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"] == "INVALID_TOKEN"


class TestUserLogout:
    """用户登出测试 REQ-AUTH-5"""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient):
        """测试成功登出"""
        # 注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "logoutuser",
                "password": "LogoutPass123"
            }
        )
        
        # 登录获取access_token
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "logoutuser",
                "password": "LogoutPass123"
            }
        )
        
        access_token = login_response.json()["access_token"]
        
        # 登出
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
        
        # 验证Token已加入黑名单
        is_blacklisted = await is_token_blacklisted(access_token)
        assert is_blacklisted is True


class TestChangePassword:
    """修改密码测试 REQ-AUTH-4"""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, client: AsyncClient, test_session: AsyncSession):
        """测试成功修改密码"""
        # 注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "changeuser",
                "password": "OldPass123"
            }
        )
        
        # 登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "changeuser",
                "password": "OldPass123"
            }
        )
        
        access_token = login_response.json()["access_token"]
        
        # 修改密码
        response = await client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": "OldPass123",
                "new_password": "NewPass456"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"
        assert data["require_relogin"] == True
        
        # 验证可以用新密码登录
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "changeuser",
                "password": "NewPass456"
            }
        )
        
        assert login_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, client: AsyncClient):
        """测试旧密码错误"""
        # 注册
        await client.post(
            "/api/auth/register",
            json={
                "username": "testuser_change",
                "password": "CorrectPass123"
            }
        )
        
        # 登录获取token
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser_change",
                "password": "CorrectPass123"
            }
        )
        
        access_token = login_response.json()["access_token"]
        
        # 使用错误的旧密码
        response = await client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": "WrongPass123",
                "new_password": "NewPass456"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"] == "WRONG_PASSWORD"
        assert "Old password is incorrect" in data["detail"]["message"]


class TestSecurityFunctions:
    """安全函数测试"""
    
    def test_password_hashing(self):
        """测试密码加密"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        # 验证加密后的密码不等于原密码
        assert hashed != password
        
        # 验证可以正确验证密码
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
    
    def test_jwt_token_decode(self):
        """测试JWT Token解码"""
        from app.core.security import create_access_token
        
        # 新的API签名
        token = create_access_token(
            user_id="test_user_id",
            username="test_username"
        )
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["user_id"] == "test_user_id"
        assert payload["username"] == "test_username"
        assert payload["type"] == "access"
        assert "exp" in payload
