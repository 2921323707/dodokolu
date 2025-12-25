# -*- coding: utf-8 -*-
"""
时间工具模块
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Union


# 中国时区（UTC+8）
CHINA_TZ = timezone(timedelta(hours=8))


def get_current_time() -> str:
    """
    获取当前时间，返回格式化的时间字符串（本地时间，UTC+8）
    
    Returns:
        str: 格式化的时间字符串，例如 "2024-01-15 14:30:25"
    """
    now = datetime.now(CHINA_TZ)
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_time_info() -> Dict[str, Any]:
    """
    获取详细的时间信息（本地时间，UTC+8）
    
    Returns:
        dict: 包含日期、时间、星期等信息
    """
    now = datetime.now(CHINA_TZ)
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


def convert_utc_to_local(dt_str: str) -> str:
    """
    将UTC时间字符串转换为本地时间（UTC+8）字符串
    
    Args:
        dt_str: UTC时间字符串，格式如 "2025-12-25 04:21:50" 或 "2025-12-25T04:21:50"
    
    Returns:
        str: 本地时间字符串，格式 "2025-12-25 12:21:50"
    """
    if not dt_str:
        return dt_str
    
    try:
        # 尝试多种时间格式
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f"
        ]
        
        dt = None
        for fmt in formats:
            try:
                dt = datetime.strptime(dt_str, fmt)
                break
            except ValueError:
                continue
        
        if dt is None:
            return dt_str
        
        # 如果没有时区信息，假设是UTC时间
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        # 转换为中国时区
        local_dt = dt.astimezone(CHINA_TZ)
        
        # 返回格式化的时间字符串
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        # 如果转换失败，返回原始字符串
        return dt_str


def is_datetime_field(field_name: str) -> bool:
    """
    判断字段名是否可能是时间字段
    
    Args:
        field_name: 字段名
    
    Returns:
        bool: 如果是时间相关字段名则返回True
    """
    datetime_keywords = ['time', 'date', 'at', 'timestamp', 'created', 'updated']
    field_lower = field_name.lower()
    return any(keyword in field_lower for keyword in datetime_keywords)


def convert_row_datetime_fields(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    转换字典中所有时间字段从UTC到本地时间（UTC+8）
    
    Args:
        row: 包含数据的字典
    
    Returns:
        dict: 转换后的字典
    """
    converted = {}
    for key, value in row.items():
        if isinstance(value, str) and is_datetime_field(key):
            converted[key] = convert_utc_to_local(value)
        else:
            converted[key] = value
    return converted

