# -*- coding: utf-8 -*-
"""
生成API路由
处理图片和视频生成功能
"""
import os
import json
import tempfile
import requests
from pathlib import Path
from flask import Blueprint, request, jsonify, session, url_for
from openai import OpenAI
from dotenv import load_dotenv
from config.llm.base.history import get_conversation_history, save_message, set_current_file, HISTORY_DIR
from config.llm.agent_config import is_agent_online
from route.chat_route.utils import generate_video

# 加载环境变量
load_dotenv()

# 创建蓝图
generation_api_bp = Blueprint('generation_api', __name__)


@generation_api_bp.route('/generate-image', methods=['POST'])
def generate_image_api():
    """生成图片API"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
        
        data = request.json
        mode = data.get('mode', 'normal') if data else 'normal'
        
        # 检查智能体是否在线
        if not is_agent_online(mode):
            return jsonify({'error': '智能体当前离线，无法使用图像生成功能'}), 503
        
        prompt = data.get('prompt', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not prompt:
            return jsonify({'error': '提示词不能为空'}), 400
        
        # 直接调用API获取图片URL（不下载到临时文件）
        image_client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=os.environ.get("ARK_API_KEY"),
        )
        
        images_response = image_client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=prompt,
            size="4K",
            response_format="url",
            extra_body={
                "watermark": False,
            },
        )
        
        # 获取图片URL
        cloud_image_url = images_response.data[0].url
        
        # 确定保存目录（保存到static/imgs/user_chat）
        save_dir = Path('static') / 'imgs' / 'user_chat'
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名：用户邮箱_对话id_x.jpg/png
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        # 获取该用户在该session中已存在的文件数量
        existing_files = list(save_dir.glob(f"{safe_email}_{session_id}_*"))
        file_num = len(existing_files) + 1
        
        # 从URL下载文件并确定文件扩展名
        response = requests.get(cloud_image_url, stream=True)
        response.raise_for_status()
        
        # 确定文件扩展名（通过下载少量内容判断文件类型）
        first_chunk = next(response.iter_content(chunk_size=4), b'')
        response.close()  # 关闭第一个response
        
        # 重新创建response用于完整下载
        response = requests.get(cloud_image_url, stream=True)
        response.raise_for_status()
        
        if first_chunk[:4] == b'\x89PNG' or '.png' in cloud_image_url.lower():
            ext = 'png'
        elif first_chunk[:2] == b'\xff\xd8' or '.jpg' in cloud_image_url.lower() or '.jpeg' in cloud_image_url.lower():
            ext = 'jpg'
        else:
            ext = 'jpg'  # 默认jpg
        
        filename = f"{safe_email}_{session_id}_{file_num}.{ext}"
        file_path = save_dir / filename
        
        # 保存文件
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # 生成访问URL
        relative_path = f"imgs/user_chat/{filename}"
        image_url = url_for('static', filename=relative_path)
        
        # 获取当前会话文件名
        current_file = session.get('current_history_file')
        history, current_file = get_conversation_history(user_email, session_id, current_file)
        if current_file:
            session['current_history_file'] = current_file
            set_current_file(user_email, current_file)
        
        # 检查历史记录中是否已有该指令的用户消息，如果有则更新，否则创建新消息
        # 查找最后一条用户消息，看是否是该指令
        user_command_message = None
        for msg in reversed(history):
            if msg.get("role") == "user" and msg.get("content", "").startswith(f"/image {prompt}"):
                user_command_message = msg
                break
        
        # 保存指令执行结果到历史记录
        command_info = {
            "type": "image",
            "prompt": prompt,
            "result": {
                "image_url": image_url,
                "file_path": str(file_path),
                "filename": filename
            },
            "success": True
        }
        
        # 如果找到了用户消息，更新它；否则创建新消息
        if user_command_message:
            # 更新现有消息，添加command_info
            # 需要重新读取历史记录文件并更新
            # 构建用户目录路径
            safe_email = user_email.replace('@', '_at_').replace('.', '_')
            user_dir = HISTORY_DIR / safe_email
            file_path_history = user_dir / current_file
            try:
                with open(file_path_history, 'r', encoding='utf-8') as f:
                    history_list = json.load(f)
                # 找到并更新最后一条匹配的用户消息
                for msg in reversed(history_list):
                    if msg.get("role") == "user" and msg.get("content", "").startswith(f"/image {prompt}"):
                        msg["command_info"] = command_info
                        break
                # 保存更新后的历史记录
                with open(file_path_history, 'w', encoding='utf-8') as f:
                    json.dump(history_list, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f'更新历史记录失败: {e}')
                # 如果更新失败，创建新消息
                save_message(
                    user_email, 
                    "user", 
                    f"/image {prompt}", 
                    session_id, 
                    current_file,
                    command_info=command_info
                )
        else:
            # 如果没有找到，创建新消息
            save_message(
                user_email, 
                "user", 
                f"/image {prompt}", 
                session_id, 
                current_file,
                command_info=command_info
            )
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'file_path': str(file_path)
        })
        
    except Exception as e:
        print(f'生成图片错误: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成图片失败: {str(e)}'}), 500


@generation_api_bp.route('/generate-video', methods=['POST'])
def generate_video_api():
    """生成视频API"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
        
        data = request.json
        mode = data.get('mode', 'normal') if data else 'normal'
        
        # 检查智能体是否在线
        if not is_agent_online(mode):
            return jsonify({'error': '智能体当前离线，无法使用视频生成功能'}), 503
        
        prompt = data.get('prompt', '').strip()
        session_id = data.get('session_id', 'default')
        duration = data.get('duration', 5)  # 默认5秒
        watermark = data.get('watermark', False)  # 默认False
        
        if not prompt:
            return jsonify({'error': '提示词不能为空'}), 400
        
        # 构建完整的prompt，包含参数
        full_prompt = f"{prompt} --duration {duration} --watermark {'true' if watermark else 'false'}"
        
        # 调用生成视频函数获取云端URL（需要修改seedance.py来获取URL）
        # 暂时使用临时目录，然后从返回的文件中读取
        temp_dir = tempfile.mkdtemp()
        file_path = generate_video(
            prompt=full_prompt,
            save_dir=temp_dir
        )
        
        # 由于seedance已经下载了文件，我们需要重新调用API获取URL
        # 或者修改seedance.py，这里我们直接读取文件然后移动
        # 为了获取URL，我们需要重新调用API（这里简化处理，直接使用已下载的文件）
        
        # 读取临时文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 删除临时文件
        try:
            os.remove(file_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        # 确定保存目录（保存到static/video/user_chat）
        save_dir = Path('static') / 'video' / 'user_chat'
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名：用户邮箱_对话id_x.mp4
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        # 获取该用户在该session中已存在的文件数量
        existing_files = list(save_dir.glob(f"{safe_email}_{session_id}_*"))
        file_num = len(existing_files) + 1
        
        filename = f"{safe_email}_{session_id}_{file_num}.mp4"
        file_path = save_dir / filename
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # 生成访问URL
        relative_path = f"video/user_chat/{filename}"
        video_url = url_for('static', filename=relative_path)
        
        # 获取当前会话文件名
        current_file = session.get('current_history_file')
        history, current_file = get_conversation_history(user_email, session_id, current_file)
        if current_file:
            session['current_history_file'] = current_file
            set_current_file(user_email, current_file)
        
        # 检查历史记录中是否已有该指令的用户消息，如果有则更新，否则创建新消息
        # 查找最后一条用户消息，看是否是该指令
        user_command_message = None
        for msg in reversed(history):
            if msg.get("role") == "user" and msg.get("content", "").startswith(f"/video {prompt}"):
                user_command_message = msg
                break
        
        # 保存指令执行结果到历史记录
        command_info = {
            "type": "video",
            "prompt": prompt,
            "result": {
                "video_url": video_url,
                "file_path": str(file_path),
                "filename": filename,
                "duration": duration,
                "watermark": watermark
            },
            "success": True
        }
        
        # 如果找到了用户消息，更新它；否则创建新消息
        if user_command_message:
            # 更新现有消息，添加command_info
            # 需要重新读取历史记录文件并更新
            safe_email = user_email.replace('@', '_at_').replace('.', '_')
            user_dir = HISTORY_DIR / safe_email
            file_path_history = user_dir / current_file
            try:
                with open(file_path_history, 'r', encoding='utf-8') as f:
                    history_list = json.load(f)
                # 找到并更新最后一条匹配的用户消息
                for msg in reversed(history_list):
                    if msg.get("role") == "user" and msg.get("content", "").startswith(f"/video {prompt}"):
                        msg["command_info"] = command_info
                        break
                # 保存更新后的历史记录
                with open(file_path_history, 'w', encoding='utf-8') as f:
                    json.dump(history_list, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f'更新历史记录失败: {e}')
                # 如果更新失败，创建新消息
                save_message(
                    user_email, 
                    "user", 
                    f"/video {prompt}", 
                    session_id, 
                    current_file,
                    command_info=command_info
                )
        else:
            # 如果没有找到，创建新消息
            save_message(
                user_email, 
                "user", 
                f"/video {prompt}", 
                session_id, 
                current_file,
                command_info=command_info
            )
        
        return jsonify({
            'success': True,
            'video_url': video_url,
            'file_path': str(file_path)
        })
        
    except Exception as e:
        print(f'生成视频错误: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成视频失败: {str(e)}'}), 500

