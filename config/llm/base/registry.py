# -*- coding: utf-8 -*-
"""
Agent 注册系统
管理所有已注册的 Agent
"""
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from config.llm.base.agent import BaseAgent

# Agent 注册表
AGENT_REGISTRY: Dict[str, 'BaseAgent'] = {}


def register_agent(name: str, agent: 'BaseAgent'):
    """
    注册一个 Agent
    
    Args:
        name: Agent 名称
        agent: Agent 实例
    
    Raises:
        ValueError: 如果 agent 不是 BaseAgent 的实例
    """
    from config.llm.base.agent import BaseAgent
    
    if not isinstance(agent, BaseAgent):
        raise ValueError(f"Agent 必须是 BaseAgent 的实例，但收到: {type(agent)}")
    
    AGENT_REGISTRY[name] = agent


def get_agent(name: str = 'default'):
    """
    获取指定的 Agent
    
    Args:
        name: Agent 名称，默认为 'default'
    
    Returns:
        Agent 实例
    
    Raises:
        ValueError: 如果 Agent 不存在
    """
    if name not in AGENT_REGISTRY:
        available = ', '.join(AGENT_REGISTRY.keys())
        raise ValueError(f"未知的 Agent: {name}。可用 Agent: {available}")
    
    return AGENT_REGISTRY[name]


def list_agents() -> Dict[str, Dict[str, str]]:
    """
    列出所有已注册的 Agent
    
    Returns:
        Agent 信息字典，格式: {name: {'name': ..., 'description': ...}}
    """
    return {
        name: agent.get_info()
        for name, agent in AGENT_REGISTRY.items()
    }


def unregister_agent(name: str) -> bool:
    """
    取消注册一个 Agent
    
    Args:
        name: Agent 名称
    
    Returns:
        bool: 如果成功取消注册返回 True，如果 Agent 不存在返回 False
    """
    if name in AGENT_REGISTRY:
        del AGENT_REGISTRY[name]
        return True
    return False


__all__ = [
    'AGENT_REGISTRY',
    'register_agent',
    'get_agent',
    'list_agents',
    'unregister_agent'
]

