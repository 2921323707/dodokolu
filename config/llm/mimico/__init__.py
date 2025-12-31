# -*- coding: utf-8 -*-
"""
Mimico 智能体模块（米米可）
基于 Minimax API 的智能体实现
"""
from config.llm.mimico.agent import MimicoAgent
from config.llm.base.registry import register_agent

# 自动注册 Mimico 智能体（米米可）
_mimico_agent = MimicoAgent()
register_agent('mimico', _mimico_agent)

__all__ = [
    'MimicoAgent'
]

