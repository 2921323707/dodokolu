# -*- coding: utf-8 -*-
"""
工具模块统一导出
"""
from tools.weather_tools import get_weather
from tools.search_tools import search_web
from tools.send_pics.send_pics import send_emoji, send_favorite_image
from typing import Dict, Any

# ==================== 工具函数映射 ====================

TOOLS = {
    "get_weather": {
        "function": get_weather,
        "description": "获取指定位置的天气信息，可以使用城市名称或经纬度",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市名称，例如：北京、上海、New York"
                },
                "latitude": {
                    "type": "number",
                    "description": "纬度（可选）"
                },
                "longitude": {
                    "type": "number",
                    "description": "经度（可选）"
                }
            }
        }
    },
    "search_web": {
        "function": search_web,
        "description": "使用Tavily进行联网搜索，获取最新的网络信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询词"
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大返回结果数，默认5",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    "send_emoji": {
        "function": send_emoji,
        "description": "根据AI自己的回复内容自动匹配并发送相关表情包。在你完成对用户的回复后，基于你自己的回复内容判断是否需要发送表情包。当检测到你的回复与表情包描述匹配时，按照90%的概率发送表情包。表情包会在流式输出完成后自动发送。",
        "parameters": {
            "type": "object",
            "properties": {
                "assistant_message": {
                    "type": "string",
                    "description": "AI的回复内容，用于匹配相关表情包。这是推荐使用的参数，应该传入你自己刚才的回复内容。"
                },
                "user_message": {
                    "type": "string",
                    "description": "用户的消息内容（向后兼容参数，不推荐使用）"
                },
                "probability": {
                    "type": "number",
                    "description": "发送表情包的概率，默认0.9（90%）",
                    "default": 0.9
                },
                "delay": {
                    "type": "number",
                    "description": "发送前停留时间（秒），默认0.8",
                    "default": 0.8
                },
                "describe_probability": {
                    "type": "number",
                    "description": "二次描述的概率（已废弃，保留以兼容旧代码）",
                    "default": 0.5
                }
            },
            "required": []
        }
    },
    "send_favorite_image": {
        "function": send_favorite_image,
        "description": "当用户询问AI最喜欢的图片、收藏的图片、你最喜欢的图片等类似问题时，从收藏图片目录中随机选择一张图片发送给用户。这个工具用于展示AI人格收藏的图片，增强对话的个性化。",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


def execute_tool(tool_name: str, arguments: Dict[str, Any] = None) -> Any:
    """
    执行指定的工具函数
    
    Args:
        tool_name: 工具名称
        arguments: 工具参数
    
    Returns:
        工具函数的执行结果
    """
    if tool_name not in TOOLS:
        return {"error": f"未知的工具: {tool_name}", "success": False}
    
    tool = TOOLS[tool_name]
    func = tool["function"]
    
    try:
        if arguments:
            result = func(**arguments)
        else:
            result = func()
        return result
    except Exception as e:
        return {"error": f"执行工具时出错: {str(e)}", "success": False}


# 导出所有工具函数和映射
__all__ = [
    'get_weather',
    'search_web',
    'send_emoji',
    'send_favorite_image',
    'TOOLS',
    'execute_tool'
]

