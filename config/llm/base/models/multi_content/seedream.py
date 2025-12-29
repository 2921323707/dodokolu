# -*- coding: utf-8 -*-
"""
豆包图像生成功能封装 (Seedream模型)
"""
import os
import requests
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# 初始化OpenAI客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)


def generate_image(
    prompt: str,
    size: str = "4K",
    model: str = "doubao-seedream-4-5-251128",
    watermark: bool = True,
    save_dir: Optional[str] = None
) -> str:
    """
    使用Seedream模型生成图片并下载保存
    
    Args:
        prompt: 图片生成提示词
        size: 图片尺寸，默认为 "4K"
        model: 使用的模型ID，默认为 "doubao-seedream-4-5-251128"
        watermark: 是否添加水印，默认为 True
        save_dir: 保存目录路径，如果为None则保存到当前文件所在目录的photo文件夹
    
    Returns:
        保存的图片文件路径
    """
    # 输出传入参数
    print("=" * 50)
    print("调用 generate_image 函数")
    print(f"参数: prompt={prompt}")
    print(f"参数: size={size}")
    print(f"参数: model={model}")
    print(f"参数: watermark={watermark}")
    print(f"参数: save_dir={save_dir}")
    print("=" * 50)
    
    # 生成图片
    print("正在生成图片...")
    images_response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        response_format="url",
        extra_body={
            "watermark": watermark,
        },
    )
    
    # 获取图片URL
    image_url = images_response.data[0].url
    print(f"图片生成成功，URL: {image_url}")
    
    # 确定保存目录
    if save_dir:
        photo_dir = Path(save_dir)
    else:
        photo_dir = Path(__file__).parent / "multi_test" / "photo"
    photo_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_time}.jpg"
    file_path = photo_dir / filename
    
    # 下载图片
    print(f"正在下载图片: {image_url}")
    response = requests.get(image_url, stream=True)
    response.raise_for_status()
    
    # 保存图片文件
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print(f"图片已保存到: {file_path}")
    return str(file_path)

