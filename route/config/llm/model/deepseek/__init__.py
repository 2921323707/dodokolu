# -*- coding: utf-8 -*-
"""
DeepSeek 模型配置和处理
支持工具调用的 Agent 模式
"""
import json
import time
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

    # 如果提供了用户位置，在工具调用时自动使用
    user_location = location

    # 最大工具调用轮数，避免无限循环
    max_tool_calls = 5
    tool_call_count = 0
    pending_favorite_image = None  # 保存待发送的收藏图片信息（跨循环）
    pending_emoji = None  # 保存待发送的表情包信息（跨循环）
    accumulated_content = ""  # 累积已输出的内容，用于在工具调用后避免重复
    
    # 初始化消息列表（不包含系统提示词，系统提示词会在每次循环中动态更新）
    full_messages = list(messages)  # 复制历史消息
    
    while tool_call_count < max_tool_calls:
        # 每次循环都重新生成系统提示词，确保使用最新的时间信息
        system_prompt = get_system_prompt_with_time(NORMAL_SYSTEM_PROMPT_BASE.strip(), location)
        
        # 构建完整的消息列表（系统提示词 + 历史对话 + 工具调用结果等）
        # 注意：系统提示词需要放在消息列表的第一位，每次循环都更新以确保时间信息最新
        messages_with_system = [{"role": "system", "content": system_prompt}]
        messages_with_system.extend(full_messages)
        
        # 调用流式聊天接口
        stream = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages_with_system,
            tools=tools if tools else None,
            stream=True,
            temperature=TEMPERATURE
        )

        full_response = ""
        tool_calls = []
        current_tool_call = None
        content_before_tool_call = ""  # 工具调用前已输出的内容
        is_tool_call_detected = False  # 标记是否已检测到工具调用
        
        for chunk in stream:
            # 处理工具调用（先检查工具调用，因为工具调用可能在内容之前）
            if chunk.choices[0].delta.tool_calls:
                is_tool_call_detected = True
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
            
            # 处理内容流
            chunk_content = chunk.choices[0].delta.content or ""
            if chunk_content:
                full_response += chunk_content
                # 如果还没有检测到工具调用，立即输出内容
                if not is_tool_call_detected:
                    content_before_tool_call += chunk_content
                    yield f"data: {json.dumps({'content': chunk_content, 'done': False}, ensure_ascii=False)}\n\n"
                # 如果已经检测到工具调用，说明这是工具调用后的新内容，直接输出
                else:
                    yield f"data: {json.dumps({'content': chunk_content, 'done': False}, ensure_ascii=False)}\n\n"
        
        # 如果有工具调用，执行工具
        if tool_calls and any(tc.get("function", {}).get("name") for tc in tool_calls):
            tool_call_count += 1
            # 累积工具调用前已输出的内容
            accumulated_content += content_before_tool_call
            
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
                
                # 如果是send_emoji工具且没有提供assistant_message，使用当前AI的回复内容
                if tool_name == "send_emoji":
                    # 优先使用assistant_message（AI的回复内容）
                    if not arguments.get("assistant_message"):
                        # 使用当前AI生成的回复内容（full_response）
                        if full_response:
                            arguments["assistant_message"] = full_response
                        else:
                            # 如果当前回复为空，从消息历史中查找最后一条assistant消息
                            for msg in reversed(full_messages):
                                if msg.get("role") == "assistant" and msg.get("content"):
                                    arguments["assistant_message"] = msg.get("content", "")
                                    break
                    
                    # 向后兼容：如果没有assistant_message，尝试使用user_message
                    if not arguments.get("assistant_message") and not arguments.get("user_message"):
                        # 从消息历史中查找最后一条用户消息
                        for msg in reversed(full_messages):
                            if msg.get("role") == "user":
                                arguments["user_message"] = msg.get("content", "")
                                break
                
                # 执行工具
                tool_result = execute_tool(tool_name, arguments)
                
                # 特殊处理 send_emoji 工具：保存表情包信息，等待流式输出完成后发送
                if tool_name == "send_emoji" and isinstance(tool_result, dict) and tool_result.get("sent"):
                    print(f"📤 [后端] 检测到表情包工具调用，将延迟到流式输出完成后发送")
                    # 保存表情包信息到全局变量，稍后发送
                    pending_emoji = {
                        "type": "emoji",
                        "emoji_id": tool_result.get("emoji_id"),
                        "emoji_url": tool_result.get("emoji_url"),
                        "category": tool_result.get("category"),
                        "description": tool_result.get("description")
                    }
                
                # 特殊处理 send_favorite_image 工具：保存图片信息，等待流式输出完成后发送
                if tool_name == "send_favorite_image" and isinstance(tool_result, dict) and tool_result.get("sent"):
                    print(f"📤 [后端] 检测到收藏图片工具调用，将延迟到流式输出完成后发送")
                    # 保存图片信息到全局变量，稍后发送
                    pending_favorite_image = {
                        "type": "favorite_image",
                        "image_filename": tool_result.get("image_filename"),
                        "image_url": tool_result.get("image_url"),
                        "description": tool_result.get("description")
                    }
                
                tool_results.append({
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # 将工具结果添加到消息历史
            full_messages.extend(tool_results)
            
            # 继续下一轮对话（工具调用后需要模型再次响应）
            # 如果有待发送的收藏图片，会在流式输出完成后发送
            continue
        else:
            # 没有工具调用，正常返回响应
            # 合并所有累积的内容（包括工具调用前的内容和当前响应）
            final_response = accumulated_content + full_response
            if final_response:
                save_message(session_id, "assistant", final_response)
            # 重置累积内容（准备下一轮对话）
            accumulated_content = ""
            
            # 发送完成标记
            yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
            
            # 如果有待发送的表情包，在流式输出完成后发送
            if pending_emoji:
                print(f"📤 [后端] 流式输出完成，准备发送表情包事件到前端")
                print(f"📤 [后端] 表情包事件数据: {json.dumps(pending_emoji, ensure_ascii=False)}")
                yield f"data: {json.dumps(pending_emoji, ensure_ascii=False)}\n\n"
            
            # 如果有待发送的收藏图片，在流式输出完成后停顿1秒再发送
            if pending_favorite_image:
                print(f"⏳ [后端] 流式输出完成，等待1秒后发送收藏图片...")
                time.sleep(1)  # 停顿1秒
                print(f"📤 [后端] 准备发送收藏图片事件到前端")
                print(f"📤 [后端] 收藏图片事件数据: {json.dumps(pending_favorite_image, ensure_ascii=False)}")
                yield f"data: {json.dumps(pending_favorite_image, ensure_ascii=False)}\n\n"
            
            break
    
    # 如果达到最大工具调用次数，返回最终响应
    if tool_call_count >= max_tool_calls:
        # 合并所有累积的内容
        final_response = accumulated_content + full_response
        if final_response:
            save_message(session_id, "assistant", final_response)
        
        # 发送完成标记
        yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
        
        # 如果有待发送的表情包，在流式输出完成后发送
        if pending_emoji:
            print(f"📤 [后端] 流式输出完成，准备发送表情包事件到前端")
            print(f"📤 [后端] 表情包事件数据: {json.dumps(pending_emoji, ensure_ascii=False)}")
            yield f"data: {json.dumps(pending_emoji, ensure_ascii=False)}\n\n"
        
        # 如果有待发送的收藏图片，在流式输出完成后停顿1秒再发送
        if pending_favorite_image:
            print(f"⏳ [后端] 流式输出完成，等待1秒后发送收藏图片...")
            time.sleep(1)  # 停顿1秒
            print(f"📤 [后端] 准备发送收藏图片事件到前端")
            print(f"📤 [后端] 收藏图片事件数据: {json.dumps(pending_favorite_image, ensure_ascii=False)}")
            yield f"data: {json.dumps(pending_favorite_image, ensure_ascii=False)}\n\n"


__all__ = [
    'create_client',
    'stream_completion'
]
