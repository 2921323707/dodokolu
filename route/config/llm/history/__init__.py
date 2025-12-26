# -*- coding: utf-8 -*-
"""
对话历史和记忆管理
"""
from datetime import datetime
from route.config.llm.setting import MAX_HISTORY_LENGTH

# 对话历史存储（可以改为文件存储或数据库）
conversation_history = {}


def get_conversation_history(session_id):
    """
    获取对话历史
    
    Args:
        session_id: 会话ID
    
    Returns:
        对话历史列表
    """
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    return conversation_history[session_id]


def save_message(session_id, role, content):
    """
    保存消息到历史
    
    Args:
        session_id: 会话ID
        role: 角色（user/assistant/system）
        content: 消息内容
    """
    history = get_conversation_history(session_id)
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    # 限制历史记录长度，避免过长
    if len(history) > MAX_HISTORY_LENGTH:
        conversation_history[session_id] = history[-MAX_HISTORY_LENGTH:]


def clear_history(session_id):
    """
    清空指定会话的历史记录
    
    Args:
        session_id: 会话ID
    """
    if session_id in conversation_history:
        conversation_history[session_id] = []


__all__ = [
    'conversation_history',
    'get_conversation_history',
    'save_message',
    'clear_history'
]
