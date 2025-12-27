# -*- coding: utf-8 -*-
"""
配置模块统一导出
所有 LLM 相关配置已整合到 route.config.llm 模块
"""
# 从 llm 模块导入所有内容并重新导出
from route.config.llm import (
    # 配置常量
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    DEFAULT_MODE, MAX_HISTORY_LENGTH, TEMPERATURE,
    # 提示词
    SYSTEM_PROMPT_BASE, NORMAL_SYSTEM_PROMPT_BASE, get_system_prompt_with_time,
    # 历史管理
    get_conversation_history, save_message, clear_history, create_history_file,
    # LLM处理
    llm_stream, llm_stream_normal, llm_stream_unnormal,
    # 集成接口
    stream_llm_response, get_available_models, switch_model,
    # 模型管理
    get_model_handler, MODEL_REGISTRY
)

__all__ = [
    # 配置常量
    'OPENROUTER_API_KEY', 'OPENROUTER_BASE_URL', 'OPENROUTER_MODEL',
    'DEEPSEEK_API_KEY', 'DEEPSEEK_BASE_URL', 'DEEPSEEK_MODEL',
    'DEFAULT_MODE', 'MAX_HISTORY_LENGTH', 'TEMPERATURE',
    # 提示词
    'SYSTEM_PROMPT_BASE', 'NORMAL_SYSTEM_PROMPT_BASE', 'get_system_prompt_with_time',
    # 历史管理
    'get_conversation_history', 'save_message', 'clear_history', 'create_history_file',
    # LLM处理
    'llm_stream', 'llm_stream_normal', 'llm_stream_unnormal',
    # 集成接口
    'stream_llm_response', 'get_available_models', 'switch_model',
    # 模型管理
    'get_model_handler', 'MODEL_REGISTRY'
]
