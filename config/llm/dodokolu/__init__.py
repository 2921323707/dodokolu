# -*- coding: utf-8 -*-
"""
Dodokolu 智能体模块
苏禾瑶智能体的专属实现
"""
from config.llm.dodokolu.agent import SuheyaoAgent
from config.llm.base.registry import register_agent

# 自动注册苏禾瑶智能体
_suheyao_agent = SuheyaoAgent()
register_agent('suheyao', _suheyao_agent)
register_agent('normal', _suheyao_agent)  # 向后兼容
register_agent('default', _suheyao_agent)  # 默认 Agent

__all__ = [
    'SuheyaoAgent'
]

