"""
修复 bcrypt 版本兼容性问题
passlib 1.7.4 与 bcrypt 5.0+ 不兼容，需要降级到 bcrypt 4.0.1
"""
import subprocess
import sys


def run_command(cmd):
    """运行命令并显示输出"""
    print(f"\n执行: {cmd}")
    print("-" * 60)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0


def check_version(package):
    """检查包版本"""
    result = subprocess.run(
        f"{sys.executable} -m pip show {package}",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':')[1].strip()
    return None


def main():
    print("=" * 60)
    print("修复 bcrypt 版本兼容性")
    print("=" * 60)
    
    # 检查当前版本
    print("\n当前版本:")
    passlib_version = check_version('passlib')
    bcrypt_version = check_version('bcrypt')
    
    print(f"  passlib: {passlib_version}")
    print(f"  bcrypt:  {bcrypt_version}")
    
    if bcrypt_version and bcrypt_version.startswith('5.'):
        print("\n⚠️  检测到 bcrypt 5.x 版本，与 passlib 1.7.4 不兼容")
        print("    需要降级到 bcrypt 4.0.1")
        
        response = input("\n是否继续修复? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("操作已取消")
            return
        
        # 卸载 bcrypt
        print("\n步骤 1: 卸载当前 bcrypt")
        if not run_command(f"{sys.executable} -m pip uninstall bcrypt -y"):
            print("✗ 卸载失败")
            print("\n可能的原因:")
            print("  1. Python 进程正在使用 bcrypt（请关闭 PyCharm、测试等）")
            print("  2. 权限不足")
            print("\n请手动执行:")
            print(f"  {sys.executable} -m pip uninstall bcrypt -y")
            return
        
        # 安装兼容版本
        print("\n步骤 2: 安装 bcrypt 4.0.1")
        if not run_command(f"{sys.executable} -m pip install bcrypt==4.0.1"):
            print("✗ 安装失败")
            return
        
        # 验证
        print("\n步骤 3: 验证安装")
        new_version = check_version('bcrypt')
        print(f"  新版本: {new_version}")
        
        if new_version == "4.0.1":
            print("\n✓ 修复成功！")
            print("\n下一步:")
            print("  1. 运行测试: pytest tests/test_auth.py -v")
            print("  2. 启动服务器: python run.py")
        else:
            print(f"\n✗ 版本不正确: {new_version}")
    
    elif bcrypt_version and bcrypt_version.startswith('4.0'):
        print("\n✓ bcrypt 版本正确，无需修复")
    
    else:
        print(f"\n⚠️  未知的 bcrypt 版本: {bcrypt_version}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()

