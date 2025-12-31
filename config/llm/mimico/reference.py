import os
import anthropic

# ===================== 关键配置（必须替换！）=====================
# 1. 设置Minimax的API基础地址（兼容Anthropic SDK）
os.environ["ANTHROPIC_BASE_URL"] = "https://api.minimaxi.com/anthropic"
# 2. 替换为你自己的Minimax API密钥（从Minimax控制台获取）
os.environ["ANTHROPIC_API_KEY"] = "sk-cp-4XiY6Wu1VyIGD-fqbwTSWTbASbN_yHGoAQ5e1356RsI8WDyDsYzHjYB5U4HcpPvlEUjtkQz_E8HvQ5wXwJfBIF-bu4T4WqSojlKRkU7AP7uF80tsxavQaR4"

# ===================== 初始化客户端并调用 =====================
import anthropic
import json

# 初始化客户端
client = anthropic.Anthropic()

# 定义工具：天气查询
tools = [
    {
        "name": "get_weather",
        "description": "Get weather of a location, the user should supply a location first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, US",
                }
            },
            "required": ["location"]
        }
    }
]

def send_messages(messages):
    params = {
        "model": "MiniMax-M2.1",
        "max_tokens": 4096,
        "messages": messages,
        "tools": tools,
    }

    response = client.messages.create(**params)
    return response

def process_response(response):
    thinking_blocks = []
    text_blocks = []
    tool_use_blocks = []

    # 遍历所有内容块
    for block in response.content:
        if block.type == "thinking":
            thinking_blocks.append(block)
            print(f"💭 Thinking>\n{block.thinking}\n")
        elif block.type == "text":
            text_blocks.append(block)
            print(f"💬 Model>\t{block.text}")
        elif block.type == "tool_use":
            tool_use_blocks.append(block)
            print(f"🔧 Tool>\t{block.name}({json.dumps(block.input, ensure_ascii=False)})")

    return thinking_blocks, text_blocks, tool_use_blocks

# 1. 用户提问
messages = [{"role": "user", "content": "How's the weather in San Francisco?"}]
print(f"\n👤 User>\t {messages[0]['content']}")

# 2. 模型返回第一轮响应（可能包含工具调用）
response = send_messages(messages)
thinking_blocks, text_blocks, tool_use_blocks = process_response(response)

# 3. 如果有工具调用，执行工具并继续对话
if tool_use_blocks:
    # ⚠️ 关键：将助手的完整响应回传到消息历史
    # response.content 包含所有块的列表：[thinking块, text块, tool_use块]
    # 必须完整回传，否则后续对话会丢失上下文信息
    messages.append({
        "role": "assistant",
        "content": response.content
    })

    # 执行工具并返回结果（这里模拟天气API调用）
    print(f"\n🔨 执行工具: {tool_use_blocks[0].name}")
    tool_result = "24℃, sunny"
    print(f"📊 工具返回: {tool_result}")

    # 添加工具执行结果
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_blocks[0].id,
                "content": tool_result
            }
        ]
    })

    # 4. 获取最终回复
    final_response = send_messages(messages)
    process_response(final_response)