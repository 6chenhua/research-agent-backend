"""
测试环境配置脚本
用于快速设置测试所需的数据库
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def create_test_database():
    """创建测试数据库"""
    # 连接到 MySQL 服务器（不指定数据库）
    server_url = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}"
    
    engine = create_async_engine(server_url, isolation_level="AUTOCOMMIT")
    
    try:
        async with engine.connect() as conn:
            # 删除旧的测试数据库（如果存在）
            await conn.exec_driver_sql("DROP DATABASE IF EXISTS test_research_agent")
            print("✓ 已删除旧的测试数据库（如果存在）")
            
            # 创建新的测试数据库
            await conn.exec_driver_sql(
                "CREATE DATABASE test_research_agent "
                "CHARACTER SET utf8mb4 "
                "COLLATE utf8mb4_unicode_ci"
            )
            print("✓ 已创建测试数据库: test_research_agent")
            
        print("\n测试数据库设置完成！")
        print("注意: 表结构将在运行测试时由 SQLAlchemy 自动创建")
        
    except Exception as e:
        print(f"✗ 创建测试数据库时出错: {e}")
        raise
    finally:
        await engine.dispose()


async def check_database_connection():
    """检查数据库连接"""
    try:
        server_url = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/test_research_agent"
        engine = create_async_engine(server_url)
        
        async with engine.connect() as conn:
            result = await conn.exec_driver_sql("SELECT DATABASE()")
            db_name = result.scalar()
            print(f"\n✓ 成功连接到测试数据库: {db_name}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"\n✗ 连接测试数据库失败: {e}")
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("设置测试环境")
    print("=" * 60)
    
    # 显示配置信息
    print(f"\nMySQL 配置:")
    print(f"  Host: {settings.MYSQL_HOST}")
    print(f"  Port: {settings.MYSQL_PORT}")
    print(f"  User: {settings.MYSQL_USER}")
    print(f"  生产数据库: {settings.MYSQL_DATABASE}")
    print(f"  测试数据库: test_research_agent")
    
    # 创建测试数据库
    print("\n" + "-" * 60)
    await create_test_database()
    
    # 检查连接
    print("\n" + "-" * 60)
    await check_database_connection()
    
    print("\n" + "=" * 60)
    print("测试环境设置完成！现在可以运行测试了")
    print("运行测试命令:")
    print("  pytest tests/test_auth.py -v")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

