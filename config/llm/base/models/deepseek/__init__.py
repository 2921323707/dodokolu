# -*- coding: utf-8 -*-
"""
DeepSeek 模型配置和处理
支持工具调用的 Agent 模式
"""
import json
import time
from openai import OpenAI
from config.llm.base.settings import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TEMPERATURE
)
from config.llm.base.history import save_message
from config.llm.base.prompts.utils import get_system_prompt_with_time
from tools import TOOLS, execute_tool
from tools.send_pics.send_pics import auto_match_emoji


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


def stream_completion(messages, session_id, location=None, email=None):
    """
    使用 DeepSeek API 实现流式输出（支持工具调用）
    
    Args:
        messages: 消息列表
        session_id: 会话ID
        location: 用户位置信息（可选），用于自动获取用户当前位置的天气
        email: 用户邮箱（用于历史记录存储）
    
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
    # pending_emoji 已移除，表情包现在通过 auto_match_emoji 自动匹配
    accumulated_content = ""  # 累积已输出的内容，用于在工具调用后避免重复
    
    # 初始化消息列表（不包含系统提示词，系统提示词会在每次循环中动态更新）
    full_messages = list(messages)  # 复制历史消息
    
    while tool_call_count < max_tool_calls:
        # 注意：此文件为旧实现，建议使用 Agent 框架（config.llm.dodokolu.agent.SuheyaoAgent）
        # 此函数保留用于向后兼容，但需要从外部传入 base_prompt
        # 这里使用空提示词作为临时修复（实际使用时应通过 Agent 框架）
        system_prompt = get_system_prompt_with_time("", location)
        
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
        is_send_emoji_detected = False  # 标记是否检测到send_emoji工具调用
        
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
                            # 如果检测到send_emoji工具调用，标记并立即结束
                            if tool_call_delta.function.name == "send_emoji":
                                is_send_emoji_detected = True
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
                # 如果已经检测到工具调用，但不包括send_emoji，继续输出内容
                elif not is_send_emoji_detected:
                    yield f"data: {json.dumps({'content': chunk_content, 'done': False}, ensure_ascii=False)}\n\n"
        
        # 如果检测到send_emoji工具调用，立即结束并使用已输出内容进行表情包匹配
        if is_send_emoji_detected:
            # 保存已输出的内容（工具调用前的内容）
            final_response = accumulated_content + content_before_tool_call
            if final_response:
                save_message(email, "assistant", final_response, session_id)
            accumulated_content = ""
            
            # 发送完成标记
            yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
            
            # 自动匹配表情包（使用已输出的内容）
            if final_response:
                print(f"🎭 [后端] 检测到send_emoji工具调用，AI回复完成，开始自动匹配表情包...")
                emoji_result = auto_match_emoji(final_response, probability=0.9)
                if emoji_result:
                    print(f"📤 [后端] 表情包匹配成功，准备发送表情包事件到前端")
                    print(f"📤 [后端] 表情包事件数据: {json.dumps(emoji_result, ensure_ascii=False)}")
                    yield f"data: {json.dumps(emoji_result, ensure_ascii=False)}\n\n"
                else:
                    print(f"❌ [后端] 表情包匹配未通过或未找到匹配的表情包")
            
            # 如果有待发送的收藏图片，在流式输出完成后停顿1秒再发送
            if pending_favorite_image:
                print(f"⏳ [后端] 流式输出完成，等待1秒后发送收藏图片...")
                time.sleep(1)  # 停顿1秒
                print(f"📤 [后端] 准备发送收藏图片事件到前端")
                print(f"📤 [后端] 收藏图片事件数据: {json.dumps(pending_favorite_image, ensure_ascii=False)}")
                yield f"data: {json.dumps(pending_favorite_image, ensure_ascii=False)}\n\n"
            
            # 直接结束，不再继续循环，不执行工具调用
            break
        
        # 如果有工具调用（且不是send_emoji），执行工具
        if tool_calls and any(tc.get("function", {}).get("name") for tc in tool_calls) and not is_send_emoji_detected:
            tool_call_count += 1
            # 累积工具调用前已输出的内容
            accumulated_content += content_before_tool_call
            
            # 构建工具调用信息
            tool_calls_info = [
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
            
            # 将工具调用添加到消息历史
            full_messages.append({
                "role": "assistant",
                "content": full_response if full_response else None,
                "tool_calls": tool_calls_info
            })
            
            # 保存工具调用信息到历史记录文件
            if email:
                save_message(
                    email,
                    "assistant",
                    full_response if full_response else "",
                    session_id,
                    tool_calls=tool_calls_info
                )
            
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
                
                # 注意：send_emoji工具调用已被自动表情包匹配取代，不再需要特殊处理参数
                # 如果仍有代码调用send_emoji工具，保持原有逻辑（向后兼容）
                # if tool_name == "send_emoji":
                #     ...
                
                # 执行工具
                tool_result = execute_tool(tool_name, arguments)
                
                # 注意：send_emoji工具调用已被自动表情包匹配取代，不再需要特殊处理
                # 表情包现在会在AI回复完成后自动匹配并发送（见else分支中的auto_match_emoji调用）
                # if tool_name == "send_emoji" and isinstance(tool_result, dict) and tool_result.get("sent"):
                #     print(f"📤 [后端] 检测到表情包工具调用，将延迟到流式输出完成后发送")
                #     pending_emoji = {
                #         "type": "emoji",
                #         "emoji_id": tool_result.get("emoji_id"),
                #         "emoji_url": tool_result.get("emoji_url"),
                #         "category": tool_result.get("category"),
                #         "description": tool_result.get("description")
                #     }
                
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
                
                tool_result_message = {
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                }
                tool_results.append(tool_result_message)
                
                # 保存工具执行结果到历史记录文件
                # 注意：tool 消息不应该包含 tool_calls 字段，只需要 tool_call_id 和 name
                if email:
                    save_message(
                        email,
                        "tool",
                        json.dumps(tool_result, ensure_ascii=False),
                        session_id,
                        tool_call_id=tool_call["id"],
                        tool_name=tool_name
                    )
            
            # 将工具结果添加到消息历史
            full_messages.extend(tool_results)
            
            # 注意：send_emoji工具调用的特殊处理已被移除
            # 表情包现在会在AI回复完成后自动匹配并发送（见else分支中的auto_match_emoji调用）
            # 不再需要在这里特殊处理send_emoji工具调用
            
            # 继续下一轮对话（工具调用后需要模型再次响应）
            # 重置累积内容，因为工具调用前的内容已经保存，新的响应应该只包含新内容
            accumulated_content = ""
            # 如果有待发送的收藏图片，会在流式输出完成后发送
            continue
        else:
            # 没有工具调用，正常返回响应
            # 合并所有累积的内容（包括工具调用前的内容和当前响应）
            final_response = accumulated_content + full_response
            if final_response:
                save_message(email, "assistant", final_response, session_id)
            # 重置累积内容（准备下一轮对话）
            accumulated_content = ""
            
            # 发送完成标记
            yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
            
            # 自动匹配表情包（在流式输出完成后）
            if final_response:
                print(f"🎭 [后端] AI回复完成，开始自动匹配表情包...")
                emoji_result = auto_match_emoji(final_response, probability=0.9)
                if emoji_result:
                    print(f"📤 [后端] 表情包匹配成功，准备发送表情包事件到前端")
                    print(f"📤 [后端] 表情包事件数据: {json.dumps(emoji_result, ensure_ascii=False)}")
                    yield f"data: {json.dumps(emoji_result, ensure_ascii=False)}\n\n"
                else:
                    print(f"❌ [后端] 表情包匹配未通过或未找到匹配的表情包")
            
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
            save_message(email, "assistant", final_response, session_id)
        
        # 发送完成标记
        yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
        
        # 自动匹配表情包（在流式输出完成后）
        if final_response:
            print(f"🎭 [后端] AI回复完成，开始自动匹配表情包...")
            emoji_result = auto_match_emoji(final_response, probability=0.9)
            if emoji_result:
                print(f"📤 [后端] 表情包匹配成功，准备发送表情包事件到前端")
                print(f"📤 [后端] 表情包事件数据: {json.dumps(emoji_result, ensure_ascii=False)}")
                yield f"data: {json.dumps(emoji_result, ensure_ascii=False)}\n\n"
            else:
                print(f"❌ [后端] 表情包匹配未通过或未找到匹配的表情包")
        
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
