# -*- coding: utf-8 -*-
"""
LLM 模块统一导出
"""
# 从各个子模块导入
from route.config.llm.setting import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    DEFAULT_MODE, MAX_HISTORY_LENGTH, TEMPERATURE
)

from route.config.llm.prompt import (
    SYSTEM_PROMPT_BASE,
    NORMAL_SYSTEM_PROMPT_BASE,
    get_system_prompt_with_time
)

from route.config.llm.history import (
    conversation_history,
    get_conversation_history,
    save_message,
    clear_history
)

from route.config.llm.integration import (
    stream_llm_response,
    get_available_models,
    switch_model
)

from route.config.llm.model import (
    get_model_handler,
    MODEL_REGISTRY
)

# 为了向后兼容，提供旧的函数接口
def llm_stream(messages, session_id, mode='unnormal', location=None):
    """
    根据模式选择不同的LLM流式输出函数（向后兼容接口）
    
    Args:
        messages: 消息列表
        session_id: 会话ID
        mode: 模式，'normal' 或 'unnormal'，默认为 'unnormal'
        location: 用户位置信息（可选），包含latitude和longitude
    
    Returns:
        生成器，产生流式响应
    """
    return stream_llm_response(messages, session_id, model_name=mode, location=location)


def llm_stream_normal(messages, session_id, location=None):
    """
    Normal模式的流式输出（向后兼容接口）
    """
    return stream_llm_response(messages, session_id, model_name='normal', location=location)


def llm_stream_unnormal(messages, session_id, location=None):
    """
    Unnormal模式的流式输出（向后兼容接口）
    """
    return stream_llm_response(messages, session_id, model_name='unnormal', location=location)


__all__ = [
    # 配置
    'OPENROUTER_API_KEY', 'OPENROUTER_BASE_URL', 'OPENROUTER_MODEL',
    'DEEPSEEK_API_KEY', 'DEEPSEEK_BASE_URL', 'DEEPSEEK_MODEL',
    'DEFAULT_MODE', 'MAX_HISTORY_LENGTH', 'TEMPERATURE',
    # 提示词
    'SYSTEM_PROMPT_BASE', 'NORMAL_SYSTEM_PROMPT_BASE', 'get_system_prompt_with_time',
    # 历史管理
    'conversation_history', 'get_conversation_history', 'save_message', 'clear_history',
    # 集成接口
    'stream_llm_response', 'get_available_models', 'switch_model',
    # 模型管理
    'get_model_handler', 'MODEL_REGISTRY',
    # 向后兼容接口
    'llm_stream', 'llm_stream_normal', 'llm_stream_unnormal'
]
