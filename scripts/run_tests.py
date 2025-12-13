#!/usr/bin/env python
"""
测试运行脚本
提供方便的测试执行命令

使用方法:
    python scripts/run_tests.py              # 运行所有测试
    python scripts/run_tests.py auth         # 只运行认证模块测试
    python scripts/run_tests.py research     # 只运行研究会话测试
    python scripts/run_tests.py chat         # 只运行聊天模块测试
    python scripts/run_tests.py crud         # 只运行CRUD层测试
    python scripts/run_tests.py integration  # 只运行集成测试
    python scripts/run_tests.py --coverage   # 运行测试并生成覆盖率报告
"""
import sys
# 导入 pytest 库，而不是使用 subprocess
import pytest
import argparse


# from subprocess import run # 不再需要 subprocess


def run_tests(test_type: str = None, coverage: bool = False, verbose: bool = True):
    """运行测试"""

    # 构建 pytest 命令行参数列表（而不是系统命令）
    args = []

    # 添加详细输出
    if verbose:
        args.append("-v")

    # 添加覆盖率
    if coverage:
        # 注意: --cov-report=term-missing 应该在 args 中
        args.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])

    # 根据测试类型选择测试文件
    test_files = {
        "auth": "tests/test_auth.py",
        "research": "tests/test_research.py",
        "chat": "tests/test_chat.py",
        "crud": "tests/test_crud_repository.py",
        "integration": "tests/test_integration.py",
        "graph": "tests/test_graph.py",
        "user": "tests/test_user.py",
    }

    if test_type:
        if test_type in test_files:
            args.append(test_files[test_type])
        else:
            print(f"未知的测试类型: {test_type}")
            print(f"可用的测试类型: {', '.join(test_files.keys())}")
            return 1  # 直接返回退出码
    else:
        args.append("tests/")

    # 添加异步标记
    args.extend(["-m", "asyncio"])

    # 打印将要执行的 pytest 参数
    # 我们不再打印 'python -m pytest'，只打印参数
    print(f"运行 pytest 参数: {args}")
    print("-" * 60)

    # **核心修改：使用 pytest.main() API 直接运行测试**
    # pytest.main() 返回一个退出码，0 表示成功
    return_code = pytest.main(args)

    return return_code


def main():
    parser = argparse.ArgumentParser(description="运行测试")
    parser.add_argument(
        "test_type",
        nargs="?",
        help="测试类型: auth, research, chat, crud, integration, graph, user"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="生成覆盖率报告"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="简洁输出"
    )

    args = parser.parse_args()

    return_code = run_tests(
        test_type=args.test_type,
        coverage=args.coverage,
        verbose=not args.quiet
    )

    # 使用 return_code 作为程序的退出码
    sys.exit(return_code)


if __name__ == "__main__":
    main()