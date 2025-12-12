from anthropic import Anthropic

# 初始化客户端
client = Anthropic(api_key="your_api_key_here")

# 创建消息,使用 Skills 功能
response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [
            # Anthropic 官方提供的 PDF 技能
            {"type": "anthropic", "skill_id": "pdf", "version": "latest"},
            # Anthropic 官方提供的 Excel 技能
            {"type": "anthropic", "skill_id": "xlsx", "version": "latest"},
            # 自定义技能
            {"type": "custom", "skill_id": "skill_01AbCdEf...", "version": "1.0.0"}
        ]
    },
    messages=[
        {
            "role": "user",
            "content": "从这份PDF中提取数据,并创建一份Excel报告。"
        }
    ],
    tools=[
        {"type": "code_execution_20250825", "name": "code_execution"}
    ]
)

# 处理响应
print("Claude 的回复:")
for block in response.content:
    if block.type == "text":
        print(block.text)
    elif block.type == "tool_use":
        print(f"\n使用工具: {block.name}")
        print(f"工具输入: {block.input}")

# 如果需要继续对话(处理工具结果)
if response.stop_reason == "tool_use":
    # 这里需要执行工具并返回结果
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            # 执行代码或处理工具调用
            # result = execute_tool(block)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": "工具执行结果"
            })

    # 继续对话
    follow_up = client.beta.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        betas=["code-execution-2025-08-25", "skills-2025-10-02"],
        container={
            "skills": [
                {"type": "anthropic", "skill_id": "pdf", "version": "latest"},
                {"type": "anthropic", "skill_id": "xlsx", "version": "latest"},
            ]
        },
        messages=[
            {"role": "user", "content": "从这份PDF中提取数据,并创建一份Excel报告。"},
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results}
        ],
        tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
    )