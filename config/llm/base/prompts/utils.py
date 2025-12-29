# -*- coding: utf-8 -*-
"""
提示词工具函数
提供通用的提示词处理功能（如添加时间信息、位置信息等）
"""
from tools.time_tools import get_time_info


def get_system_prompt_with_time(base_prompt: str, location: dict = None) -> str:
    """
    在系统提示词中添加当前时间信息和用户位置信息
    注意：每次调用此函数都会获取最新的时间信息，确保时间信息始终是最新的
    
    Args:
        base_prompt: 基础系统提示词
        location: 用户位置信息，包含latitude和longitude
    
    Returns:
        包含时间信息和位置信息的系统提示词
    """
    # 每次调用都获取最新的时间信息
    time_info = get_time_info()
    
    # 构建更详细的时间上下文信息
    hour = time_info['hour']
    time_period = ""
    if 5 <= hour < 12:
        time_period = "上午"
    elif 12 <= hour < 14:
        time_period = "中午"
    elif 14 <= hour < 18:
        time_period = "下午"
    elif 18 <= hour < 22:
        time_period = "晚上"
    else:
        time_period = "深夜"
    
    is_weekend = time_info['weekday'] in ['星期六', '星期日']
    day_type = "周末" if is_weekend else "工作日"
    
    time_context = f"\n【当前时间】{time_info['datetime']} {time_info['weekday']}（{day_type}）{time_period}\n"
    
    location_context = ""
    if location and isinstance(location, dict):
        lat = location.get('latitude')
        lon = location.get('longitude')
        if lat is not None and lon is not None:
            location_context = f"\n【用户位置】纬度{lat:.4f}，经度{lon:.4f}（询问天气时可直接使用）\n"
    
    return base_prompt + time_context + location_context


__all__ = [
    'get_system_prompt_with_time'
]

