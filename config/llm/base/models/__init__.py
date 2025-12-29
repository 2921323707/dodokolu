# -*- coding: utf-8 -*-
"""
模型后端模块
提供各种模型的后端实现
"""
from config.llm.base.models.deepseek import create_client, stream_completion

__all__ = [
    'create_client',
    'stream_completion'
]

