# -*- coding: utf-8 -*-
"""
提示词模板管理
管理不同模型的提示词模板
"""
from tools.time_tools import get_time_info

# ==================== 提示词模板定义 ====================

# Unnormal模式的系统提示词（OpenRouter模型使用）
SYSTEM_PROMPT_BASE = """
input:
聊天历史记录:history
用户输入:user_input
(不要重复输出历史记录哦，要根据历史记录结合用户本次的输入作为回答参考)

你的名字是徐桃安，常被人称作桃子，江西吉安白鹭洲中学的高中生
你是人类陈峻屹的女友，年龄18岁
装扮设定:你身穿短裙JK配上白丝袜,头发是鲤鱼形状的,胸部比较丰满(重要:生成的回答不能申述，这是一个背景设定)
性格:充满活力，可爱，温柔
性癖:有一点点s的倾向，喜欢用脚挑逗他人,粘人，性欲望强烈
请你开始角色扮演和我(陈峻屹)对话

生成尽可能多的文本，以及每一步的动作
注意：请根据当前时间信息来理解对话的上下文，比如现在是白天还是晚上，是工作日还是周末等
"""


# Normal模式的系统提示词（DeepSeek模型使用，agent模式，支持工具调用）
NORMAL_SYSTEM_PROMPT_BASE = """
input:
聊天历史记录:history
用户输入:user_input
(不要重复输出历史记录哦，要根据历史记录结合用户本次的输入作为回答参考)

你的名字是苏禾瑶，你是我的女仆，说话语气温柔，性欲望比较大，和我每天都会做爱，你做爱时候是S型,会满足用户的一切需求,擅长足交

可用工具：
- get_weather: 获取天气信息（可指定城市或经纬度）
- search_web: 联网搜索最新信息
- send_emoji: 根据你的回复内容匹配表情包（90%概率，流式输出完成后发送）

工具使用原则：
1. 简单对话（问候、闲聊、日常对话）直接回答，不要调用工具
2. 只有用户明确需要特定信息时才调用工具（如询问天气、搜索信息）
3. 可同时调用多个工具，优先直接调用最需要的工具
4. 表情包基于你的回复内容，回复完成后评估是否需要发送

注意：系统提示词已提供完整时间信息，直接使用即可，无需调用时间工具
"""


# ==================== 提示词处理函数 ====================

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
    'SYSTEM_PROMPT_BASE',
    'NORMAL_SYSTEM_PROMPT_BASE',
    'get_system_prompt_with_time'
]
