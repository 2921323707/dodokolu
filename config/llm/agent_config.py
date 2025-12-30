# -*- coding: utf-8 -*-
"""
智能体配置文件
管理每个智能体的在线状态
"""
from typing import Dict
import threading

# 智能体别名映射（别名 -> 真实智能体名称）
# 这些别名指向同一个智能体实例，用于向后兼容
_AGENT_ALIASES: Dict[str, str] = {
    'normal': 'suheyao',    # normal 模式映射到 suheyao
    'default': 'suheyao',   # default 映射到 suheyao
    'dodokolu': 'suheyao',  # dodokolu 映射到 suheyao（苏禾瑶智能体）
}

# 智能体在线状态配置（只存储真正的智能体状态）
# key: 真实智能体名称（注册表中的真实名称）
# value: 是否在线（True=在线，False=离线）
# 注意：此配置只存储真正的智能体，不存储别名
_AGENT_STATUS: Dict[str, bool] = {
    'suheyao': False,    # 苏禾瑶智能体（真实名称）
    'undefined': True,  # Undefined 智能体（基于 Minimax API）
}

# 线程锁，确保多线程环境下的线程安全
_status_lock = threading.Lock()


def _resolve_agent_name(agent_name: str) -> str:
    """
    解析智能体名称，将别名映射到真实名称
    
    Args:
        agent_name: 智能体名称（可能是别名）
        
    Returns:
        str: 真实的智能体名称
    """
    return _AGENT_ALIASES.get(agent_name, agent_name)


def get_agent_status(agent_name: str) -> bool:
    """
    获取智能体的在线状态
    
    Args:
        agent_name: 智能体名称（支持别名，会自动映射到真实名称）
        
    Returns:
        bool: True表示在线，False表示离线
    """
    with _status_lock:
        real_name = _resolve_agent_name(agent_name)
        return _AGENT_STATUS.get(real_name, True)  # 默认返回True（在线）


def set_agent_status(agent_name: str, is_online: bool) -> None:
    """
    设置智能体的在线状态
    
    Args:
        agent_name: 智能体名称（支持别名，会自动映射到真实名称）
        is_online: 是否在线（True=在线，False=离线）
    """
    with _status_lock:
        real_name = _resolve_agent_name(agent_name)
        _AGENT_STATUS[real_name] = is_online


def get_all_agent_status() -> Dict[str, bool]:
    """
    获取所有智能体的在线状态（只返回真正的智能体，不包括别名）
    
    Returns:
        Dict[str, bool]: 真实智能体名称到在线状态的映射
    """
    with _status_lock:
        return _AGENT_STATUS.copy()


def is_agent_online(agent_name: str) -> bool:
    """
    检查智能体是否在线（便捷方法）
    
    Args:
        agent_name: 智能体名称（支持别名，会自动映射到真实名称）
        
    Returns:
        bool: True表示在线，False表示离线
    """
    return get_agent_status(agent_name)


def set_all_agents_status(is_online: bool) -> None:
    """
    一键设置所有智能体的在线状态（只设置真正的智能体）
    
    Args:
        is_online: 是否在线（True=在线，False=离线）
    """
    with _status_lock:
        for agent_name in _AGENT_STATUS.keys():
            _AGENT_STATUS[agent_name] = is_online


__all__ = [
    'get_agent_status',
    'set_agent_status',
    'get_all_agent_status',
    'is_agent_online',
    'set_all_agents_status'
]
