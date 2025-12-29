# -*- coding: utf-8 -*-
"""
苏禾瑶智能体实现
基于 DeepSeek 模型，支持工具调用的 Agent
"""
import json
import time
from typing import List, Dict, Any, Optional, Generator
from openai import OpenAI
from config.llm.base.agent import BaseAgent
from config.llm.base.settings import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TEMPERATURE
)
from config.llm.base.prompts.utils import get_system_prompt_with_time
from config.llm.dodokolu.prompt import SYSTEM_PROMPT_BASE
from config.llm.base.history import save_message
from tools import TOOLS, execute_tool
from tools.send_pics.send_pics import auto_match_emoji


class SuheyaoAgent(BaseAgent):
    """
    苏禾瑶智能体
    基于 DeepSeek 模型，支持工具调用的 Agent 实现
    """
    
    def __init__(self):
        super().__init__(
            name="苏禾瑶",
            description="温柔的女仆智能体，支持工具调用（天气、搜索、表情包等）"
        )
        self._client = None
    
    def _create_client(self):
        """创建 DeepSeek API 客户端"""
        if self._client is None:
            if not DEEPSEEK_API_KEY:
                raise ValueError("DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置")
            
            self._client = OpenAI(
                base_url=DEEPSEEK_BASE_URL,
                api_key=DEEPSEEK_API_KEY,
            )
        return self._client
    
    def get_system_prompt(self, location: Optional[Dict[str, float]] = None) -> str:
        """
        获取系统提示词（包含时间信息）
        
        Args:
            location: 用户位置信息（可选）
        
        Returns:
            系统提示词字符串
        """
        return get_system_prompt_with_time(SYSTEM_PROMPT_BASE.strip(), location)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        获取工具列表（OpenAI 格式）
        
        Returns:
            工具定义列表
        """
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
        return tools
    
    def _process_stream_chunk(self, chunk, tool_calls, is_tool_call_detected, is_send_emoji_detected):
        """
        处理流式响应的单个 chunk
        
        Args:
            chunk: API 返回的 chunk
            tool_calls: 工具调用列表（会被修改）
            is_tool_call_detected: 是否已检测到工具调用（会被修改）
            is_send_emoji_detected: 是否检测到 send_emoji（会被修改）
        
        Returns:
            tuple: (chunk_content, content_before_tool_call)
        """
        chunk_content = ""
        content_before_tool_call = ""
        
        # 处理工具调用
        if chunk.choices[0].delta.tool_calls:
            is_tool_call_detected[0] = True
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
                            is_send_emoji_detected[0] = True
                    if tool_call_delta.function.arguments:
                        current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments
        
        # 处理内容流
        chunk_content = chunk.choices[0].delta.content or ""
        if chunk_content:
            if not is_tool_call_detected[0]:
                content_before_tool_call = chunk_content
        
        return chunk_content, content_before_tool_call
    
    def _handle_emoji_detection(self, final_response, email, session_id, pending_favorite_image):
        """
        处理检测到 send_emoji 工具调用的情况
        
        Args:
            final_response: 最终响应内容
            email: 用户邮箱
            session_id: 会话ID
            pending_favorite_image: 待发送的收藏图片
        
        Yields:
            str: SSE格式的响应数据
        """
        if final_response:
            save_message(email, "assistant", final_response, session_id)
        
        # 发送完成标记
        yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
        
        # 自动匹配表情包
        if final_response:
            print(f"🎭 [后端] 检测到send_emoji工具调用，AI回复完成，开始自动匹配表情包...")
            emoji_result = auto_match_emoji(final_response, probability=0.9)
            if emoji_result:
                print(f"📤 [后端] 表情包匹配成功，准备发送表情包事件到前端")
                print(f"📤 [后端] 表情包事件数据: {json.dumps(emoji_result, ensure_ascii=False)}")
                yield f"data: {json.dumps(emoji_result, ensure_ascii=False)}\n\n"
            else:
                print(f"❌ [后端] 表情包匹配未通过或未找到匹配的表情包")
        
        # 发送收藏图片
        if pending_favorite_image:
            print(f"⏳ [后端] 流式输出完成，等待1秒后发送收藏图片...")
            time.sleep(1)
            print(f"📤 [后端] 准备发送收藏图片事件到前端")
            print(f"📤 [后端] 收藏图片事件数据: {json.dumps(pending_favorite_image, ensure_ascii=False)}")
            yield f"data: {json.dumps(pending_favorite_image, ensure_ascii=False)}\n\n"
    
    def _execute_tool_calls(self, tool_calls, user_location, email, session_id, full_messages):
        """
        执行工具调用
        
        Args:
            tool_calls: 工具调用列表
            user_location: 用户位置信息
            email: 用户邮箱
            session_id: 会话ID
            full_messages: 完整消息列表（会被修改）
        
        Returns:
            tuple: (tool_results, pending_favorite_image)
        """
        tool_results = []
        pending_favorite_image = None
        
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
            tool_result = self.execute_tool(tool_name, arguments)
            
            # 特殊处理 send_favorite_image 工具
            if tool_name == "send_favorite_image" and isinstance(tool_result, dict) and tool_result.get("sent"):
                print(f"📤 [后端] 检测到收藏图片工具调用，将延迟到流式输出完成后发送")
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
            
            # 保存工具执行结果到历史记录
            if email:
                save_message(
                    email,
                    "tool",
                    json.dumps(tool_result, ensure_ascii=False),
                    session_id,
                    tool_call_id=tool_call["id"],
                    tool_name=tool_name
                )
        
        return tool_results, pending_favorite_image
    
    def _handle_final_response(self, final_response, email, session_id, pending_favorite_image):
        """
        处理最终响应（发送完成标记、表情包、收藏图片）
        
        Args:
            final_response: 最终响应内容
            email: 用户邮箱
            session_id: 会话ID
            pending_favorite_image: 待发送的收藏图片
        
        Yields:
            str: SSE格式的响应数据
        """
        if final_response:
            save_message(email, "assistant", final_response, session_id)
        
        # 发送完成标记
        yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
        
        # 自动匹配表情包
        if final_response:
            print(f"🎭 [后端] AI回复完成，开始自动匹配表情包...")
            emoji_result = auto_match_emoji(final_response, probability=0.9)
            if emoji_result:
                print(f"📤 [后端] 表情包匹配成功，准备发送表情包事件到前端")
                print(f"📤 [后端] 表情包事件数据: {json.dumps(emoji_result, ensure_ascii=False)}")
                yield f"data: {json.dumps(emoji_result, ensure_ascii=False)}\n\n"
            else:
                print(f"❌ [后端] 表情包匹配未通过或未找到匹配的表情包")
        
        # 发送收藏图片
        if pending_favorite_image:
            print(f"⏳ [后端] 流式输出完成，等待1秒后发送收藏图片...")
            time.sleep(1)
            print(f"📤 [后端] 准备发送收藏图片事件到前端")
            print(f"📤 [后端] 收藏图片事件数据: {json.dumps(pending_favorite_image, ensure_ascii=False)}")
            yield f"data: {json.dumps(pending_favorite_image, ensure_ascii=False)}\n\n"
    
    def stream_response(
        self,
        messages: List[Dict[str, Any]],
        session_id: str,
        location: Optional[Dict[str, float]] = None,
        email: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        流式生成响应（支持工具调用）
        
        Args:
            messages: 消息列表
            session_id: 会话ID
            location: 用户位置信息（可选）
            email: 用户邮箱（用于历史记录存储）
        
        Yields:
            str: SSE格式的流式响应数据
        """
        client = self._create_client()
        tools = self.get_tools()
        user_location = location
        
        # 最大工具调用轮数，避免无限循环
        max_tool_calls = 5
        tool_call_count = 0
        pending_favorite_image = None
        accumulated_content = ""
        
        # 初始化消息列表
        full_messages = list(messages)
        
        while tool_call_count < max_tool_calls:
            # 每次循环都重新生成系统提示词，确保使用最新的时间信息
            system_prompt = self.get_system_prompt(location)
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
            content_before_tool_call = ""
            is_tool_call_detected = [False]  # 使用列表以便在函数中修改
            is_send_emoji_detected = [False]
            
            # 处理流式响应
            for chunk in stream:
                chunk_content, before_tool = self._process_stream_chunk(
                    chunk, tool_calls, is_tool_call_detected, is_send_emoji_detected
                )
                if chunk_content:
                    full_response += chunk_content
                    content_before_tool_call += before_tool
                    # 如果还没有检测到工具调用，立即输出内容
                    if not is_tool_call_detected[0]:
                        yield f"data: {json.dumps({'content': chunk_content, 'done': False}, ensure_ascii=False)}\n\n"
                    # 如果已经检测到工具调用，但不包括send_emoji，继续输出内容
                    elif not is_send_emoji_detected[0]:
                        yield f"data: {json.dumps({'content': chunk_content, 'done': False}, ensure_ascii=False)}\n\n"
            
            # 如果检测到send_emoji工具调用，立即结束
            if is_send_emoji_detected[0]:
                final_response = accumulated_content + content_before_tool_call
                yield from self._handle_emoji_detection(final_response, email, session_id, pending_favorite_image)
                accumulated_content = ""
                break
            
            # 如果有工具调用（且不是send_emoji），执行工具
            if tool_calls and any(tc.get("function", {}).get("name") for tc in tool_calls) and not is_send_emoji_detected[0]:
                tool_call_count += 1
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
                
                # 保存工具调用信息到历史记录
                if email:
                    save_message(
                        email,
                        "assistant",
                        full_response if full_response else "",
                        session_id,
                        tool_calls=tool_calls_info
                    )
                
                # 执行工具调用
                tool_results, new_pending_image = self._execute_tool_calls(
                    tool_calls, user_location, email, session_id, full_messages
                )
                if new_pending_image:
                    pending_favorite_image = new_pending_image
                
                # 将工具结果添加到消息历史
                full_messages.extend(tool_results)
                accumulated_content = ""
                continue
            else:
                # 没有工具调用，正常返回响应
                final_response = accumulated_content + full_response
                yield from self._handle_final_response(final_response, email, session_id, pending_favorite_image)
                accumulated_content = ""
                break
        
        # 如果达到最大工具调用次数，返回最终响应
        if tool_call_count >= max_tool_calls:
            final_response = accumulated_content + full_response
            yield from self._handle_final_response(final_response, email, session_id, pending_favorite_image)
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
        
        Returns:
            工具执行结果
        """
        return execute_tool(tool_name, arguments)

