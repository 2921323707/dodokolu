# -*- coding: utf-8 -*-
"""
配置模块统一导出
所有 LLM 相关配置已整合到 config.llm 模块
"""
# 从新的 base 和 llm 模块导入
from config.llm.base import (
    # 配置常量
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    DEFAULT_MODE, MAX_HISTORY_LENGTH, TEMPERATURE,
    # 历史管理
    get_conversation_history, save_message, clear_history, create_history_file,
    # 提示词
    get_system_prompt_with_time
)
from config.llm import llm_stream, llm_stream_normal

__all__ = [
    # 配置常量
    'OPENROUTER_API_KEY', 'OPENROUTER_BASE_URL', 'OPENROUTER_MODEL',
    'DEEPSEEK_API_KEY', 'DEEPSEEK_BASE_URL', 'DEEPSEEK_MODEL',
    'DEFAULT_MODE', 'MAX_HISTORY_LENGTH', 'TEMPERATURE',
    # 提示词
    'get_system_prompt_with_time',
    # 历史管理
    'get_conversation_history', 'save_message', 'clear_history', 'create_history_file',
    # LLM处理（向后兼容）
    'llm_stream', 'llm_stream_normal'
]
