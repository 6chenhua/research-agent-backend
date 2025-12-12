"""
图谱模块测试脚本
测试PRD_图谱模块.md中定义的4个API接口

使用方法:
1. 确保服务已启动: python -m uvicorn main:app --reload
2. 运行测试: python scripts/test_graph_module.py

测试接口:
- REQ-GRAPH-1: GET /api/v1/graph/{user_id} - 获取用户图谱
- REQ-GRAPH-2: GET /api/v1/graph/node/{node_uuid} - 获取节点详情
- REQ-GRAPH-3: GET /api/v1/graph/edge/{edge_uuid} - 获取边详情
- REQ-GRAPH-4: GET /api/v1/graph/stats - 图谱统计信息
"""
import asyncio
import httpx
from typing import Optional

BASE_URL = "http://localhost:8000"


async def login(client: httpx.AsyncClient, username: str, password: str) -> Optional[str]:
    """登录并获取access_token"""
    try:
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None


async def register(client: httpx.AsyncClient, username: str, password: str) -> bool:
    """注册新用户"""
    try:
        response = await client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": username,
                "password": password,
                "email": f"{username}@test.com"
            }
        )
        if response.status_code == 201:
            print(f"✅ 注册成功: {username}")
            return True
        elif response.status_code == 409:
            print(f"ℹ️ 用户已存在: {username}")
            return True
        else:
            print(f"❌ 注册失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 注册异常: {str(e)}")
        return False


async def test_req_graph_4_stats(client: httpx.AsyncClient, token: str) -> tuple[bool, Optional[str]]:
    """测试REQ-GRAPH-4: 获取图谱统计信息"""
    print("\n" + "=" * 60)
    print("测试 REQ-GRAPH-4: GET /api/v1/graph/stats")
    print("=" * 60)
    
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/graph/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get('user_id')
            print(f"✅ 成功获取图谱统计")
            print(f"   用户ID: {user_id}")
            stats = data.get('statistics', {})
            print(f"   总节点数: {stats.get('total_nodes', 0)}")
            print(f"   总边数: {stats.get('total_edges', 0)}")
            print(f"   节点类型分布: {stats.get('node_types', {})}")
            print(f"   领域分布: {stats.get('entity_domains', {})}")
            print(f"   Top实体: {len(stats.get('top_entities', []))} 个")
            return True, user_id
        else:
            print(f"❌ 失败: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False, None


async def test_req_graph_1_user_graph(client: httpx.AsyncClient, token: str, user_id: str) -> bool:
    """测试REQ-GRAPH-1: 获取用户图谱"""
    print("\n" + "=" * 60)
    print(f"测试 REQ-GRAPH-1: GET /api/v1/graph/{user_id}")
    print("=" * 60)
    
    try:
        response = await client.get(
            f"{BASE_URL}/api/v1/graph/{user_id}",
            params={"mode": "simple", "include_episodes": False, "limit": 100},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取用户图谱")
            print(f"   用户ID: {data.get('user_id')}")
            stats = data.get('graph_stats', {})
            print(f"   总节点数: {stats.get('total_nodes', 0)}")
            print(f"   总边数: {stats.get('total_edges', 0)}")
            print(f"   实体节点: {stats.get('entity_count', 0)}")
            print(f"   Episode节点: {stats.get('episode_count', 0)}")
            print(f"   返回节点数: {len(data.get('nodes', []))}")
            print(f"   返回边数: {len(data.get('edges', []))}")
            return True
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


async def test_access_denied(client: httpx.AsyncClient, token: str) -> bool:
    """测试权限校验：尝试访问其他用户的图谱"""
    print("\n" + "=" * 60)
    print("测试权限校验: 尝试访问其他用户图谱")
    print("=" * 60)
    
    try:
        # 使用一个假的user_id
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(
            f"{BASE_URL}/api/v1/graph/{fake_user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 403:
            print(f"✅ 权限校验正确，拒绝访问其他用户图谱")
            data = response.json()
            detail = data.get('detail', {})
            if isinstance(detail, dict):
                print(f"   错误代码: {detail.get('error', 'N/A')}")
                print(f"   错误信息: {detail.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ 权限校验失败，应该返回403，实际返回 {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


async def test_req_graph_2_node_not_found(client: httpx.AsyncClient, token: str) -> bool:
    """测试REQ-GRAPH-2: 节点不存在"""
    print("\n" + "=" * 60)
    print("测试 REQ-GRAPH-2: 节点不存在情况")
    print("=" * 60)
    
    try:
        fake_node_uuid = "non_existent_node_uuid"
        response = await client.get(
            f"{BASE_URL}/api/v1/graph/node/{fake_node_uuid}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 404:
            print(f"✅ 正确返回404，节点不存在")
            data = response.json()
            detail = data.get('detail', {})
            if isinstance(detail, dict):
                print(f"   错误代码: {detail.get('error', 'N/A')}")
            return True
        else:
            print(f"❌ 应该返回404，实际返回 {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


async def test_req_graph_3_edge_not_found(client: httpx.AsyncClient, token: str) -> bool:
    """测试REQ-GRAPH-3: 边不存在"""
    print("\n" + "=" * 60)
    print("测试 REQ-GRAPH-3: 边不存在情况")
    print("=" * 60)
    
    try:
        fake_edge_uuid = "non_existent_edge_uuid"
        response = await client.get(
            f"{BASE_URL}/api/v1/graph/edge/{fake_edge_uuid}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 404:
            print(f"✅ 正确返回404，边不存在")
            data = response.json()
            detail = data.get('detail', {})
            if isinstance(detail, dict):
                print(f"   错误代码: {detail.get('error', 'N/A')}")
            return True
        else:
            print(f"❌ 应该返回404，实际返回 {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


async def test_unauthenticated(client: httpx.AsyncClient) -> bool:
    """测试未认证访问"""
    print("\n" + "=" * 60)
    print("测试未认证访问")
    print("=" * 60)
    
    try:
        response = await client.get(f"{BASE_URL}/api/v1/graph/stats")
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code in [401, 403]:
            print(f"✅ 正确拒绝未认证请求")
            return True
        else:
            print(f"❌ 应该返回401或403，实际返回 {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


async def main():
    """主测试函数"""
    print("=" * 60)
    print("图谱模块测试 (PRD_图谱模块.md)")
    print("=" * 60)
    print("\n测试接口:")
    print("  - REQ-GRAPH-1: GET /api/v1/graph/{user_id}")
    print("  - REQ-GRAPH-2: GET /api/v1/graph/node/{node_uuid}")
    print("  - REQ-GRAPH-3: GET /api/v1/graph/edge/{edge_uuid}")
    print("  - REQ-GRAPH-4: GET /api/v1/graph/stats")
    
    # 测试用户凭证
    TEST_USERNAME = "graph_test_user"
    TEST_PASSWORD = "TestPass123"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 检查服务是否运行
        try:
            health = await client.get(f"{BASE_URL}/health")
            if health.status_code != 200:
                print(f"\n❌ 服务未运行，请先启动: uvicorn main:app --reload")
                return
            print("\n✅ 服务运行正常")
        except Exception as e:
            print(f"\n❌ 无法连接到服务: {str(e)}")
            print("   请先启动服务: uvicorn main:app --reload")
            return
        
        # 2. 测试未认证访问
        results = []
        results.append(("未认证访问拒绝", await test_unauthenticated(client)))
        
        # 3. 注册/登录
        await register(client, TEST_USERNAME, TEST_PASSWORD)
        token = await login(client, TEST_USERNAME, TEST_PASSWORD)
        
        if not token:
            print("\n❌ 无法获取认证token，测试终止")
            return
        
        print(f"\n✅ 登录成功，获取到token")
        
        # 4. 执行测试
        
        # REQ-GRAPH-4: 图谱统计（同时获取user_id）
        success, user_id = await test_req_graph_4_stats(client, token)
        results.append(("REQ-GRAPH-4: 图谱统计", success))
        
        # REQ-GRAPH-1: 获取用户图谱
        if user_id:
            results.append(("REQ-GRAPH-1: 获取用户图谱", await test_req_graph_1_user_graph(client, token, user_id)))
        else:
            print("\n⚠️ 无法获取user_id，跳过REQ-GRAPH-1测试")
        
        # 权限校验测试
        results.append(("权限校验（访问其他用户）", await test_access_denied(client, token)))
        
        # REQ-GRAPH-2: 节点不存在
        results.append(("REQ-GRAPH-2: 节点不存在", await test_req_graph_2_node_not_found(client, token)))
        
        # REQ-GRAPH-3: 边不存在
        results.append(("REQ-GRAPH-3: 边不存在", await test_req_graph_3_edge_not_found(client, token)))
        
        # 5. 打印测试结果摘要
        print("\n" + "=" * 60)
        print("测试结果摘要")
        print("=" * 60)
        
        passed = 0
        failed = 0
        for name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {name}: {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\n   总计: {passed} 通过, {failed} 失败")
        print("=" * 60)
        
        if failed == 0:
            print("\n🎉 所有测试通过！")
        else:
            print(f"\n⚠️ 有 {failed} 个测试失败，请检查")


if __name__ == "__main__":
    asyncio.run(main())
