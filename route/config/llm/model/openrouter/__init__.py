# -*- coding: utf-8 -*-
"""
OpenRouter 模型配置和处理
"""
import json
import time
from openai import OpenAI
from openai import AuthenticationError, APIError, APIConnectionError
from route.config.llm.setting import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL, TEMPERATURE
)
from route.config.llm.prompt import get_system_prompt_with_time, SYSTEM_PROMPT_BASE
from route.config.llm.history import save_message


def create_client():
    """
    创建 OpenRouter API 客户端
    
    Returns:
        OpenAI 客户端实例
    
    Raises:
        ValueError: 如果 API Key 未配置
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY 未配置，请在 .env 文件中设置")
    
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )


def stream_completion(messages, session_id, location=None):
    """
    使用 OpenRouter API 实现流式输出
    
    Args:
        messages: 消息列表
        session_id: 会话ID
        location: 用户位置信息（可选）
    
    Yields:
        str: SSE格式的流式响应数据
    """
    client = create_client()

    # 构建完整的消息列表（系统提示词 + 历史对话 + 当前消息）
    system_prompt = get_system_prompt_with_time(SYSTEM_PROMPT_BASE.strip(), location)
    full_messages = [{"role": "system", "content": system_prompt}]
    full_messages.extend(messages)

    # 调用流式聊天接口（带重试机制）
    max_retries = 3
    retry_delay = 1  # 秒
    
    for attempt in range(max_retries):
        try:
            stream = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://localhost",
                    "X-Title": "GF_Chat"
                },
                model=OPENROUTER_MODEL,
                messages=full_messages,
                stream=True,
                temperature=TEMPERATURE
            )
            break  # 成功则跳出重试循环
        except APIConnectionError as e:
            if attempt < max_retries - 1:
                # 不是最后一次尝试，等待后重试
                time.sleep(retry_delay * (attempt + 1))  # 指数退避
                continue
            else:
                # 最后一次尝试也失败，抛出详细错误
                error_msg = f"OpenRouter API 连接失败（已重试 {max_retries} 次）: {str(e)}"
                error_msg += "\n可能的原因："
                error_msg += "\n1. 网络连接问题，请检查网络是否正常"
                error_msg += "\n2. SSL/TLS 协议问题，可能是 Python 版本或依赖库版本不兼容"
                error_msg += "\n3. 代理设置问题，如果使用代理，请检查代理配置"
                error_msg += "\n4. OpenRouter 服务器暂时不可用，请稍后重试"
                error_msg += "\n5. 防火墙或安全软件阻止了连接"
                error_msg += "\n建议："
                error_msg += "\n- 检查网络连接"
                error_msg += "\n- 尝试更新 httpx 和 openai 库：pip install --upgrade httpx openai"
                error_msg += "\n- 如果使用代理，请配置环境变量或使用代理设置"
                error_msg += "\n- 检查 Python 版本（建议使用 Python 3.10+）"
                raise ValueError(error_msg) from e
        except AuthenticationError as e:
            # 认证错误不需要重试，直接抛出
            error_msg = f"OpenRouter API 认证失败: {str(e)}"
            error_msg += "\n请检查："
            error_msg += "\n1. .env 文件中的 OPENROUTER_API_KEY 是否正确配置"
            error_msg += "\n2. API密钥是否有效（未过期或被撤销）"
            error_msg += "\n3. API密钥格式是否正确（应以 'sk-or-v1-' 开头）"
            error_msg += "\n4. 是否在 OpenRouter 网站（https://openrouter.ai/）正确创建了API密钥"
            raise ValueError(error_msg) from e
        except APIError as e:
            # 其他API错误不需要重试，直接抛出
            error_msg = f"OpenRouter API 调用失败: {str(e)}"
            raise ValueError(error_msg) from e

    full_response = ""
    for chunk in stream:
        chunk_content = chunk.choices[0].delta.content or ""
        if chunk_content:
            full_response += chunk_content
            yield f"data: {json.dumps({'content': chunk_content, 'done': False}, ensure_ascii=False)}\n\n"
    
    # 保存完整的响应到历史
    save_message(session_id, "assistant", full_response)
    yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"


__all__ = [
    'create_client',
    'stream_completion'
]
