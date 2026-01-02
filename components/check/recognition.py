# -*- coding: utf-8 -*-
"""
打卡截图识别功能
支持识别多邻国、百词斩等学习app的打卡截图，判断是否打卡成功
"""
import os
import base64
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Dict, List
from datetime import datetime

load_dotenv()

# 初始化OpenAI客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)


def analyze_check_in_screenshot(
    image_path: str = None,
    image_base64: str = None,
    image_url: str = None,
    model: str = "doubao-seed-1-6-flash-250828",
    reasoning_effort: str = "high"
) -> Dict:
    """
    分析打卡截图，识别app类型并判断是否打卡成功
    
    Args:
        image_path: 本地图片文件路径（可选）
        image_base64: base64编码的图片数据（可选，格式：data:image/jpeg;base64,xxx）
        image_url: 图片URL地址（可选）
        model: 使用的模型ID，默认为 doubao-seed-1-6-flash-250828
        reasoning_effort: 推理强度，可选值: minimal, low, medium, high，默认medium以获得更准确的分析
    
    Returns:
        格式化的分析结果字典:
        {
            "success": True/False,  # 是否成功识别
            "app_name": "app名称",  # 识别的app名称（如：多邻国、百词斩等）
            "check_in_status": "success"/"failed"/"unknown",  # 打卡状态
            "check_in_date": "2024-01-01",  # 打卡日期（如果可识别）
            "details": "详细描述",  # 详细分析结果
            "confidence": "high"/"medium"/"low",  # 识别置信度
            "raw_response": "原始响应"  # 原始API响应（用于调试）
        }
    """
    # 构建专门的打卡识别提示词
    current_time = datetime.now().strftime("%Y")
    prompt = f"""当前时间：{current_time}年

请仔细分析这张截图，判断这是哪个学习app的打卡截图，以及是否打卡成功。

请按以下JSON格式输出分析结果（只输出JSON，不要有其他文字）：
{{
    "app_name": "app名称（如：多邻国、百词斩、扇贝单词、墨墨背单词、不背单词等，如果无法识别则返回'unknown'）",
    "check_in_status": "打卡状态（success表示打卡成功，failed表示打卡失败，unknown表示无法确定）",
    "check_in_date": "打卡日期（格式：YYYY-MM-DD，如果无法识别则返回'unknown'）没有年份默认为当前年份",
    "details": "详细描述（说明识别依据，比如看到了什么文字、图标、状态等）",
    "confidence": "置信度（high/medium/low）"
}}



如果图片不是打卡截图，或者无法识别，请将app_name设为"unknown"，check_in_status设为"unknown"。
"""
    
    # 确定使用哪种图片输入方式
    if image_base64:
        # 如果已经是 base64 格式（包含 data:image/... 前缀），直接使用
        if image_base64.startswith('data:image/'):
            image_data = image_base64
        else:
            # 否则添加默认前缀
            image_data = f"data:image/jpeg;base64,{image_base64}"
    elif image_path:
        # 从本地文件读取并转换为 base64
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"图片文件不存在: {image_path}",
                "app_name": "unknown",
                "check_in_status": "unknown",
                "check_in_date": "unknown",
                "details": f"文件路径不存在: {image_path}",
                "confidence": "low"
            }
        
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            image_base64_str = base64.b64encode(image_bytes).decode('utf-8')
            # 根据文件扩展名确定 MIME 类型
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            image_data = f"data:{mime_type};base64,{image_base64_str}"
    elif image_url:
        # 使用 URL（仅当 URL 可公开访问时）
        image_data = image_url
    else:
        return {
            "success": False,
            "error": "必须提供 image_url、image_path 或 image_base64 之一",
            "app_name": "unknown",
            "check_in_status": "unknown",
            "check_in_date": "unknown",
            "details": "未提供图片输入",
            "confidence": "low"
        }
    
    try:
        # 调用API进行识别
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data}},
                    ],
                }
            ],
            reasoning_effort=reasoning_effort
        )
        
        raw_response = completion.choices[0].message.content
        
        # 尝试解析JSON响应
        try:
            # 清理响应文本，提取JSON部分
            response_text = raw_response.strip()
            # 如果响应包含代码块标记，提取JSON部分
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # 解析JSON
            result = json.loads(response_text)
            
            # 格式化返回结果
            return {
                "success": True,
                "app_name": result.get("app_name", "unknown"),
                "check_in_status": result.get("check_in_status", "unknown"),
                "check_in_date": result.get("check_in_date", "unknown"),
                "details": result.get("details", ""),
                "confidence": result.get("confidence", "medium"),
                "raw_response": raw_response
            }
        except json.JSONDecodeError as e:
            # 如果JSON解析失败，尝试从文本中提取信息
            return {
                "success": False,
                "error": f"JSON解析失败: {str(e)}",
                "app_name": "unknown",
                "check_in_status": "unknown",
                "check_in_date": "unknown",
                "details": raw_response,
                "confidence": "low",
                "raw_response": raw_response
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"API调用失败: {str(e)}",
            "app_name": "unknown",
            "check_in_status": "unknown",
            "check_in_date": "unknown",
            "details": f"识别过程出错: {str(e)}",
            "confidence": "low"
        }


def format_check_in_result(result: Dict) -> str:
    """
    格式化打卡识别结果为可读的字符串
    
    Args:
        result: analyze_check_in_screenshot 返回的结果字典
    
    Returns:
        格式化的字符串
    """
    if not result.get("success"):
        error_msg = result.get("error", "未知错误")
        return f"❌ 识别失败: {error_msg}\n详细信息: {result.get('details', '无')}"
    
    app_name = result.get("app_name", "unknown")
    status = result.get("check_in_status", "unknown")
    date = result.get("check_in_date", "unknown")
    details = result.get("details", "")
    confidence = result.get("confidence", "medium")
    
    # 状态图标
    status_icon = {
        "success": "✅",
        "failed": "❌",
        "unknown": "❓"
    }.get(status, "❓")
    
    # 置信度显示
    confidence_text = {
        "high": "高",
        "medium": "中",
        "low": "低"
    }.get(confidence, "未知")
    
    # 构建格式化输出
    output = f"""
{'='*50}
📱 打卡截图识别结果
{'='*50}
应用名称: {app_name}
打卡状态: {status_icon} {status}
打卡日期: {date}
识别置信度: {confidence_text}
{'='*50}
详细说明:
{details}
{'='*50}
"""
    
    return output.strip()


# 测试函数
def test_recognition(image_path: str):
    """
    测试打卡识别功能
    
    Args:
        image_path: 测试图片路径
    """
    print(f"\n开始测试打卡识别功能...")
    print(f"图片路径: {image_path}")
    print(f"{'='*50}\n")
    
    # 调用识别函数
    result = analyze_check_in_screenshot(image_path=image_path)
    
    # 格式化输出
    formatted_output = format_check_in_result(result)
    print(formatted_output)
    
    # 打印原始JSON结果（用于调试）
    print(f"\n原始JSON结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return result


if __name__ == "__main__":
    """
    直接运行此文件时进行测试
    使用方法: python recognition.py [图片路径]
    """
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python recognition.py <图片路径>")
        print("示例: python recognition.py test_image.jpg")
        print("\n注意: 请确保已设置 ARK_API_KEY 环境变量")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"❌ 错误: 文件不存在: {image_path}")
        sys.exit(1)
    
    # 运行测试
    try:
        test_recognition(image_path)
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

