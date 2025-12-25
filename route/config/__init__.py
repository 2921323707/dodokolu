# -*- coding: utf-8 -*-
"""
配置模块统一导出
为了保持向后兼容，此文件作为统一导出接口
"""
# 从各个模块导入并重新导出
from route.config.settings import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    DEFAULT_MODE, MAX_HISTORY_LENGTH, TEMPERATURE
)
from route.config.prompts import (
    SYSTEM_PROMPT_BASE,
    NORMAL_SYSTEM_PROMPT_BASE,
    get_system_prompt_with_time
)
from route.config.history import (
    conversation_history,
    get_conversation_history,
    save_message
)
from route.config.llm_handlers import (
    llm_stream,
    llm_stream_normal,
    llm_stream_unnormal
)

# 导出所有内容，保持向后兼容
__all__ = [
    # 配置常量
    'OPENROUTER_API_KEY', 'OPENROUTER_BASE_URL', 'OPENROUTER_MODEL',
    'DEEPSEEK_API_KEY', 'DEEPSEEK_BASE_URL', 'DEEPSEEK_MODEL',
    'DEFAULT_MODE', 'MAX_HISTORY_LENGTH', 'TEMPERATURE',
    # 提示词
    'SYSTEM_PROMPT_BASE', 'NORMAL_SYSTEM_PROMPT_BASE', 'get_system_prompt_with_time',
    # 历史管理
    'conversation_history', 'get_conversation_history', 'save_message',
    # LLM处理
    'llm_stream', 'llm_stream_normal', 'llm_stream_unnormal'
]

