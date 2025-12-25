# -*- coding: utf-8 -*-
"""
对话历史管理
"""
from datetime import datetime
from route.config.settings import MAX_HISTORY_LENGTH

# 对话历史存储（可以改为文件存储或数据库）
conversation_history = {}


def get_conversation_history(session_id):
    """获取对话历史"""
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    return conversation_history[session_id]


def save_message(session_id, role, content):
    """保存消息到历史"""
    history = get_conversation_history(session_id)
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    # 限制历史记录长度，避免过长
    if len(history) > MAX_HISTORY_LENGTH:
        conversation_history[session_id] = history[-MAX_HISTORY_LENGTH:]

