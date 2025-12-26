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
    image_url: str,
    prompt: str = "请描述这张图片的内容，一句话简短描述输出即可，不要有任何其他内容",
    model: str = "doubao-seed-1-6-flash-250828",
    reasoning_effort: str = "minimal",
    return_reasoning: bool = False
) -> Dict[str, Optional[str]]:
    """
    图像识别功能
    
    Args:
        image_url: 图片URL地址
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
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
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

