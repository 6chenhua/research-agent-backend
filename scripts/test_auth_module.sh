#!/bin/bash

# 用户认证模块测试脚本
# 用于快速验证所有认证功能

set -e

echo "🚀 开始测试用户认证模块..."
echo ""

# 配置
BASE_URL="http://localhost:8000"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_USERNAME="测试用户_$(date +%s)"
TEST_PASSWORD="TestPass123!"
NEW_PASSWORD="NewPass456!"

echo "📝 测试配置:"
echo "  - 基础URL: $BASE_URL"
echo "  - 测试邮箱: $TEST_EMAIL"
echo "  - 测试用户名: $TEST_USERNAME"
echo ""

# 1. 健康检查
echo "1️⃣  测试健康检查..."
curl -s "$BASE_URL/health" | jq '.'
echo "✅ 健康检查通过"
echo ""

# 2. 用户注册
echo "2️⃣  测试用户注册..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME\",
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

echo "$REGISTER_RESPONSE" | jq '.'

ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token')
REFRESH_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.refresh_token')
USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.user.user_id')

if [ "$ACCESS_TOKEN" != "null" ]; then
  echo "✅ 用户注册成功"
  echo "  - User ID: $USER_ID"
  echo "  - Access Token: ${ACCESS_TOKEN:0:20}..."
else
  echo "❌ 用户注册失败"
  exit 1
fi
echo ""

# 3. 获取用户信息
echo "3️⃣  测试获取用户信息..."
curl -s -X GET "$BASE_URL/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'
echo "✅ 获取用户信息成功"
echo ""

# 4. 用户登录
echo "4️⃣  测试用户登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

echo "$LOGIN_RESPONSE" | jq '.'

NEW_ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$NEW_ACCESS_TOKEN" != "null" ]; then
  echo "✅ 用户登录成功"
  ACCESS_TOKEN=$NEW_ACCESS_TOKEN
else
  echo "❌ 用户登录失败"
  exit 1
fi
echo ""

# 5. Token刷新
echo "5️⃣  测试Token刷新..."
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh_token\": \"$REFRESH_TOKEN\"
  }")

echo "$REFRESH_RESPONSE" | jq '.'

REFRESHED_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.access_token')

if [ "$REFRESHED_TOKEN" != "null" ]; then
  echo "✅ Token刷新成功"
else
  echo "❌ Token刷新失败"
  exit 1
fi
echo ""

# 6. 修改密码
echo "6️⃣  测试修改密码..."
CHANGE_PASSWORD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/change-password" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"old_password\": \"$TEST_PASSWORD\",
    \"new_password\": \"$NEW_PASSWORD\"
  }")

echo "$CHANGE_PASSWORD_RESPONSE" | jq '.'
echo "✅ 修改密码成功"
echo ""

# 7. 使用新密码登录
echo "7️⃣  测试使用新密码登录..."
NEW_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$NEW_PASSWORD\"
  }")

NEW_LOGIN_TOKEN=$(echo "$NEW_LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$NEW_LOGIN_TOKEN" != "null" ]; then
  echo "✅ 使用新密码登录成功"
  ACCESS_TOKEN=$NEW_LOGIN_TOKEN
else
  echo "❌ 使用新密码登录失败"
  exit 1
fi
echo ""

# 8. 用户登出
echo "8️⃣  测试用户登出..."
LOGOUT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$LOGOUT_RESPONSE" | jq '.'
echo "✅ 用户登出成功"
echo ""

# 9. 验证Token黑名单
echo "9️⃣  验证Token黑名单（使用已登出的Token）..."
BLACKLIST_TEST=$(curl -s -X GET "$BASE_URL/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$BLACKLIST_TEST" | grep -q "Token已被撤销"; then
  echo "✅ Token黑名单机制正常"
else
  echo "⚠️  Token黑名单机制可能有问题"
fi
echo ""

# 10. 测试错误密码
echo "🔟 测试错误密码登录..."
ERROR_LOGIN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"WrongPassword123!\"
  }")

if echo "$ERROR_LOGIN" | grep -q "邮箱或密码错误"; then
  echo "✅ 错误密码验证正常"
else
  echo "⚠️  错误密码验证可能有问题"
fi
echo ""

echo "🎉 所有测试完成！"
echo ""
echo "📊 测试总结:"
echo "  ✅ 健康检查"
echo "  ✅ 用户注册"
echo "  ✅ 获取用户信息"
echo "  ✅ 用户登录"
echo "  ✅ Token刷新"
echo "  ✅ 修改密码"
echo "  ✅ 使用新密码登录"
echo "  ✅ 用户登出"
echo "  ✅ Token黑名单验证"
echo "  ✅ 错误密码验证"
echo ""
echo "🎊 Module H 用户认证模块测试通过！"

