# -*- coding: utf-8 -*-
"""
Lumina 智能体模块
基于 Google Gemini Flash 3 的智能体实现
"""
from config.llm.lumina.agent import LuminaAgent
from config.llm.base.registry import register_agent

# 自动注册 Lumina 智能体
_lumina_agent = LuminaAgent()
register_agent('lumina', _lumina_agent)

__all__ = [
    'LuminaAgent'
]

