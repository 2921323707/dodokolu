# -*- coding: utf-8 -*-
"""
LLM 模块统一导出
仅导出 base 和 dodokolu 的公共接口
"""
# 从 base 模块导入公共接口
from config.llm.base import (
    BaseAgent,
    register_agent,
    get_agent,
    list_agents,
    AGENT_REGISTRY,
    history,
    settings,
    prompts,
    models
)

# 导入 dodokolu 模块（会自动注册 SuheyaoAgent）
import config.llm.dodokolu

# 为了向后兼容，提供旧的函数接口
def llm_stream(messages, session_id, mode='normal', location=None, email=None):
    """
    根据模式选择不同的LLM流式输出函数（向后兼容接口）
    
    注意：此函数已废弃，建议使用 Agent 框架：
        from config.llm.base import get_agent
        agent = get_agent('normal')
        agent.stream_response(messages, session_id, location, email)
    
    Args:
        messages: 消息列表
        session_id: 会话ID
        mode: 模式，'normal'，默认为 'normal'
        location: 用户位置信息（可选），包含latitude和longitude
        email: 用户邮箱（用于历史记录存储）
    
    Returns:
        生成器，产生流式响应
    """
    agent = get_agent(mode)
    return agent.stream_response(messages, session_id, location, email)


def llm_stream_normal(messages, session_id, location=None):
    """
    Normal模式的流式输出（向后兼容接口）
    
    注意：此函数已废弃，建议使用 Agent 框架
    """
    agent = get_agent('normal')
    return agent.stream_response(messages, session_id, location, None)


__all__ = [
    # Agent 框架
    'BaseAgent',
    'register_agent',
    'get_agent',
    'list_agents',
    'AGENT_REGISTRY',
    # 公共模块
    'history',
    'settings',
    'prompts',
    'models',
    # 向后兼容接口
    'llm_stream',
    'llm_stream_normal'
]
