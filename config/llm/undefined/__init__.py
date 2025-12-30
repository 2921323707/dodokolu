# -*- coding: utf-8 -*-
"""
Undefined 智能体模块
基于 Minimax API 的智能体实现
"""
from config.llm.undefined.agent import UndefinedAgent
from config.llm.base.registry import register_agent

# 自动注册 Undefined 智能体
_undefined_agent = UndefinedAgent()
register_agent('undefined', _undefined_agent)

__all__ = [
    'UndefinedAgent'
]

