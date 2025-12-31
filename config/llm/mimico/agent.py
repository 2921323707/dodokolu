# -*- coding: utf-8 -*-
"""
Mimico 智能体实现（米米可）
基于 Minimax API（使用 Anthropic SDK）的 Agent
Minimax M2.1 是完整的 agentic model，不需要外部工具
"""
import os
import json
import time
from typing import List, Dict, Any, Optional, Generator
import anthropic
from config.llm.base.agent import BaseAgent
from config.llm.base.settings import MINIMAX_API_KEY, MINIMAX_BASE_URL, MINIMAX_MODEL
from config.llm.base.prompts.utils import get_system_prompt_with_time
from config.llm.mimico.prompt import SYSTEM_PROMPT_BASE
from config.llm.base.history import save_message


class MimicoAgent(BaseAgent):
    """
    Mimico 智能体（米米可）
    基于 Minimax API（使用 Anthropic SDK）的 Agent 实现
    
    注意：Minimax M2.1 是完整的 agentic model，自带联网搜索、天气查询等功能，
    不需要任何外部工具（包括 search_web、get_weather、send_emoji、send_favorite_image）
    """
    
    def __init__(self):
        super().__init__(
            name="米米可",
            description="基于 Minimax API 的智能体，内置联网搜索和天气查询功能"
        )
        self._client = None
        self._model = MINIMAX_MODEL
        self._max_tokens = 4096
        
        # 设置 Minimax API 配置
        self._base_url = MINIMAX_BASE_URL
        self._api_key = MINIMAX_API_KEY
        
        # 设置环境变量（Anthropic SDK 使用）
        if self._base_url:
            os.environ["ANTHROPIC_BASE_URL"] = self._base_url
        if self._api_key:
            os.environ["ANTHROPIC_API_KEY"] = self._api_key
    
    def _create_client(self):
        """创建 Anthropic API 客户端（用于 Minimax）"""
        if self._client is None:
            if not self._api_key:
                raise ValueError("MINIMAX_API_KEY 未配置，请在 .env 文件中设置")
            
            self._client = anthropic.Anthropic(
                base_url=self._base_url,
                api_key=self._api_key,
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
        获取工具列表（Anthropic 格式）
        
        注意：Minimax M2.1 是 agentic model，自带联网搜索、天气查询等功能，
        不需要任何外部工具（包括 search_web、get_weather、send_emoji、send_favorite_image）
        
        Returns:
            工具定义列表（Anthropic 格式），对于 Minimax M2.1 返回空列表
        """
        # Minimax M2.1 是完整的 agentic model，不需要任何外部工具
        return []
    
    def _process_response_blocks(self, response):
        """
        处理响应中的内容块（thinking、text）
        
        Args:
            response: API 响应对象
        
        Returns:
            tuple: (thinking_blocks, text_blocks, full_text)
        """
        thinking_blocks = []
        text_blocks = []
        full_text = ""
        
        # 遍历所有内容块
        for block in response.content:
            if block.type == "thinking":
                thinking_blocks.append(block)
            elif block.type == "text":
                text_blocks.append(block)
                full_text += block.text
        
        return thinking_blocks, text_blocks, full_text
    
    def _handle_final_response(self, final_response, email, session_id):
        """
        处理最终响应（发送完成标记）
        
        Args:
            final_response: 最终响应内容
            email: 用户邮箱
            session_id: 会话ID
        
        Yields:
            str: SSE格式的响应数据
        """
        if final_response:
            save_message(email, "assistant", final_response, session_id)
        
        # 发送完成标记
        yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
    
    def stream_response(
        self,
        messages: List[Dict[str, Any]],
        session_id: str,
        location: Optional[Dict[str, float]] = None,
        email: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        流式生成响应
        
        注意：Minimax M2.1 是 agentic model，自带联网搜索、天气查询等功能，
        不需要任何外部工具，直接返回模型响应即可。
        
        Args:
            messages: 消息列表
            session_id: 会话ID
            location: 用户位置信息（可选）
            email: 用户邮箱（用于历史记录存储）
        
        Yields:
            str: SSE格式的流式响应数据
        """
        client = self._create_client()
        
        # 每次循环都重新生成系统提示词，确保使用最新的时间信息
        system_prompt = self.get_system_prompt(location)
        
        # 调用 API（注意：Minimax 可能不支持流式，这里先使用非流式）
        # 使用 system 参数传递系统提示词（Anthropic SDK 支持）
        # 不传递 tools 参数，因为 Minimax M2.1 不需要外部工具
        try:
            response = client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=system_prompt,
                messages=messages,
            )
        except Exception as e:
            print(f"❌ [后端] API 调用失败: {e}")
            error_msg = f"抱歉，服务暂时不可用：{str(e)}"
            yield f"data: {json.dumps({'content': error_msg, 'done': False}, ensure_ascii=False)}\n\n"
            yield from self._handle_final_response(error_msg, email, session_id)
            return
        
        # 处理响应块
        thinking_blocks, text_blocks, full_text = self._process_response_blocks(response)
        
        # 如果有文本内容，流式输出（模拟流式）
        if text_blocks:
            # 将文本分块输出，模拟流式效果
            text_content = full_text
            chunk_size = 10  # 每次输出10个字符
            for i in range(0, len(text_content), chunk_size):
                chunk = text_content[i:i + chunk_size]
                yield f"data: {json.dumps({'content': chunk, 'done': False}, ensure_ascii=False)}\n\n"
                time.sleep(0.01)  # 小延迟以模拟流式效果
        
        # 返回最终响应
        yield from self._handle_final_response(full_text, email, session_id)
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行工具调用（保留接口以兼容基类，但 Minimax M2.1 不需要外部工具）
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
        
        Returns:
            工具执行结果（对于 Minimax M2.1，此方法不会被调用）
        """
        # Minimax M2.1 不需要外部工具，此方法保留仅为兼容接口
        return {"error": "Minimax M2.1 不需要外部工具", "success": False}

