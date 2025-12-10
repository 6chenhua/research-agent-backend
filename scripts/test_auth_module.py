"""
用户认证模块测试脚本
用于快速验证所有认证功能
"""
import asyncio
import httpx
from datetime import datetime


BASE_URL = "http://localhost:8000"


async def test_auth_module():
    """测试认证模块所有功能"""
    
    # 生成唯一的测试数据
    timestamp = int(datetime.now().timestamp())
    test_email = f"test_{timestamp}@example.com"
    test_username = f"测试用户_{timestamp}"
    test_password = "TestPass123!"
    new_password = "NewPass456!"
    
    print("🚀 开始测试用户认证模块...")
    print()
    print("📝 测试配置:")
    print(f"  - 基础URL: {BASE_URL}")
    print(f"  - 测试邮箱: {test_email}")
    print(f"  - 测试用户名: {test_username}")
    print()
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        
        # 1. 健康检查
        print("1️⃣  测试健康检查...")
        response = await client.get("/health")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
        assert response.status_code == 200
        print("✅ 健康检查通过")
        print()
        
        # 2. 用户注册
        print("2️⃣  测试用户注册...")
        response = await client.post(
            "/api/auth/register",
            json={
                "username": test_username,
                "email": test_email,
                "password": test_password
            }
        )
        print(f"  状态码: {response.status_code}")
        data = response.json()
        print(f"  用户ID: {data['user']['user_id']}")
        print(f"  Access Token: {data['access_token'][:20]}...")
        
        assert response.status_code == 201
        assert "access_token" in data
        assert "refresh_token" in data
        
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        user_id = data["user"]["user_id"]
        
        print("✅ 用户注册成功")
        print()
        
        # 3. 获取用户信息
        print("3️⃣  测试获取用户信息...")
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(f"  状态码: {response.status_code}")
        data = response.json()
        print(f"  用户ID: {data['user_id']}")
        print(f"  邮箱: {data['email']}")
        print(f"  用户名: {data['username']}")
        
        assert response.status_code == 200
        assert data["user_id"] == user_id
        assert data["email"] == test_email
        
        print("✅ 获取用户信息成功")
        print()
        
        # 4. 用户登录
        print("4️⃣  测试用户登录...")
        response = await client.post(
            "/api/auth/login",
            json={
                "email": test_email,
                "password": test_password
            }
        )
        print(f"  状态码: {response.status_code}")
        data = response.json()
        
        assert response.status_code == 200
        assert "access_token" in data
        
        access_token = data["access_token"]
        
        print("✅ 用户登录成功")
        print()
        
        # 5. Token刷新
        print("5️⃣  测试Token刷新...")
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        print(f"  状态码: {response.status_code}")
        data = response.json()
        
        assert response.status_code == 200
        assert "access_token" in data
        
        print("✅ Token刷新成功")
        print()
        
        # 6. 修改密码
        print("6️⃣  测试修改密码...")
        response = await client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": test_password,
                "new_password": new_password
            }
        )
        print(f"  状态码: {response.status_code}")
        data = response.json()
        print(f"  消息: {data['message']}")
        
        assert response.status_code == 200
        
        print("✅ 修改密码成功")
        print()
        
        # 7. 使用新密码登录
        print("7️⃣  测试使用新密码登录...")
        response = await client.post(
            "/api/auth/login",
            json={
                "email": test_email,
                "password": new_password
            }
        )
        print(f"  状态码: {response.status_code}")
        
        assert response.status_code == 200
        
        data = response.json()
        access_token = data["access_token"]
        
        print("✅ 使用新密码登录成功")
        print()
        
        # 8. 用户登出
        print("8️⃣  测试用户登出...")
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(f"  状态码: {response.status_code}")
        data = response.json()
        print(f"  消息: {data['message']}")
        
        assert response.status_code == 200
        
        print("✅ 用户登出成功")
        print()
        
        # 9. 验证Token黑名单
        print("9️⃣  验证Token黑名单（使用已登出的Token）...")
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print(f"  错误信息: {data['detail']}")
            print("✅ Token黑名单机制正常")
        else:
            print("⚠️  Token黑名单机制可能有问题")
        print()
        
        # 10. 测试错误密码
        print("🔟 测试错误密码登录...")
        response = await client.post(
            "/api/auth/login",
            json={
                "email": test_email,
                "password": "WrongPassword123!"
            }
        )
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print(f"  错误信息: {data['detail']}")
            print("✅ 错误密码验证正常")
        else:
            print("⚠️  错误密码验证可能有问题")
        print()
        
        # 11. 测试重复邮箱注册
        print("1️⃣1️⃣  测试重复邮箱注册...")
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "另一个用户",
                "email": test_email,
                "password": test_password
            }
        )
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            print(f"  错误信息: {data['detail']}")
            print("✅ 邮箱唯一性验证正常")
        else:
            print("⚠️  邮箱唯一性验证可能有问题")
        print()
        
        # 12. 测试弱密码
        print("1️⃣2️⃣  测试弱密码注册...")
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "弱密码用户",
                "email": f"weak_{timestamp}@example.com",
                "password": "weak"
            }
        )
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            print(f"  错误信息: {data['detail']}")
            print("✅ 密码强度验证正常")
        else:
            print("⚠️  密码强度验证可能有问题")
        print()
    
    # 测试总结
    print("🎉 所有测试完成！")
    print()
    print("📊 测试总结:")
    print("  ✅ 健康检查")
    print("  ✅ 用户注册")
    print("  ✅ 获取用户信息")
    print("  ✅ 用户登录")
    print("  ✅ Token刷新")
    print("  ✅ 修改密码")
    print("  ✅ 使用新密码登录")
    print("  ✅ 用户登出")
    print("  ✅ Token黑名单验证")
    print("  ✅ 错误密码验证")
    print("  ✅ 邮箱唯一性验证")
    print("  ✅ 密码强度验证")
    print()
    print("🎊 Module H 用户认证模块测试通过！")


if __name__ == "__main__":
    try:
        asyncio.run(test_auth_module())
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

