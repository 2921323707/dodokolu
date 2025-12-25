# -*- coding: utf-8 -*-
"""
搜索工具模块
使用Tavily API进行联网搜索
"""
import os
import requests
from typing import Dict, Any


def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    使用Tavily API进行联网搜索
    
    Args:
        query: 搜索查询词
        max_results: 最大返回结果数（默认5）
    
    Returns:
        dict: 搜索结果
    """
    try:
        api_key = os.getenv('TAVILY_API_KEY', '')
        if not api_key:
            return {
                "error": "TAVILY_API_KEY 未配置，请在 .env 文件中设置",
                "success": False
            }
        
        url = "https://api.tavily.com/search"
        headers = {
            "Content-Type": "application/json"
        }
        # 配置Tavily搜索参数：24小时内的高质量搜索
        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": "advanced",  # 高质量搜索
            "time_range": "day",  # 限制为最近24小时
            "include_answer": True,
            "include_raw_content": False,
            "max_results": max_results
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        result = {
            "success": True,
            "query": query,
            "answer": data.get("answer", ""),
            "results": []
        }
        
        # 处理搜索结果
        for item in data.get("results", []):
            result["results"].append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": item.get("score", 0)
            })
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"搜索API请求失败: {str(e)}",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"搜索时出错: {str(e)}",
            "success": False
        }

