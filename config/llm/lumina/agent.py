# -*- coding: utf-8 -*-
"""
Lumina 智能体实现
基于 Google Gemini Flash 3 的 Agent
"""
import json
import time
from typing import List, Dict, Any, Optional, Generator
import google.genai as genai
from config.llm.base.agent import BaseAgent
from config.llm.base.settings import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE
from config.llm.base.prompts.utils import get_system_prompt_with_time
from config.llm.lumina.prompt import SYSTEM_PROMPT_BASE
from config.llm.base.history import save_message
from tools import TOOLS, execute_tool


class LuminaAgent(BaseAgent):
    """
    Lumina 智能体
    基于 Google Gemini Flash 3 的 Agent 实现，支持工具调用
    """
    
    def __init__(self):
        super().__init__(
            name="Lumina",
            description="基于 Google Gemini Flash 3 的智能体，进行每日一文的创作"
        )
        self._client = None
        self._model = GEMINI_MODEL
        self._max_tokens = 8192
    
    def _create_client(self):
        """创建 Gemini API 客户端"""
        if self._client is None:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY 未配置，请在 .env 文件中设置")
            
            # 创建 Gemini API 客户端（新包使用客户端模式）
            # 新包仍然支持 GenerativeModel，但需要通过客户端来配置
            self._client = genai.Client(api_key=GEMINI_API_KEY)
            # 为了兼容，同时设置全局配置（如果新包支持）
            try:
                genai.configure(api_key=GEMINI_API_KEY)
            except AttributeError:
                # 新包可能不支持 configure，使用客户端即可
                pass
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
    
    def _convert_tools_to_gemini_format(self) -> List[Dict[str, Any]]:
        """
        将工具定义转换为 Gemini 格式
        
        Returns:
            Gemini 格式的工具定义列表
        """
        function_declarations = []
        for tool_name, tool_info in TOOLS.items():
            # 过滤掉 send_emoji 工具（Lumina 不支持表情包功能）
            if tool_name == "send_emoji":
                continue
            
            # 转换参数定义
            properties = {}
            required = []
            
            params = tool_info.get("parameters", {}).get("properties", {})
            for param_name, param_info in params.items():
                properties[param_name] = {
                    "type": param_info.get("type", "string"),
                    "description": param_info.get("description", "")
                }
                if param_name in tool_info.get("parameters", {}).get("required", []):
                    required.append(param_name)
            
            function_declarations.append({
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            })
        
        # Gemini SDK 期望的格式是一个包含 function_declarations 的字典
        return [{"function_declarations": function_declarations}] if function_declarations else []
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        获取工具列表（OpenAI 格式，用于兼容基类接口）
        
        Returns:
            工具定义列表
        """
        tools = []
        for tool_name, tool_info in TOOLS.items():
            # 过滤掉 send_emoji 工具（Lumina 不支持表情包功能）
            if tool_name == "send_emoji":
                continue
            
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": tool_info.get("parameters", {})
                }
            })
        return tools
    
    def _convert_messages_to_gemini_format(self, messages: List[Dict[str, Any]], system_prompt: str) -> List[Dict[str, Any]]:
        """
        将消息列表转换为 Gemini 格式
        
        Args:
            messages: 消息列表（OpenAI 格式）
            system_prompt: 系统提示词
        
        Returns:
            Gemini 格式的消息列表
        """
        gemini_messages = []
        
        # 添加系统提示词作为第一条用户消息
        if system_prompt:
            gemini_messages.append({
                "role": "user",
                "parts": [{"text": system_prompt}]
            })
            gemini_messages.append({
                "role": "model",
                "parts": [{"text": "好的，我明白了。"}]
            })
        
        # 转换消息
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # 跳过 system 角色（已在前面处理）
            if role == "system":
                continue
            
            # 处理 tool 角色（工具执行结果）
            if role == "tool":
                # Gemini 使用 function_response 格式
                tool_name = msg.get("name", "")
                tool_result = msg.get("content", "")
                tool_call_id = msg.get("tool_call_id", "")
                
                gemini_messages.append({
                    "role": "user",
                    "parts": [{
                        "function_response": {
                            "name": tool_name,
                            "response": tool_result
                        }
                    }]
                })
                continue
            
            # 处理 assistant 角色（可能包含工具调用）
            if role == "assistant":
                parts = []
                
                # 添加文本内容
                if content:
                    parts.append({"text": content})
                
                # 添加工具调用
                tool_calls = msg.get("tool_calls", [])
                for tool_call in tool_calls:
                    function_name = tool_call.get("function", {}).get("name", "")
                    function_args = tool_call.get("function", {}).get("arguments", "{}")
                    
                    try:
                        # 解析参数
                        if isinstance(function_args, str):
                            args_dict = json.loads(function_args)
                        else:
                            args_dict = function_args
                    except (json.JSONDecodeError, TypeError):
                        args_dict = {}
                    
                    parts.append({
                        "function_call": {
                            "name": function_name,
                            "args": args_dict
                        }
                    })
                
                if parts:
                    gemini_messages.append({
                        "role": "model",
                        "parts": parts
                    })
                continue
            
            # 处理 user 角色
            if role == "user":
                gemini_messages.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })
        
        return gemini_messages
    
    def _handle_final_response(self, final_response: str, email: Optional[str], session_id: str, pending_favorite_image: Optional[Dict[str, Any]]):
        """
        处理最终响应（发送完成标记、收藏图片）
        
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
            
            # 转换消息格式
            gemini_messages = self._convert_messages_to_gemini_format(full_messages, system_prompt)
            
            # 获取工具定义（Gemini 格式）
            gemini_tools = self._convert_tools_to_gemini_format()
            
            try:
                # 获取工具定义（Gemini 格式）
                gemini_tools = self._convert_tools_to_gemini_format() if TOOLS else None
                
                # 新版本的 google-genai 使用 Client 和 models.generate_content()
                # 获取最后一条用户消息
                last_user_message = gemini_messages[-1] if gemini_messages else None
                if not last_user_message or last_user_message.get("role") != "user":
                    break
                
                # 准备生成内容参数
                generate_config = {
                    "temperature": TEMPERATURE,
                    "max_output_tokens": self._max_tokens,
                }
                
                # 如果有工具，添加到配置中
                if gemini_tools and len(gemini_tools) > 0 and len(gemini_tools[0].get("function_declarations", [])) > 0:
                    generate_config["tools"] = gemini_tools
                
                # 使用 Client 生成内容（流式）
                # 新版本 API 使用 generate_content_stream
                response = client.models.generate_content_stream(
                    model=self._model,
                    contents=gemini_messages,
                    config=generate_config
                )
                
                full_response = ""
                tool_calls = []
                content_before_tool_call = ""
                has_tool_call = False
                
                # 处理流式响应
                for chunk in response:
                    # 检查是否有文本内容
                    if hasattr(chunk, 'text') and chunk.text:
                        chunk_text = chunk.text
                        full_response += chunk_text
                        if not has_tool_call:
                            content_before_tool_call += chunk_text
                            yield f"data: {json.dumps({'content': chunk_text, 'done': False}, ensure_ascii=False)}\n\n"
                    
                    # 检查是否有函数调用（Gemini SDK 格式）
                    if hasattr(chunk, 'candidates') and chunk.candidates:
                        for candidate in chunk.candidates:
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                for part in candidate.content.parts:
                                    if hasattr(part, 'function_call') and part.function_call:
                                        has_tool_call = True
                                        func_call = part.function_call
                                        if func_call and hasattr(func_call, 'name') and func_call.name:
                                            tool_calls.append({
                                                "id": func_call.name + "_" + str(tool_call_count),
                                                "name": func_call.name,
                                                "args": dict(func_call.args) if hasattr(func_call, 'args') and hasattr(func_call.args, '__iter__') and not isinstance(func_call.args, str) else (func_call.args if hasattr(func_call, 'args') else {})
                                            })
                
                # 如果有工具调用，执行工具
                if tool_calls:
                    tool_call_count += 1
                    accumulated_content += content_before_tool_call
                    
                    # 构建工具调用信息（OpenAI 格式，用于历史记录）
                    tool_calls_info = []
                    tool_results_parts = []
                    
                    for tool_call in tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call.get("args", {})
                        
                        # 如果是get_weather工具且没有提供位置参数，使用用户位置
                        if tool_name == "get_weather" and user_location:
                            if not tool_args.get("location") and not (tool_args.get("latitude") and tool_args.get("longitude")):
                                tool_args["latitude"] = user_location.get("latitude")
                                tool_args["longitude"] = user_location.get("longitude")
                        
                        # 执行工具
                        tool_result = self.execute_tool(tool_name, tool_args)
                        
                        # 特殊处理 send_favorite_image 工具
                        if tool_name == "send_favorite_image" and isinstance(tool_result, dict) and tool_result.get("sent"):
                            print(f"📤 [后端] 检测到收藏图片工具调用，将延迟到流式输出完成后发送")
                            pending_favorite_image = {
                                "type": "favorite_image",
                                "image_filename": tool_result.get("image_filename"),
                                "image_url": tool_result.get("image_url"),
                                "description": tool_result.get("description")
                            }
                        
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
                        
                        # 构建工具结果（Gemini 格式）
                        tool_results_parts.append({
                            "function_response": {
                                "name": tool_name,
                                "response": json.dumps(tool_result, ensure_ascii=False)
                            }
                        })
                        
                        # 构建工具调用信息（OpenAI 格式）
                        tool_calls_info.append({
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args, ensure_ascii=False)
                            }
                        })
                    
                    # 将工具调用添加到消息历史（OpenAI 格式）
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
                    
                    # 将工具结果添加到消息历史（OpenAI 格式）
                    for tool_call_info in tool_calls_info:
                        tool_name = tool_call_info["function"]["name"]
                        tool_result_str = None
                        for part in tool_results_parts:
                            if part["function_response"]["name"] == tool_name:
                                tool_result_str = part["function_response"]["response"]
                                break
                        
                        full_messages.append({
                            "role": "tool",
                            "name": tool_name,
                            "content": tool_result_str or "",
                            "tool_call_id": tool_call_info["id"]
                        })
                    
                    # 将工具结果添加到 Gemini 消息历史
                    gemini_messages.append({
                        "role": "user",
                        "parts": tool_results_parts
                    })
                    
                    accumulated_content = ""
                    continue
                else:
                    # 没有工具调用，正常返回响应
                    final_response = accumulated_content + full_response
                    yield from self._handle_final_response(final_response, email, session_id, pending_favorite_image)
                    accumulated_content = ""
                    break
                    
            except Exception as e:
                print(f"❌ [后端] Gemini API 调用失败: {e}")
                error_msg = f"抱歉，服务暂时不可用：{str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'done': False}, ensure_ascii=False)}\n\n"
                yield from self._handle_final_response(error_msg, email, session_id, pending_favorite_image)
                return
        
        # 如果达到最大工具调用次数，返回最终响应
        if tool_call_count >= max_tool_calls:
            final_response = accumulated_content + full_response if 'full_response' in locals() else accumulated_content
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

