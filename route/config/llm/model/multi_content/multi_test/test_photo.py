import os
import requests
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


client = OpenAI( 
    base_url="https://ark.cn-beijing.volces.com/api/v3", 
    api_key=os.environ.get("ARK_API_KEY"), 
) 
 
imagesResponse = client.images.generate( 
    model="doubao-seedream-4-5-251128", 
    prompt="星际穿越，黑洞，黑洞里冲出一辆快支离破碎的复古列车，抢视觉冲击力，电影大片，末日既视感，动感，对比色，oc渲染，光线追踪，动态模糊，景深，超现实主义，深蓝，画面通过细腻的丰富的色彩层次塑造主体与场景，质感真实，暗黑风背景的光影效果营造出氛围，整体兼具艺术幻想感，夸张的广角透视效果，耀光，反射，极致的光影，强引力，吞噬",
    size="4K",
    response_format="url",
    extra_body={
        "watermark": True,
    },
) 

# 获取图片URL
image_url = imagesResponse.data[0].url

# 获取当前时间作为文件名（格式：YYYYMMDD_HHMMSS.jpg）
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{current_time}.jpg"

# 确保photo目录存在
photo_dir = Path(__file__).parent / "photo"
photo_dir.mkdir(parents=True, exist_ok=True)

# 构建完整文件路径
file_path = photo_dir / filename

# 下载图片
print(f"正在下载图片: {image_url}")
response = requests.get(image_url, stream=True)
response.raise_for_status()

# 保存图片文件
with open(file_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"图片已保存到: {file_path}")