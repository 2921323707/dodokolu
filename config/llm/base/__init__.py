# -*- coding: utf-8 -*-
"""
Base 模块 - 智能体公共接口和配置
提供所有智能体共享的基础功能
"""
from config.llm.base.agent import BaseAgent
from config.llm.base.registry import (
    register_agent,
    get_agent,
    list_agents,
    AGENT_REGISTRY
)

# 导出公共工具模块（直接导入子模块）
from config.llm.base import history
from config.llm.base import settings
from config.llm.base import prompts
from config.llm.base import models

# 为了向后兼容，从子模块导出常用函数和常量
from config.llm.base.settings import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    DEFAULT_MODE, MAX_HISTORY_LENGTH, TEMPERATURE
)
from config.llm.base.history import (
    get_conversation_history,
    save_message,
    clear_history,
    create_history_file,
    set_current_file,
    get_current_file,
    HISTORY_DIR
)
from config.llm.base.prompts import get_system_prompt_with_time

__all__ = [
    # Agent 基类
    'BaseAgent',
    # Agent 注册
    'register_agent',
    'get_agent',
    'list_agents',
    'AGENT_REGISTRY',
    # 公共模块
    'history',
    'settings',
    'prompts',
    'models',
    # 配置常量（向后兼容）
    'OPENROUTER_API_KEY', 'OPENROUTER_BASE_URL', 'OPENROUTER_MODEL',
    'DEEPSEEK_API_KEY', 'DEEPSEEK_BASE_URL', 'DEEPSEEK_MODEL',
    'DEFAULT_MODE', 'MAX_HISTORY_LENGTH', 'TEMPERATURE',
    # 历史管理（向后兼容）
    'get_conversation_history', 'save_message', 'clear_history',
    'create_history_file', 'set_current_file', 'get_current_file', 'HISTORY_DIR',
    # 提示词工具（向后兼容）
    'get_system_prompt_with_time'
]

