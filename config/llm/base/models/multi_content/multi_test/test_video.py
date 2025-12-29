import os
import time
import requests
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
# 通过 pip install 'volcengine-python-sdk[ark]' 安装方舟SDK
from volcenginesdkarkruntime import Ark

load_dotenv()

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ARK_API_KEY"),
)

if __name__ == "__main__":
    print("----- create request -----")
    create_result = client.content_generation.tasks.create(
        model="doubao-seedance-1-5-pro-251215", # 模型 Model ID 已为您填入
        content=[
            {
                # 文本提示词与参数组合
                "type": "text",
                "text": "无人机以极快速度穿越复杂障碍或自然奇观，带来沉浸式飞行体验  --duration 5 --camerafixed false --watermark false"
            }
            # { # 若仅需使用文本生成视频功能，可对该大括号内的内容进行注释处理，并删除上一行中大括号后的逗号。
            #     # 首帧图片URL
            #     "type": "image_url",
            #     "image_url": {
            #         "url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seepro_i2v.png" 
            #     }
            # }
        ]
    )
    print(create_result)

    # 轮询查询部分
    print("----- polling task status -----")
    task_id = create_result.id
    while True:
        get_result = client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        if status == "succeeded":
            print("----- task succeeded -----")
            print(get_result)
            
            # 从响应对象中提取视频URL
            video_url = None
            # 根据实际响应结构，URL在 content.video_url 中
            if hasattr(get_result, 'content') and get_result.content:
                if hasattr(get_result.content, 'video_url') and get_result.content.video_url:
                    video_url = get_result.content.video_url
                elif hasattr(get_result.content, 'url') and get_result.content.url:
                    video_url = get_result.content.url
            # 兼容其他可能的响应结构
            elif hasattr(get_result, 'output') and get_result.output:
                if isinstance(get_result.output, dict):
                    video_url = get_result.output.get('video_url') or get_result.output.get('url')
                elif isinstance(get_result.output, str):
                    video_url = get_result.output
            elif hasattr(get_result, 'video_url'):
                video_url = get_result.video_url
            elif hasattr(get_result, 'url'):
                video_url = get_result.url
            
            if video_url:
                # 获取当前时间作为文件名（格式：YYYYMMDD_HHMMSS.mp4）
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{current_time}.mp4"
                
                # 确保video目录存在
                video_dir = Path(__file__).parent / "video"
                video_dir.mkdir(parents=True, exist_ok=True)
                
                # 构建完整文件路径
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
                        # 如果知道文件大小，显示进度条
                        with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc="下载进度") as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                    else:
                        # 如果不知道文件大小，显示已下载字节数
                        downloaded = 0
                        with tqdm(unit='B', unit_scale=True, unit_divisor=1024, desc="下载进度") as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    pbar.update(len(chunk))
                
                print(f"视频已保存到: {file_path}")
            else:
                print("警告: 未找到视频URL，请检查API响应结构")
                print(f"响应内容: {get_result}")
            
            break
        elif status == "failed":
            print("----- task failed -----")
            print(f"Error: {get_result.error}")
            break
        else:
            print(f"Current status: {status}, Retrying after 3 seconds...")
            time.sleep(3)

# 更多操作请参考下述网址
# 查询视频生成任务列表：https://www.volcengine.com/docs/82379/1521675
# 取消或删除视频生成任务：https://www.volcengine.com/docs/82379/1521720