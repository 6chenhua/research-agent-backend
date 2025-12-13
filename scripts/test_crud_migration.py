"""
CRUD 迁移验证脚本
验证重构后的代码结构是否正确
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试模块导入是否正常"""
    print("=" * 60)
    print("CRUD 迁移验证测试")
    print("=" * 60)
    
    errors = []
    successes = []
    
    # 1. 测试 CRUD 模块导入
    print("\n[1] 测试 CRUD 模块导入...")
    try:
        from app.crud import (
            BaseRepository,
            UserRepository,
            SessionRepository,
            MessageRepository,
            PaperRepository
        )
        successes.append("✅ CRUD 模块导入成功")
        print("   ✅ BaseRepository, UserRepository, SessionRepository, MessageRepository, PaperRepository")
    except Exception as e:
        errors.append(f"❌ CRUD 模块导入失败: {e}")
        print(f"   ❌ 错误: {e}")
    
    # 2. 测试 Services 模块导入
    print("\n[2] 测试 Services 模块导入...")
    try:
        from app.services.auth_service import AuthService
        from app.services.research_service import ResearchService
        from app.services.chat_service import ChatService
        from app.services.ingest_service import IngestService
        successes.append("✅ Services 模块导入成功")
        print("   ✅ AuthService, ResearchService, ChatService, IngestService")
    except Exception as e:
        errors.append(f"❌ Services 模块导入失败: {e}")
        print(f"   ❌ 错误: {e}")
    
    # 3. 测试依赖注入模块导入
    print("\n[3] 测试依赖注入模块导入...")
    try:
        from app.api.dependencies.services import (
            get_user_repository,
            get_session_repository,
            get_message_repository,
            get_paper_repository,
            get_auth_service,
            get_research_service,
            get_chat_service,
            get_ingest_service
        )
        successes.append("✅ 依赖注入模块导入成功")
        print("   ✅ 所有依赖注入函数")
    except Exception as e:
        errors.append(f"❌ 依赖注入模块导入失败: {e}")
        print(f"   ❌ 错误: {e}")
    
    # 4. 测试路由模块导入
    print("\n[4] 测试路由模块导入...")
    try:
        from app.api.routes.auth import router as auth_router
        from app.api.routes.research import router as research_router
        from app.api.routes.chat import router as chat_router
        successes.append("✅ 路由模块导入成功")
        print("   ✅ auth_router, research_router, chat_router")
    except Exception as e:
        errors.append(f"❌ 路由模块导入失败: {e}")
        print(f"   ❌ 错误: {e}")
    
    # 5. 测试 Service 类签名
    print("\n[5] 测试 Service 类初始化签名...")
    try:
        from app.services.auth_service import AuthService
        from app.crud.user import UserRepository
        import inspect
        
        sig = inspect.signature(AuthService.__init__)
        params = list(sig.parameters.keys())
        
        if 'user_repo' in params:
            successes.append("✅ AuthService 接收 UserRepository 参数")
            print("   ✅ AuthService.__init__(self, user_repo: UserRepository)")
        else:
            errors.append("❌ AuthService 未正确定义 user_repo 参数")
            print(f"   ❌ AuthService 参数: {params}")
    except Exception as e:
        errors.append(f"❌ Service 类签名检查失败: {e}")
        print(f"   ❌ 错误: {e}")
    
    # 6. 测试 Repository 继承关系
    print("\n[6] 测试 Repository 继承关系...")
    try:
        from app.crud.base import BaseRepository
        from app.crud.user import UserRepository
        from app.crud.session import SessionRepository
        from app.crud.message import MessageRepository
        from app.crud.paper import PaperRepository
        
        # 检查是否是 BaseRepository 的子类
        repos = [
            ('UserRepository', UserRepository),
            ('SessionRepository', SessionRepository),
            ('MessageRepository', MessageRepository),
            ('PaperRepository', PaperRepository),
        ]
        
        all_inherit = True
        for name, repo_class in repos:
            if not issubclass(repo_class, BaseRepository):
                all_inherit = False
                errors.append(f"❌ {name} 未继承 BaseRepository")
                print(f"   ❌ {name} 未继承 BaseRepository")
        
        if all_inherit:
            successes.append("✅ 所有 Repository 都继承自 BaseRepository")
            print("   ✅ 所有 Repository 都继承自 BaseRepository")
    except Exception as e:
        errors.append(f"❌ Repository 继承关系检查失败: {e}")
        print(f"   ❌ 错误: {e}")
    
    # 7. 测试 main.py 导入
    print("\n[7] 测试 main.py 应用导入...")
    try:
        from main import app
        successes.append("✅ FastAPI 应用导入成功")
        print("   ✅ FastAPI app 对象")
    except Exception as e:
        errors.append(f"❌ main.py 导入失败: {e}")
        print(f"   ❌ 错误: {e}")
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"\n成功: {len(successes)}")
    for s in successes:
        print(f"  {s}")
    
    if errors:
        print(f"\n失败: {len(errors)}")
        for e in errors:
            print(f"  {e}")
        return False
    else:
        print("\n🎉 所有测试通过！CRUD 迁移成功！")
        return True


def test_repository_methods():
    """测试 Repository 方法是否存在"""
    print("\n" + "=" * 60)
    print("Repository 方法检查")
    print("=" * 60)
    
    from app.crud.user import UserRepository
    from app.crud.session import SessionRepository
    from app.crud.message import MessageRepository
    from app.crud.paper import PaperRepository
    
    # 检查 UserRepository 方法
    user_methods = ['get_by_username', 'get_by_id', 'create_user', 'update_last_login', 'update_password', 'exists_by_username']
    print("\nUserRepository 方法:")
    for method in user_methods:
        has = hasattr(UserRepository, method)
        print(f"  {'✅' if has else '❌'} {method}")
    
    # 检查 SessionRepository 方法
    session_methods = ['create_session', 'get_by_id_and_user', 'list_by_user', 'update_stats', 'parse_domains']
    print("\nSessionRepository 方法:")
    for method in session_methods:
        has = hasattr(SessionRepository, method)
        print(f"  {'✅' if has else '❌'} {method}")
    
    # 检查 MessageRepository 方法
    message_methods = ['create_message', 'get_by_session', 'get_recent', 'format_message', 'to_history_format']
    print("\nMessageRepository 方法:")
    for method in message_methods:
        has = hasattr(MessageRepository, method)
        print(f"  {'✅' if has else '❌'} {method}")
    
    # 检查 PaperRepository 方法
    paper_methods = ['get_by_id', 'get_by_ids', 'get_by_user', 'update_parsed_content', 'update_graph_status', 'update_status']
    print("\nPaperRepository 方法:")
    for method in paper_methods:
        has = hasattr(PaperRepository, method)
        print(f"  {'✅' if has else '❌'} {method}")


if __name__ == "__main__":
    success = test_imports()
    test_repository_methods()
    
    sys.exit(0 if success else 1)

