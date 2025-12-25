# -*- coding: utf-8 -*-
"""
时间工具模块
"""
from datetime import datetime
from typing import Dict, Any


def get_current_time() -> str:
    """
    获取当前时间，返回格式化的时间字符串
    
    Returns:
        str: 格式化的时间字符串，例如 "2024-01-15 14:30:25"
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_time_info() -> Dict[str, Any]:
    """
    获取详细的时间信息
    
    Returns:
        dict: 包含日期、时间、星期等信息
    """
    now = datetime.now()
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday": weekdays[now.weekday()],
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second
    }

