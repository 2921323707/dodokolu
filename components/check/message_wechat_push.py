# -*- coding: utf-8 -*-
"""
微信消息推送功能
使用 showdoc 推送服务发送微信消息通知
"""
import requests
from typing import Dict, Optional


# 推送服务地址
PUSH_URL = "https://push.showdoc.com.cn/server/api/push/7b7f60b0c2b8a6f05740819f7b1bd23c377111248"


def push_wechat_message(title: str, content: str, timeout: int = 10) -> Dict:
    """
    推送微信消息到 showdoc 推送服务
    
    Args:
        title: 推送的消息标题（必填）
        content: 推送的消息内容，支持文本、markdown和html（必填）
        timeout: 请求超时时间（秒），默认10秒
    
    Returns:
        dict: 推送结果
        {
            "success": True/False,  # 是否成功
            "error_code": 0/其他,  # 错误码，0表示成功
            "error_message": "ok"/错误信息,  # 错误消息
            "raw_response": {}  # 原始响应数据
        }
    
    Raises:
        ValueError: 当 title 或 content 为空时抛出异常
    """
    # 参数验证
    if not title or not title.strip():
        raise ValueError("标题不能为空")
    
    if not content or not content.strip():
        raise ValueError("内容不能为空")
    
    # 准备请求参数
    params = {
        "title": title.strip(),
        "content": content.strip()
    }
    
    try:
        # 发送 POST 请求
        response = requests.post(
            PUSH_URL,
            data=params,  # 使用 data 参数发送表单数据
            timeout=timeout
        )
        
        # 检查 HTTP 状态码
        response.raise_for_status()
        
        # 解析响应 JSON
        result = response.json()
        
        # 判断是否成功（error_code 为 0 表示成功）
        success = result.get("error_code") == 0
        
        return {
            "success": success,
            "error_code": result.get("error_code", -1),
            "error_message": result.get("error_message", "未知错误"),
            "raw_response": result
        }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_code": -1,
            "error_message": "请求超时",
            "raw_response": {}
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error_code": -1,
            "error_message": f"请求失败: {str(e)}",
            "raw_response": {}
        }
    
    except ValueError as e:
        # JSON 解析失败
        return {
            "success": False,
            "error_code": -1,
            "error_message": f"响应解析失败: {str(e)}",
            "raw_response": {}
        }
    
    except Exception as e:
        return {
            "success": False,
            "error_code": -1,
            "error_message": f"未知错误: {str(e)}",
            "raw_response": {}
        }


def format_push_result(result: Dict) -> str:
    """
    格式化推送结果为可读的字符串
    
    Args:
        result: push_wechat_message 返回的结果字典
    
    Returns:
        格式化的字符串
    """
    if result.get("success"):
        return f"[成功] 推送成功\n错误码: {result.get('error_code')}\n消息: {result.get('error_message')}"
    else:
        return f"[失败] 推送失败\n错误码: {result.get('error_code')}\n错误信息: {result.get('error_message')}"


# 测试函数
def test_push():
    """
    测试微信消息推送功能
    """
    print("=" * 50)
    print("开始测试微信消息推送功能...")
    print("=" * 50)
    
    # 测试用例 1: 正常推送
    print("\n【测试用例 1】正常推送")
    print("-" * 50)
    result1 = push_wechat_message(
        title="测试消息",
        content="这是一条测试消息，用于验证推送功能是否正常工作。"
    )
    print(format_push_result(result1))
    print(f"\n原始响应: {result1.get('raw_response')}")
    
    # 测试用例 2: 带 Markdown 格式的内容
    print("\n\n【测试用例 2】Markdown 格式内容")
    print("-" * 50)
    markdown_content = """# 打卡提醒

**今日打卡状态**: 已完成

- 应用: 多邻国
- 连续天数: 7天
- 打卡时间: 2024-01-01 08:00:00

> 继续保持，加油！"""
    
    result2 = push_wechat_message(
        title="打卡提醒",
        content=markdown_content
    )
    print(format_push_result(result2))
    print(f"\n原始响应: {result2.get('raw_response')}")
    
    # 测试用例 3: 空标题（应该抛出异常）
    print("\n\n【测试用例 3】空标题测试（应该失败）")
    print("-" * 50)
    try:
        result3 = push_wechat_message(
            title="",
            content="测试内容"
        )
        print(format_push_result(result3))
    except ValueError as e:
        print(f"[预期错误] {str(e)}")
    
    # 测试用例 4: 空内容（应该抛出异常）
    print("\n\n【测试用例 4】空内容测试（应该失败）")
    print("-" * 50)
    try:
        result4 = push_wechat_message(
            title="测试标题",
            content=""
        )
        print(format_push_result(result4))
    except ValueError as e:
        print(f"[预期错误] {str(e)}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    """
    直接运行此文件时进行测试
    使用方法: python message_wechat_push.py
    """
    try:
        test_push()
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n[错误] 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

