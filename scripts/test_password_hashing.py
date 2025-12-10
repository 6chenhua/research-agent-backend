"""
密码哈希测试脚本
用于诊断 bcrypt 72字节限制问题
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.security import hash_password, verify_password


def test_password_lengths():
    """测试不同长度的密码"""
    print("=" * 60)
    print("密码哈希测试")
    print("=" * 60)
    
    test_cases = [
        ("TestPass123!", "正常密码"),
        ("a" * 50, "50字符"),
        ("a" * 72, "72字符"),
        ("a" * 100, "100字符（将被截断）"),
        ("中文密码Test123!", "包含中文的密码"),
    ]
    
    for password, description in test_cases:
        print(f"\n测试: {description}")
        print(f"  密码: {password[:20]}..." if len(password) > 20 else f"  密码: {password}")
        print(f"  字符长度: {len(password)}")
        print(f"  字节长度: {len(password.encode('utf-8'))}")
        
        try:
            hashed = hash_password(password)
            print(f"  ✓ 加密成功")
            print(f"  哈希: {hashed[:30]}...")
            print(f"  哈希长度: {len(hashed)}")
            
            # 验证密码
            is_valid = verify_password(password, hashed)
            print(f"  ✓ 验证结果: {is_valid}")
            
        except Exception as e:
            print(f"  ✗ 错误: {e}")


def test_hash_rehash():
    """测试重复加密问题"""
    print("\n" + "=" * 60)
    print("重复加密测试")
    print("=" * 60)
    
    password = "TestPass123!"
    print(f"\n原始密码: {password}")
    
    # 第一次加密
    hashed1 = hash_password(password)
    print(f"\n第一次加密:")
    print(f"  哈希: {hashed1}")
    print(f"  长度: {len(hashed1)} 字符, {len(hashed1.encode('utf-8'))} 字节")
    
    # 尝试将哈希再次加密（这会导致错误）
    print(f"\n尝试将哈希值再次加密（模拟错误场景）:")
    try:
        hashed2 = hash_password(hashed1)
        print(f"  ✓ 居然成功了（已截断）: {hashed2[:50]}...")
    except Exception as e:
        print(f"  ✗ 失败（预期）: {e}")


def test_common_passwords():
    """测试常见的测试密码"""
    print("\n" + "=" * 60)
    print("常见测试密码")
    print("=" * 60)
    
    passwords = [
        "TestPass123!",
        "LoginPass123!",
        "RefreshPass123!",
        "LogoutPass123!",
        "MePass123!",
        "ChangePass123!",
        "OldPass123!",
        "NewPass456!",
        "CorrectPass123!",
        "WrongPass123!",
        "SomePass123!",
        "SecurePass123!",
        "WeakPass",
    ]
    
    for password in passwords:
        try:
            hashed = hash_password(password)
            is_valid = verify_password(password, hashed)
            status = "✓" if is_valid else "✗"
            print(f"{status} {password:20} -> {hashed[:40]}...")
        except Exception as e:
            print(f"✗ {password:20} -> 错误: {e}")


if __name__ == "__main__":
    test_password_lengths()
    test_hash_rehash()
    test_common_passwords()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

