# -*- coding: utf-8 -*-
"""
模型管理模块
统一导出所有模型接口
"""
from route.config.llm.model.openrouter import stream_completion as openrouter_stream
from route.config.llm.model.deepseek import stream_completion as deepseek_stream

# 模型映射字典
MODEL_REGISTRY = {
    'openrouter': openrouter_stream,
    'deepseek': deepseek_stream,
    # 为了向后兼容，保留模式名称映射
    'unnormal': openrouter_stream,
    'normal': deepseek_stream,
}


def get_model_handler(model_name):
    """
    根据模型名称获取对应的处理器
    
    Args:
        model_name: 模型名称（'openrouter', 'deepseek', 'unnormal', 'normal'）
    
    Returns:
        模型流式处理函数
    
    Raises:
        ValueError: 如果模型名称不存在
    """
    if model_name not in MODEL_REGISTRY:
        available_models = ', '.join(MODEL_REGISTRY.keys())
        raise ValueError(f"未知的模型名称: {model_name}。可用模型: {available_models}")
    
    return MODEL_REGISTRY[model_name]


__all__ = [
    'openrouter_stream',
    'deepseek_stream',
    'MODEL_REGISTRY',
    'get_model_handler'
]
