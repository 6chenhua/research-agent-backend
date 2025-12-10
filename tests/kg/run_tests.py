#!/usr/bin/env python
"""
知识图谱模块测试运行脚本

使用方法:
    python tests/kg/run_tests.py              # 运行所有测试
    python tests/kg/run_tests.py --verbose    # 详细输出
    python tests/kg/run_tests.py --coverage   # 生成覆盖率报告
    python tests/kg/run_tests.py --schemas    # 只运行Schema测试
"""
import sys
import subprocess
import argparse
import os
from pathlib import Path


def find_project_root() -> Path:
    """查找项目根目录（包含tests目录的目录）"""
    current = Path(__file__).resolve()
    
    # 从当前文件向上查找，直到找到包含tests目录的目录
    for parent in [current] + list(current.parents):
        if (parent / "tests").exists() and (parent / "app").exists():
            return parent
    
    # 如果找不到，返回当前工作目录
    return Path.cwd()


def run_command(cmd: list, cwd: Path) -> int:
    """运行命令并返回退出码"""
    print(f"工作目录: {cwd}")
    print(f"运行命令: {' '.join(cmd)}")
    print("-" * 80)
    result = subprocess.run(cmd, cwd=str(cwd))
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="运行知识图谱模块测试")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="生成测试覆盖率报告"
    )
    parser.add_argument(
        "--schemas",
        action="store_true",
        help="只运行Schema测试"
    )
    parser.add_argument(
        "--validators",
        action="store_true",
        help="只运行验证器测试"
    )
    parser.add_argument(
        "--namespace",
        action="store_true",
        help="只运行命名空间服务测试"
    )
    parser.add_argument(
        "--service",
        action="store_true",
        help="只运行图谱服务测试"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="只运行API测试"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="生成HTML格式的测试报告"
    )
    
    args = parser.parse_args()
    
    # 查找项目根目录
    project_root = find_project_root()
    print(f"📁 项目根目录: {project_root}")
    
    # 检查tests/kg目录是否存在
    test_dir = project_root / "tests" / "kg"
    if not test_dir.exists():
        print(f"❌ 错误: 找不到测试目录 {test_dir}")
        print(f"   当前工作目录: {Path.cwd()}")
        print(f"   脚本位置: {Path(__file__).resolve()}")
        return 1
    
    print(f"✓ 测试目录: {test_dir}")
    print()
    
    # 构建pytest命令
    cmd = ["pytest"]
    
    # 确定测试路径
    if args.schemas:
        cmd.append("tests/kg/test_schemas.py")
    elif args.validators:
        cmd.append("tests/kg/test_validators.py")
    elif args.namespace:
        cmd.append("tests/kg/test_namespace_service.py")
    elif args.service:
        cmd.append("tests/kg/test_graph_service.py")
    elif args.api:
        cmd.append("tests/kg/test_graph_api.py")
    else:
        # 运行所有测试
        cmd.append("tests/kg/")
    
    # 添加详细输出
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-v")  # 默认显示详细输出
    
    # 添加覆盖率选项
    if args.coverage:
        cmd.extend([
            "--cov=app.schemas.entities",
            "--cov=app.schemas.relations",
            "--cov=app.schemas.validators",
            "--cov=app.schemas.graph",
            "--cov=app.services.graph_service",
            "--cov=app.services.namespace_service",
            "--cov=app.api.routes.graph",
            "--cov-report=term",
            "--cov-report=html",
        ])
    
    # 添加HTML报告
    if args.html:
        cmd.append("--html=tests/kg/report.html")
        cmd.append("--self-contained-html")
    
    # 添加颜色输出
    cmd.append("--color=yes")
    
    # 运行测试
    exit_code = run_command(cmd, project_root)
    
    if exit_code == 0:
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        if args.coverage:
            print("📊 覆盖率报告已生成: htmlcov/index.html")
        if args.html:
            print("📄 测试报告已生成: tests/kg/report.html")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ 测试失败，请查看上面的错误信息")
        print("=" * 80)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

