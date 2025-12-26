# -*- coding: utf-8 -*-
"""
豆包图像识别功能封装
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Dict

load_dotenv()

# 初始化OpenAI客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)


def recognize_image(
    image_url: str = None,
    image_path: str = None,
    image_base64: str = None,
    prompt: str = "请描述这张图片的内容，一句话简短描述输出即可，不要有任何其他内容",
    model: str = "doubao-seed-1-6-flash-250828",
    reasoning_effort: str = "minimal",
    return_reasoning: bool = False
) -> Dict[str, Optional[str]]:
    """
    图像识别功能
    
    Args:
        image_url: 图片URL地址（可选）
        image_path: 本地图片文件路径（可选）
        image_base64: base64编码的图片数据（可选，格式：data:image/jpeg;base64,xxx）
        prompt: 识别提示词，默认为简短描述
        model: 使用的模型ID，默认为 doubao-seed-1-6-flash-250828
        reasoning_effort: 推理强度，可选值: minimal, low, medium, high
        return_reasoning: 是否返回推理过程，默认为False
    
    Returns:
        包含描述内容的字典，如果 return_reasoning=True 则同时包含推理过程
        {
            "description": "图片描述内容",
            "reasoning": "推理过程（可选）"
        }
    """
    import base64
    
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
        raise ValueError("必须提供 image_url、image_path 或 image_base64 之一")
    
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
    
    result = {
        "description": completion.choices[0].message.content
    }
    
    if return_reasoning and hasattr(completion.choices[0].message, 'reasoning_content'):
        result["reasoning"] = completion.choices[0].message.reasoning_content
    
    return result

