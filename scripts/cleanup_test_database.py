"""
测试数据库清理脚本
用于清理测试数据库（通常测试框架会自动清理）
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def cleanup_test_database():
    """清理测试数据库"""
    # 连接到 MySQL 服务器
    server_url = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}"
    
    engine = create_async_engine(server_url, isolation_level="AUTOCOMMIT")
    
    try:
        async with engine.connect() as conn:
            # 删除测试数据库
            await conn.exec_driver_sql("DROP DATABASE IF EXISTS test_research_agent")
            print("✓ 已删除测试数据库: test_research_agent")
            
    except Exception as e:
        print(f"✗ 清理测试数据库时出错: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """主函数"""
    print("=" * 60)
    print("清理测试数据库")
    print("=" * 60)
    
    response = input("\n确定要删除测试数据库 'test_research_agent' 吗? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        await cleanup_test_database()
        print("\n测试数据库已清理完成")
    else:
        print("\n操作已取消")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

