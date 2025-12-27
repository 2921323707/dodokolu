# -*- coding: utf-8 -*-
"""
对话历史和记忆管理
使用文件存储，每个用户的历史记录存储在 database/history/chat_history/{邮箱}/{时间戳}.json
"""
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from route.config.llm.setting import MAX_HISTORY_LENGTH

# 历史记录文件存储目录
HISTORY_DIR = Path(__file__).parent.parent.parent.parent.parent / 'database' / 'history' / 'chat_history'

# 线程本地存储，用于存储当前会话文件
_thread_local = threading.local()


def _ensure_history_dir():
    """确保历史记录目录存在"""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _get_user_dir(email):
    """
    获取用户历史记录文件夹路径
    
    Args:
        email: 用户邮箱
    
    Returns:
        Path: 用户文件夹路径
    """
    _ensure_history_dir()
    # 将邮箱中的特殊字符替换为安全字符，用于文件夹名
    safe_email = email.replace('@', '_at_').replace('.', '_')
    user_dir = HISTORY_DIR / safe_email
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def _get_latest_history_file(email):
    """
    获取最新的历史记录文件路径
    
    Args:
        email: 用户邮箱
    
    Returns:
        Path: 最新的历史记录文件路径，如果不存在则返回None
    """
    user_dir = _get_user_dir(email)
    
    # 查找所有 JSON 文件
    json_files = list(user_dir.glob('*.json'))
    
    if not json_files:
        return None
    
    # 按修改时间排序，返回最新的
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    return latest_file


def _create_new_history_file(email):
    """
    创建新的历史记录文件（使用时间戳命名）
    
    Args:
        email: 用户邮箱
    
    Returns:
        Path: 新创建的历史记录文件路径
    """
    user_dir = _get_user_dir(email)
    
    # 使用时间戳作为文件名（格式：YYYYMMDD_HHMMSS.json）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}.json"
    file_path = user_dir / filename
    
    # 创建空的历史记录文件
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f'创建历史记录文件失败: {e}')
        raise
    
    return file_path


def get_conversation_history(email, session_id=None, current_file=None):
    """
    获取对话历史
    
    Args:
        email: 用户邮箱（如果为None，则使用session_id作为向后兼容）
        session_id: 会话ID（保留参数以兼容现有代码）
        current_file: 当前会话文件名（如果提供，则加载该文件；否则加载最新的文件）
    
    Returns:
        tuple: (历史记录列表, 当前会话文件路径)
    """
    # 向后兼容：如果email为None，使用session_id
    if email is None:
        if session_id is None:
            return [], None
        # 将session_id作为标识符使用（向后兼容）
        email = session_id
    
    user_dir = _get_user_dir(email)
    
    # 如果指定了当前文件，使用该文件
    if current_file:
        file_path = user_dir / current_file
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    if not isinstance(history, list):
                        return [], str(file_path.name)
                    return history, str(file_path.name)
            except (json.JSONDecodeError, IOError) as e:
                print(f'读取历史记录文件失败: {e}')
    
    # 如果没有指定文件或文件不存在，查找最新的文件
    latest_file = _get_latest_history_file(email)
    
    if latest_file is None:
        # 如果没有历史文件，创建新的
        new_file = _create_new_history_file(email)
        return [], str(new_file.name)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            if not isinstance(history, list):
                return [], str(latest_file.name)
            return history, str(latest_file.name)
    except (json.JSONDecodeError, IOError) as e:
        print(f'读取历史记录文件失败: {e}')
        return [], str(latest_file.name)


def set_current_file(email, current_file):
    """
    设置当前会话文件（线程本地存储）
    
    Args:
        email: 用户邮箱
        current_file: 当前会话文件名
    """
    _thread_local.current_file = (email, current_file)


def get_current_file(email):
    """
    获取当前会话文件（从线程本地存储）
    
    Args:
        email: 用户邮箱
    
    Returns:
        str: 当前会话文件名，如果不存在则返回None
    """
    if hasattr(_thread_local, 'current_file'):
        stored_email, current_file = _thread_local.current_file
        if stored_email == email:
            return current_file
    return None


def save_message(email, role, content, session_id=None, current_file=None):
    """
    保存消息到历史
    
    Args:
        email: 用户邮箱（如果为None，则使用session_id作为向后兼容）
        role: 角色（user/assistant/system）
        content: 消息内容
        session_id: 会话ID（保留参数以兼容现有代码）
        current_file: 当前会话文件名（如果提供，则保存到该文件；否则从线程本地存储获取，或使用最新的文件或创建新的）
    
    Returns:
        str: 当前会话文件名
    """
    # 向后兼容：如果email为None，使用session_id
    if email is None:
        if session_id is None:
            return None  # 无法保存，因为没有标识符
        # 将session_id作为标识符使用（向后兼容）
        email = session_id
    
    # 如果没有提供 current_file，尝试从线程本地存储获取
    if current_file is None:
        current_file = get_current_file(email)
    
    user_dir = _get_user_dir(email)
    
    # 确定要使用的文件
    if current_file:
        file_path = user_dir / current_file
        # 如果文件不存在，创建新的
        if not file_path.exists():
            file_path = _create_new_history_file(email)
            current_file = file_path.name
    else:
        # 如果没有指定文件，查找最新的文件
        latest_file = _get_latest_history_file(email)
        if latest_file is None:
            # 如果没有历史文件，创建新的
            file_path = _create_new_history_file(email)
            current_file = file_path.name
        else:
            file_path = latest_file
            current_file = latest_file.name
    
    # 更新线程本地存储
    set_current_file(email, current_file)
    
    # 读取现有历史
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
            if not isinstance(history, list):
                history = []
    except (json.JSONDecodeError, IOError):
        history = []
    
    # 添加新消息
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    
    # 限制历史记录长度，避免过长
    if len(history) > MAX_HISTORY_LENGTH:
        history = history[-MAX_HISTORY_LENGTH:]
    
    # 保存到文件
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f'保存历史记录文件失败: {e}')
    
    return current_file


def clear_history(email, session_id=None):
    """
    清空历史记录（创建新的会话文件）
    
    Args:
        email: 用户邮箱
        session_id: 会话ID（保留参数以兼容现有代码）
    
    Returns:
        str: 新创建的会话文件名
    """
    # 向后兼容：如果email为None，使用session_id
    if email is None:
        if session_id is None:
            return None
        email = session_id
    
    # 创建新的历史记录文件
    new_file = _create_new_history_file(email)
    return new_file.name


def create_history_file(email):
    """
    创建用户历史记录文件夹和初始会话文件（如果不存在）
    
    Args:
        email: 用户邮箱
    
    Returns:
        str: 创建的会话文件名，如果已存在则返回最新的文件名
    """
    user_dir = _get_user_dir(email)
    
    # 检查是否已有历史文件
    latest_file = _get_latest_history_file(email)
    if latest_file is not None:
        return latest_file.name
    
    # 如果没有历史文件，创建新的
    new_file = _create_new_history_file(email)
    return new_file.name


__all__ = [
    'get_conversation_history',
    'save_message',
    'clear_history',
    'create_history_file',
    'set_current_file',
    'get_current_file'
]
