# -*- coding: utf-8 -*-
"""
豆包视频生成功能封装 (Seedance模型)
"""
import os
import time
import requests
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
from typing import Optional
# 通过 pip install 'volcengine-python-sdk[ark]' 安装方舟SDK
from volcenginesdkarkruntime import Ark

load_dotenv()

# 初始化Ark客户端
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)


def generate_video(
    prompt: str,
    model: str = "doubao-seedance-1-5-pro-251215",
    image_url: Optional[str] = None,
    save_dir: Optional[str] = None,
    polling_interval: int = 3
) -> str:
    """
    使用Seedance模型生成视频并下载保存
    
    Args:
        prompt: 视频生成提示词（可包含参数如 --duration 5 --camerafixed false --watermark false）
        model: 使用的模型ID，默认为 "doubao-seedance-1-5-pro-251215"
        image_url: 首帧图片URL（可选，用于图片转视频）
        save_dir: 保存目录路径，如果为None则保存到当前文件所在目录的multi_test/video文件夹
        polling_interval: 轮询任务状态的间隔时间（秒），默认为3秒
    
    Returns:
        保存的视频文件路径
    """
    # 输出传入参数
    print("=" * 50)
    print("调用 generate_video 函数")
    print(f"参数: prompt={prompt}")
    print(f"参数: model={model}")
    print(f"参数: image_url={image_url}")
    print(f"参数: save_dir={save_dir}")
    print(f"参数: polling_interval={polling_interval}")
    print("=" * 50)
    
    # 构建内容列表
    content = [
        {
            "type": "text",
            "text": prompt
        }
    ]
    
    # 如果提供了图片URL，添加到内容中
    if image_url:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        })
    
    # 创建视频生成任务
    print("正在创建视频生成任务...")
    create_result = client.content_generation.tasks.create(
        model=model,
        content=content
    )
    print(f"任务已创建，任务ID: {create_result.id}")
    
    # 轮询查询任务状态
    print("正在轮询任务状态...")
    task_id = create_result.id
    while True:
        get_result = client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        
        if status == "succeeded":
            print("任务执行成功")
            
            # 从响应对象中提取视频URL
            video_url = None
            if hasattr(get_result, 'content') and get_result.content:
                if hasattr(get_result.content, 'video_url') and get_result.content.video_url:
                    video_url = get_result.content.video_url
                elif hasattr(get_result.content, 'url') and get_result.content.url:
                    video_url = get_result.content.url
            elif hasattr(get_result, 'output') and get_result.output:
                if isinstance(get_result.output, dict):
                    video_url = get_result.output.get('video_url') or get_result.output.get('url')
                elif isinstance(get_result.output, str):
                    video_url = get_result.output
            elif hasattr(get_result, 'video_url'):
                video_url = get_result.video_url
            elif hasattr(get_result, 'url'):
                video_url = get_result.url
            
            if not video_url:
                raise ValueError("未找到视频URL，请检查API响应结构")
            
            # 确定保存目录
            if save_dir:
                video_dir = Path(save_dir)
            else:
                video_dir = Path(__file__).parent / "multi_test" / "video"
            video_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{current_time}.mp4"
            file_path = video_dir / filename
            
            # 下载视频
            print(f"正在下载视频: {video_url}")
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            # 获取文件总大小（如果可用）
            total_size = int(response.headers.get('content-length', 0))
            
            # 保存视频文件，显示下载进度
            with open(file_path, 'wb') as f:
                if total_size > 0:
                    with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc="下载进度") as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    with tqdm(unit='B', unit_scale=True, unit_divisor=1024, desc="下载进度") as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
            
            print(f"视频已保存到: {file_path}")
            return str(file_path)
            
        elif status == "failed":
            error_msg = getattr(get_result, 'error', '未知错误')
            raise RuntimeError(f"任务执行失败: {error_msg}")
        else:
            print(f"当前状态: {status}，{polling_interval}秒后重试...")
            time.sleep(polling_interval)

