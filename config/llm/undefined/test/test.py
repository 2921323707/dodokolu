# -*- coding: utf-8 -*-
"""
Undefined 智能体测试文件
测试 Minimax M2.1 API 调用
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 确保环境变量已设置（如果 .env 文件存在）
from dotenv import load_dotenv
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from config.llm.base import get_agent


def test_undefined_agent():
    """测试 Undefined 智能体的基本功能"""
    print("=" * 60)
    print("测试 Undefined 智能体")
    print("=" * 60)
    
    # 获取 Undefined 智能体
    try:
        agent = get_agent('undefined')
        print(f"✅ 成功获取智能体: {agent.name}")
        print(f"   描述: {agent.description}")
    except Exception as e:
        print(f"❌ 获取智能体失败: {e}")
        return
    
    # 测试消息列表
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
    
    session_id = "test_session_001"
    email = None  # 测试时可以不提供邮箱
    
    print("\n" + "-" * 60)
    print("用户消息:")
    print(f"  {messages[0]['content']}")
    print("-" * 60)
    print("\n智能体回复:")
    print("-" * 60)
    
    # 调用流式响应
    try:
        response_text = ""
        for chunk in agent.stream_response(messages, session_id, location=None, email=email):
            # 解析 SSE 格式的数据
            if chunk.startswith("data: "):
                data_str = chunk[6:].strip()  # 移除 "data: " 前缀
                if data_str:
                    import json
                    try:
                        data = json.loads(data_str)
                        if 'content' in data:
                            content = data['content']
                            if content:
                                print(content, end='', flush=True)
                                response_text += content
                        if data.get('done', False):
                            print("\n" + "-" * 60)
                            print("✅ 响应完成")
                            break
                    except json.JSONDecodeError:
                        pass
        
        print(f"\n\n完整回复内容:\n{response_text}")
        
    except Exception as e:
        print(f"\n❌ 调用失败: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_questions():
    """测试多个问题"""
    print("\n\n" + "=" * 60)
    print("测试多个问题")
    print("=" * 60)
    
    try:
        agent = get_agent('undefined')
    except Exception as e:
        print(f"❌ 获取智能体失败: {e}")
        return
    
    # 测试问题列表
    questions = [
        "今天北京的天气怎么样？",
        "请搜索一下最新的 AI 新闻",
        "现在几点了？"
    ]
    
    session_id = "test_session_002"
    messages = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'=' * 60}")
        print(f"问题 {i}: {question}")
        print("=" * 60)
        
        # 添加用户消息
        messages.append({"role": "user", "content": question})
        
        # 获取回复
        response_text = ""
        for chunk in agent.stream_response(messages, session_id, location=None, email=None):
            if chunk.startswith("data: "):
                data_str = chunk[6:].strip()
                if data_str:
                    import json
                    try:
                        data = json.loads(data_str)
                        if 'content' in data:
                            content = data['content']
                            if content:
                                print(content, end='', flush=True)
                                response_text += content
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        pass
        
        # 添加助手回复到消息历史（用于多轮对话）
        if response_text:
            messages.append({"role": "assistant", "content": response_text})
        
        print("\n")


def test_direct_api_call():
    """直接测试 Minimax API 调用（参考 reference.py）"""
    print("\n\n" + "=" * 60)
    print("直接测试 Minimax API 调用")
    print("=" * 60)
    
    import anthropic
    from config.llm.base.settings import MINIMAX_API_KEY, MINIMAX_BASE_URL, MINIMAX_MODEL
    
    # 检查配置
    if not MINIMAX_API_KEY:
        print("❌ MINIMAX_API_KEY 未配置，请在 .env 文件中设置")
        return
    
    print(f"✅ API Key: {MINIMAX_API_KEY[:20]}...")
    print(f"✅ Base URL: {MINIMAX_BASE_URL}")
    print(f"✅ Model: {MINIMAX_MODEL}")
    
    # 设置环境变量
    os.environ["ANTHROPIC_BASE_URL"] = MINIMAX_BASE_URL
    os.environ["ANTHROPIC_API_KEY"] = MINIMAX_API_KEY
    
    # 初始化客户端
    client = anthropic.Anthropic()
    
    # 测试消息
    messages = [
        {"role": "user", "content": "你好，请用一句话介绍你自己"}
    ]
    
    print(f"\n👤 用户: {messages[0]['content']}")
    print("\n🤖 助手回复:")
    print("-" * 60)
    
    try:
        # 调用 API（不使用工具，因为 Minimax M2.1 自带能力）
        response = client.messages.create(
            model=MINIMAX_MODEL,
            max_tokens=4096,
            messages=messages,
        )
        
        # 处理响应
        for block in response.content:
            if block.type == "thinking":
                print(f"💭 Thinking: {block.thinking[:100]}...")
            elif block.type == "text":
                print(block.text)
        
        print("-" * 60)
        print("✅ API 调用成功")
        
    except Exception as e:
        print(f"❌ API 调用失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Undefined 智能体测试套件")
    print("=" * 60)
    print("\n请确保已在 .env 文件中配置以下环境变量:")
    print("  MINIMAX_API_KEY=your_api_key")
    print("  MINIMAX_BASE_URL=https://api.minimaxi.com/anthropic")
    print("  MINIMAX_MODEL=MiniMax-M2.1")
    print("\n")
    
    # 运行测试
    try:
        # 测试 1: 基本功能测试
        test_undefined_agent()
        
        # 测试 2: 多个问题测试（可选，取消注释以运行）
        # test_multiple_questions()
        
        # 测试 3: 直接 API 调用测试（可选，取消注释以运行）
        # test_direct_api_call()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

