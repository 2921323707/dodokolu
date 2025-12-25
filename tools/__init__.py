# -*- coding: utf-8 -*-
"""
工具模块统一导出
"""
from tools.time_tools import get_current_time, get_time_info
from tools.weather_tools import get_weather
from tools.search_tools import search_web
from typing import Dict, Any

# ==================== 工具函数映射 ====================

TOOLS = {
    "get_current_time": {
        "function": get_current_time,
        "description": "获取当前时间，返回格式化的时间字符串",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    "get_time_info": {
        "function": get_time_info,
        "description": "获取详细的时间信息，包括日期、时间、星期等",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
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
    'get_current_time',
    'get_time_info',
    'get_weather',
    'search_web',
    'TOOLS',
    'execute_tool'
]

