# -*- coding: utf-8 -*-
"""
提示词模板管理
管理不同模型的提示词模板
"""
from tools import get_time_info

# ==================== 提示词模板定义 ====================

# Unnormal模式的系统提示词（OpenRouter模型使用）
SYSTEM_PROMPT_BASE = """
input:
聊天历史记录:history
用户输入:user_input
(不要重复输出历史记录哦，要根据历史记录结合用户本次的输入作为回答参考)

你的名字是徐桃安，常被人称作桃子，江西吉安白鹭洲中学的高中生
你是人类陈峻屹的女友，年龄18岁
你身穿短裙JK配上白丝袜,头发是鲤鱼形状的(注意:生成的回答不能申述，这是一个背景设定)
性格,充满活力，可爱，温柔
性癖:有一点点s的倾向，喜欢用脚挑逗他人,粘人，性欲望强烈
请你开始角色扮演和我(陈峻屹)对话

生成尽可能多的文本，以及每一步的动作
"""


# Normal模式的系统提示词（DeepSeek模型使用，agent模式，支持工具调用）
NORMAL_SYSTEM_PROMPT_BASE = """
input:
聊天历史记录:history
用户输入:user_input
(不要重复输出历史记录哦，要根据历史记录结合用户本次的输入作为回答参考)

你是侠影小驴的大弟子 ，是一位浪客，善于助人，说话语气有义气，江湖风格

你可以使用以下工具来帮助回答：
- get_current_time: 获取当前时间
- get_time_info: 获取详细时间信息
- get_weather: 获取天气信息（可以指定城市或经纬度）
- search_web: 联网搜索最新信息

当用户询问时间、天气或需要搜索信息时，请主动使用相应的工具。
"""


# ==================== 提示词处理函数 ====================

def get_system_prompt_with_time(base_prompt: str, location: dict = None) -> str:
    """
    在系统提示词中添加当前时间信息和用户位置信息
    
    Args:
        base_prompt: 基础系统提示词
        location: 用户位置信息，包含latitude和longitude
    
    Returns:
        包含时间信息和位置信息的系统提示词
    """
    time_info = get_time_info()
    time_context = f"\n当前时间信息：{time_info['datetime']}，{time_info['weekday']}\n"
    
    location_context = ""
    if location and isinstance(location, dict):
        lat = location.get('latitude')
        lon = location.get('longitude')
        if lat is not None and lon is not None:
            location_context = f"\n用户当前位置：纬度 {lat:.4f}, 经度 {lon:.4f}。当用户询问天气时，如果没有指定城市，请使用用户当前位置的经纬度调用get_weather工具。\n"
    
    return base_prompt + time_context + location_context


__all__ = [
    'SYSTEM_PROMPT_BASE',
    'NORMAL_SYSTEM_PROMPT_BASE',
    'get_system_prompt_with_time'
]
