"""
研究与聊天模块测试脚本
测试REQ-CHAT-1到REQ-CHAT-4的API功能
"""
import asyncio
import httpx
import json
import sys

# API基础URL
BASE_URL = "http://localhost:8000/api"

# 测试用户凭据（需要先注册）
TEST_USER = {
    "username": "test_chat_user",
    "password": "TestPassword123"
}


async def register_and_login() -> str:
    """注册用户并登录，返回access_token"""
    async with httpx.AsyncClient() as client:
        # 尝试注册
        register_response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"],
                "email": "test_chat@example.com"
            }
        )
        if register_response.status_code == 201:
            print("✅ 用户注册成功")
        elif register_response.status_code == 400:
            print("ℹ️ 用户已存在，跳过注册")
        else:
            print(f"⚠️ 注册返回: {register_response.status_code}")
        
        # 登录
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        
        if login_response.status_code == 200:
            data = login_response.json()
            print("✅ 用户登录成功")
            return data["access_token"]
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(login_response.text)
            sys.exit(1)


async def test_create_research_session(token: str) -> str:
    """测试创建研究会话 - REQ-CHAT-1"""
    print("\n" + "="*50)
    print("测试 REQ-CHAT-1: 创建研究会话")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/research/create",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "AI研究测试",
                "domains": ["AI", "SE"],
                "description": "测试研究会话创建"
            }
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 创建成功!")
            print(f"   - session_id: {data['session_id']}")
            print(f"   - title: {data['title']}")
            print(f"   - domains: {data['domains']}")
            print(f"   - community_build_triggered: {data['community_build_triggered']}")
            return data["session_id"]
        else:
            print(f"❌ 创建失败: {response.text}")
            return ""


async def test_list_research_sessions(token: str):
    """测试获取研究会话列表 - REQ-CHAT-2"""
    print("\n" + "="*50)
    print("测试 REQ-CHAT-2: 获取研究会话列表")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/research/list",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 10, "offset": 0, "sort": "created_desc"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取成功!")
            print(f"   - 会话数量: {len(data['sessions'])}")
            print(f"   - 分页信息: {data['pagination']}")
            for session in data["sessions"][:3]:
                print(f"   - {session['title']} (ID: {session['session_id'][:8]}...)")
        else:
            print(f"❌ 获取失败: {response.text}")


async def test_send_message(token: str, session_id: str):
    """测试发送消息 - REQ-CHAT-3"""
    print("\n" + "="*50)
    print("测试 REQ-CHAT-3: 发送消息")
    print("="*50)
    
    if not session_id:
        print("⚠️ 跳过测试：没有有效的session_id")
        return
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/chat/send",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": session_id,
                "message": "什么是Agent Memory技术？请简要介绍。",
                "attached_papers": [],
                "stream": False
            }
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 发送成功!")
            print(f"\n📤 用户消息:")
            print(f"   - ID: {data['user_message']['message_id']}")
            print(f"   - 内容: {data['user_message']['content'][:100]}...")
            
            print(f"\n📥 Agent回复:")
            print(f"   - ID: {data['agent_message']['message_id']}")
            print(f"   - 内容: {data['agent_message']['content'][:200]}...")
            
            if data['agent_message'].get('context_string'):
                print(f"\n📚 Context:")
                print(f"   {data['agent_message']['context_string'][:200]}...")
            
            print(f"\n📊 状态:")
            print(f"   - graph_updated: {data['status']['graph_updated']}")
        else:
            print(f"❌ 发送失败: {response.text}")


async def test_get_chat_history(token: str, session_id: str):
    """测试获取聊天历史 - REQ-CHAT-4"""
    print("\n" + "="*50)
    print("测试 REQ-CHAT-4: 获取聊天历史")
    print("="*50)
    
    if not session_id:
        print("⚠️ 跳过测试：没有有效的session_id")
        return
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/chat/history/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 50, "offset": 0, "order": "asc"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取成功!")
            print(f"   - 会话标题: {data['session_info']['title']}")
            print(f"   - 消息数量: {len(data['messages'])}")
            print(f"   - 分页信息: {data['pagination']}")
            
            print(f"\n📜 消息列表:")
            for msg in data["messages"][-4:]:  # 显示最后4条
                role_emoji = "👤" if msg["role"] == "user" else "🤖"
                content_preview = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
                print(f"   {role_emoji} [{msg['role']}] {content_preview}")
        else:
            print(f"❌ 获取失败: {response.text}")


async def test_error_cases(token: str):
    """测试错误情况"""
    print("\n" + "="*50)
    print("测试错误情况")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        # 测试空domains
        print("\n1. 测试空domains...")
        response = await client.post(
            f"{BASE_URL}/research/create",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "测试",
                "domains": [],
                "description": "测试"
            }
        )
        if response.status_code == 422:  # Pydantic验证错误
            print("   ✅ 正确返回验证错误")
        else:
            print(f"   ⚠️ 返回状态码: {response.status_code}")
        
        # 测试不存在的session
        print("\n2. 测试不存在的session...")
        response = await client.post(
            f"{BASE_URL}/chat/send",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": "non-existent-session-id",
                "message": "测试消息"
            }
        )
        if response.status_code == 404:
            print("   ✅ 正确返回404错误")
        else:
            print(f"   ⚠️ 返回状态码: {response.status_code}")
        
        # 测试空消息
        print("\n3. 测试空消息...")
        response = await client.post(
            f"{BASE_URL}/chat/send",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": "some-session",
                "message": ""
            }
        )
        if response.status_code == 400 or response.status_code == 422:
            print("   ✅ 正确返回错误")
        else:
            print(f"   ⚠️ 返回状态码: {response.status_code}")


async def main():
    """主测试流程"""
    print("="*60)
    print("研究与聊天模块测试")
    print("="*60)
    
    # 1. 注册并登录
    token = await register_and_login()
    
    # 2. 测试创建研究会话
    session_id = await test_create_research_session(token)
    
    # 3. 测试获取会话列表
    await test_list_research_sessions(token)
    
    # 4. 测试发送消息
    await test_send_message(token, session_id)
    
    # 5. 测试获取聊天历史
    await test_get_chat_history(token, session_id)
    
    # 6. 测试错误情况
    await test_error_cases(token)
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

