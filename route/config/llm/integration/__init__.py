# -*- coding: utf-8 -*-
"""
LLM 统一集成接口
提供统一的模型调用接口，支持模型切换
方便后续扩展和管理
"""
from route.config.llm.model import get_model_handler
from route.config.llm.setting import DEFAULT_MODE


def stream_llm_response(messages, session_id, model_name=None, location=None):
    """
    统一的 LLM 流式输出接口
    
    Args:
        messages: 消息列表
        session_id: 会话ID
        model_name: 模型名称，如果为None则使用默认模型
                   可选值: 'openrouter', 'deepseek', 'unnormal', 'normal'
        location: 用户位置信息（可选），包含latitude和longitude
    
    Yields:
        str: SSE格式的流式响应数据
    
    Example:
        # 使用默认模型
        for chunk in stream_llm_response(messages, session_id):
            yield chunk
        
        # 使用指定模型
        for chunk in stream_llm_response(messages, session_id, model_name='deepseek'):
            yield chunk
    """
    # 如果未指定模型，使用默认模型
    if model_name is None:
        model_name = DEFAULT_MODE
    
    # 获取对应的模型处理器
    handler = get_model_handler(model_name)
    
    # 调用模型处理器
    yield from handler(messages, session_id, location)


def get_available_models():
    """
    获取所有可用的模型列表
    
    Returns:
        dict: 模型信息字典，包含模型名称和描述
    """
    return {
        'openrouter': {
            'name': 'OpenRouter',
            'description': 'OpenRouter模型（unnormal模式）',
            'alias': 'unnormal'
        },
        'deepseek': {
            'name': 'DeepSeek',
            'description': 'DeepSeek模型（normal模式，支持工具调用）',
            'alias': 'normal'
        }
    }


def switch_model(model_name):
    """
    切换默认模型（此功能可用于后台管理员配置）
    
    注意：此函数主要用于设置环境变量，实际使用时建议在调用时指定model_name参数
    
    Args:
        model_name: 模型名称
    
    Returns:
        bool: 切换是否成功
    """
    from route.config.llm.model import MODEL_REGISTRY
    
    if model_name not in MODEL_REGISTRY:
        return False
    
    # 这里可以实现持久化配置，例如写入配置文件或数据库
    # 当前实现仅返回验证结果
    return True


__all__ = [
    'stream_llm_response',
    'get_available_models',
    'switch_model'
]
