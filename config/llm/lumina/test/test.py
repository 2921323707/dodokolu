# -*- coding: utf-8 -*-
"""
Lumina Agent 简单测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from config.llm.lumina.agent import LuminaAgent


def test_lumina_agent_init():
    """测试 LuminaAgent 初始化"""
    agent = LuminaAgent()
    assert agent.name == "Lumina"
    assert "Gemini" in agent.description
    print("[PASS] LuminaAgent 初始化测试通过")


def test_get_system_prompt():
    """测试获取系统提示词"""
    agent = LuminaAgent()
    prompt = agent.get_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    print("[PASS] 获取系统提示词测试通过")


def test_get_tools():
    """测试获取工具列表"""
    agent = LuminaAgent()
    tools = agent.get_tools()
    assert isinstance(tools, list)
    print(f"[PASS] 获取工具列表测试通过，共 {len(tools)} 个工具")


def test_stream_response():
    """测试流式响应"""
    import json
    import sys
    
    # 设置输出编码为 UTF-8
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    agent = LuminaAgent()
    messages = [
        {"role": "user", "content": "你好"}
    ]
    session_id = "test_session_001"
    
    print("\n开始测试流式响应...")
    print("用户消息: 你好")
    print("AI回复: ", end="", flush=True)
    
    try:
        response_text = ""
        for chunk in agent.stream_response(messages, session_id):
            # 解析 SSE 格式的数据
            if chunk.startswith("data: "):
                data_str = chunk[6:].strip()
                if data_str:
                    try:
                        data = json.loads(data_str)
                        if "content" in data:
                            content = data["content"]
                            if content:
                                try:
                                    print(content, end="", flush=True)
                                    response_text += content
                                except UnicodeEncodeError:
                                    # 如果编码失败，使用 ASCII 安全的方式
                                    safe_content = content.encode('ascii', 'ignore').decode('ascii')
                                    print(safe_content, end="", flush=True)
                                    response_text += content
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        pass
        
        print("\n")
        if len(response_text) > 0:
            print(f"[PASS] 流式响应测试通过，响应长度: {len(response_text)} 字符")
            return True
        else:
            print("[FAIL] 流式响应测试失败: 响应内容为空")
            return False
    except Exception as e:
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"\n[FAIL] 流式响应测试失败: {error_msg}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始测试 Lumina Agent...")
    test_lumina_agent_init()
    test_get_system_prompt()
    test_get_tools()
    print("\n" + "="*50)
    test_stream_response()
    print("\n所有测试完成！")

