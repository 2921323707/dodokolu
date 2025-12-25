# -*- coding: utf-8 -*-
"""
天气工具模块
使用Open-Meteo API获取天气信息
"""
import requests
from typing import Dict, Any


def get_weather(latitude: float = None, longitude: float = None, location: str = None) -> Dict[str, Any]:
    """
    使用Open-Meteo API获取天气信息
    
    Args:
        latitude: 纬度（可选，如果提供location则不需要）
        longitude: 经度（可选，如果提供location则不需要）
        location: 城市名称（可选，如果提供则自动获取经纬度）
    
    Returns:
        dict: 天气信息
    """
    try:
        # 如果没有提供经纬度，尝试通过location获取
        if location and (latitude is None or longitude is None):
            # 使用Open-Meteo的地理编码API获取坐标
            geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
            geocode_params = {
                "name": location,
                "count": 1,
                "language": "zh"
            }
            geocode_response = requests.get(geocode_url, params=geocode_params, timeout=10)
            geocode_data = geocode_response.json()
            
            if geocode_data.get("results"):
                latitude = geocode_data["results"][0]["latitude"]
                longitude = geocode_data["results"][0]["longitude"]
                location_name = geocode_data["results"][0]["name"]
            else:
                return {
                    "error": f"未找到位置: {location}",
                    "success": False
                }
        elif latitude is None or longitude is None:
            # 如果用户没有提供位置信息（拒绝了浏览器位置权限且没有指定城市），返回错误
            return {
                "error": "无法获取用户位置信息。用户拒绝了位置权限，且未指定城市名称。请询问用户所在城市，或请用户允许位置权限。",
                "success": False,
                "message": "我不知道您在哪里，无法获取天气信息。请告诉我您所在的城市，或者允许我获取您的位置。"
            }
        else:
            location_name = f"{latitude},{longitude}"
        
        # 调用Open-Meteo天气API
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,weather_code",
            "timezone": "Asia/Shanghai",
            "forecast_days": 3
        }
        
        response = requests.get(weather_url, params=weather_params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 解析天气代码
        weather_codes = {
            0: "晴朗", 1: "大部分晴朗", 2: "部分多云", 3: "阴天",
            45: "雾", 48: "沉积霜雾",
            51: "小雨", 53: "中雨", 55: "大雨",
            61: "小雨", 63: "中雨", 65: "大雨",
            71: "小雪", 73: "中雪", 75: "大雪",
            80: "小雨", 81: "中雨", 82: "大雨",
            85: "小雪", 86: "大雪",
            95: "雷暴", 96: "雷暴伴冰雹", 99: "强雷暴伴冰雹"
        }
        
        current = data.get("current", {})
        current_weather_code = int(current.get("weather_code", 0))
        
        result = {
            "success": True,
            "location": location_name,
            "current": {
                "temperature": current.get("temperature_2m", "N/A"),
                "humidity": current.get("relative_humidity_2m", "N/A"),
                "weather": weather_codes.get(current_weather_code, "未知"),
                "wind_speed": current.get("wind_speed_10m", "N/A")
            },
            "forecast": []
        }
        
        # 添加未来3天的预报
        daily = data.get("daily", {})
        if daily.get("time"):
            for i in range(min(3, len(daily["time"]))):
                forecast_code = int(daily["weather_code"][i])
                result["forecast"].append({
                    "date": daily["time"][i],
                    "max_temp": daily["temperature_2m_max"][i],
                    "min_temp": daily["temperature_2m_min"][i],
                    "weather": weather_codes.get(forecast_code, "未知")
                })
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"天气API请求失败: {str(e)}",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"获取天气信息时出错: {str(e)}",
            "success": False
        }

