# -*- coding: utf-8 -*-
"""
DeepSeek 模型配置和处理
支持工具调用的 Agent 模式
"""
import json
from openai import OpenAI
from route.config.llm.setting import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TEMPERATURE
)
from route.config.llm.prompt import get_system_prompt_with_time, NORMAL_SYSTEM_PROMPT_BASE
from route.config.llm.history import save_message
from tools import TOOLS, execute_tool


def create_client():
    """
    创建 DeepSeek API 客户端
    
    Returns:
        OpenAI 客户端实例
    
    Raises:
        ValueError: 如果 API Key 未配置
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置")
    
    return OpenAI(
        base_url=DEEPSEEK_BASE_URL,
        api_key=DEEPSEEK_API_KEY,
    )


def stream_completion(messages, session_id, location=None):
    """
    使用 DeepSeek API 实现流式输出（支持工具调用）
    
    Args:
        messages: 消息列表
        session_id: 会话ID
        location: 用户位置信息（可选），用于自动获取用户当前位置的天气
    
    Yields:
        str: SSE格式的流式响应数据
    """
    client = create_client()

    # 构建工具定义（OpenAI格式）
    tools = []
    for tool_name, tool_info in TOOLS.items():
        tools.append({
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": tool_info.get("parameters", {})
            }
        })

    # 构建完整的消息列表（系统提示词 + 历史对话 + 当前消息）
    system_prompt = get_system_prompt_with_time(NORMAL_SYSTEM_PROMPT_BASE.strip(), location)
    full_messages = [{"role": "system", "content": system_prompt}]
    full_messages.extend(messages)
    
    # 如果提供了用户位置，在工具调用时自动使用
    user_location = location

    # 最大工具调用轮数，避免无限循环
    max_tool_calls = 5
    tool_call_count = 0
    
    while tool_call_count < max_tool_calls:
        # 调用流式聊天接口
        stream = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=full_messages,
            tools=tools if tools else None,
            stream=True,
            temperature=TEMPERATURE
        )

        full_response = ""
        tool_calls = []
        current_tool_call = None
        
        for chunk in stream:
            # 处理内容流
            chunk_content = chunk.choices[0].delta.content or ""
            if chunk_content:
                full_response += chunk_content
                yield f"data: {json.dumps({'content': chunk_content, 'done': False}, ensure_ascii=False)}\n\n"
            
            # 处理工具调用
            if chunk.choices[0].delta.tool_calls:
                for tool_call_delta in chunk.choices[0].delta.tool_calls:
                    if tool_call_delta.index is not None:
                        # 确保有足够的工具调用对象
                        while len(tool_calls) <= tool_call_delta.index:
                            tool_calls.append({
                                "id": "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""}
                            })
                        
                        current_tool_call = tool_calls[tool_call_delta.index]
                        if tool_call_delta.id:
                            current_tool_call["id"] = tool_call_delta.id
                        if tool_call_delta.function.name:
                            current_tool_call["function"]["name"] = tool_call_delta.function.name
                        if tool_call_delta.function.arguments:
                            current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments
        
        # 如果有工具调用，执行工具
        if tool_calls and any(tc.get("function", {}).get("name") for tc in tool_calls):
            tool_call_count += 1
            # 将工具调用添加到消息历史
            full_messages.append({
                "role": "assistant",
                "content": full_response if full_response else None,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": tc["type"],
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    }
                    for tc in tool_calls if tc.get("function", {}).get("name")
                ]
            })
            
            # 执行工具调用
            tool_results = []
            for tool_call in tool_calls:
                if not tool_call.get("function", {}).get("name"):
                    continue
                    
                tool_name = tool_call["function"]["name"]
                try:
                    arguments_str = tool_call["function"]["arguments"]
                    arguments = json.loads(arguments_str) if arguments_str else {}
                except json.JSONDecodeError:
                    arguments = {}
                
                # 如果是get_weather工具且没有提供位置参数，使用用户位置
                if tool_name == "get_weather" and user_location:
                    if not arguments.get("location") and not (arguments.get("latitude") and arguments.get("longitude")):
                        arguments["latitude"] = user_location.get("latitude")
                        arguments["longitude"] = user_location.get("longitude")
                
                # 执行工具
                tool_result = execute_tool(tool_name, arguments)
                tool_results.append({
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # 将工具结果添加到消息历史
            full_messages.extend(tool_results)
            
            # 继续下一轮对话（工具调用后需要模型再次响应）
            continue
        else:
            # 没有工具调用，正常返回响应
            if full_response:
                save_message(session_id, "assistant", full_response)
            yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
            break
    
    # 如果达到最大工具调用次数，返回最终响应
    if tool_call_count >= max_tool_calls:
        if full_response:
            save_message(session_id, "assistant", full_response)
        yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"


__all__ = [
    'create_client',
    'stream_completion'
]
