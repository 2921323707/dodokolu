# -*- coding: utf-8 -*-
"""
聊天相关路由
"""
import os
import json
import importlib.util
import requests
from pathlib import Path
from flask import Blueprint, request, jsonify, Response, stream_with_context, session, url_for
from werkzeug.utils import secure_filename
from route.config.llm import get_conversation_history, save_message, llm_stream, clear_history, set_current_file
from route.config.llm.history.cleanup import cleanup_empty_json_files

# 导入 seed1.8.py 模块（文件名包含点号，需要特殊处理）
# 从当前文件位置（route/chat_routes.py）计算到 seed1.8.py 的路径
current_file_dir = Path(__file__).parent  # route/
seed_module_path = current_file_dir / 'config' / 'llm' / 'model' / 'multi_content' / 'seed1.8.py'
spec = importlib.util.spec_from_file_location("seed1_8", str(seed_module_path))
seed1_8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed1_8)
recognize_image = seed1_8.recognize_image

# 导入 seedream.py 和 seedance.py 模块
seedream_module_path = current_file_dir / 'config' / 'llm' / 'model' / 'multi_content' / 'seedream.py'
spec_seedream = importlib.util.spec_from_file_location("seedream", str(seedream_module_path))
seedream = importlib.util.module_from_spec(spec_seedream)
spec_seedream.loader.exec_module(seedream)
generate_image = seedream.generate_image

seedance_module_path = current_file_dir / 'config' / 'llm' / 'model' / 'multi_content' / 'seedance.py'
spec_seedance = importlib.util.spec_from_file_location("seedance", str(seedance_module_path))
seedance = importlib.util.module_from_spec(spec_seedance)
spec_seedance.loader.exec_module(seedance)
generate_video = seedance.generate_video

# 创建蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api')


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    # 检查是否登录
    user_email = session.get('email')
    if not user_email:
        return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
    
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    mode = data.get('mode', 'normal')  # 获取模式参数，默认为unnormal
    location = data.get('location', None)  # 获取用户位置信息
    image_filename = data.get('image_filename', None)  # 获取图片文件名
    
    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400
    
    # 获取当前会话文件名（从session中获取，如果没有则使用最新的）
    current_file = session.get('current_history_file')
    history, current_file = get_conversation_history(user_email, session_id, current_file)
    
    # 更新session中的当前会话文件名
    if current_file:
        session['current_history_file'] = current_file
        # 设置到线程本地存储，供模型处理器使用
        set_current_file(user_email, current_file)
    
    # 保存用户消息（使用当前会话文件），如果有图片文件名则保存
    current_file = save_message(user_email, "user", user_message, session_id, current_file, image_filename=image_filename)
    if current_file:
        session['current_history_file'] = current_file
        # 更新线程本地存储
        set_current_file(user_email, current_file)
    
    # 获取对话历史（不包括系统提示词，但保留我们转换的系统消息）
    history, _ = get_conversation_history(user_email, session_id, current_file)
    # 转换历史记录为消息列表，保留工具调用和指令调用信息
    messages = []
    for msg in history:
        # 跳过系统提示词（由模型处理器自动添加），但保留我们转换的系统消息
        # 通过检查内容是否以"用户请求生成"开头来判断是否是我们转换的系统消息
        if msg["role"] == "system" and not msg.get("content", "").startswith("用户请求生成"):
            continue
        message = {
            "role": msg["role"],
            "content": msg.get("content", "")
        }
        # 如果是 tool 角色的消息，必须包含 tool_call_id 和 name 字段
        if msg["role"] == "tool":
            if "tool_call_id" in msg:
                message["tool_call_id"] = msg["tool_call_id"]
            if "name" in msg:
                message["name"] = msg["name"]
        # 如果有工具调用信息，添加到消息中
        if "tool_calls" in msg:
            message["tool_calls"] = msg["tool_calls"]
        # 如果用户消息包含[已成功生成]标记，转换为系统消息格式
        if msg["role"] == "user" and "[已成功生成]" in msg.get("content", ""):
            content = msg.get("content", "")
            # 提取提示词：从 /image 提示词 [已成功生成] 或 /video 提示词 [已成功生成] 格式中提取
            import re
            match = re.match(r'^/(image|video)\s+(.+?)\s*\[已成功生成\]', content)
            if match:
                command_type = match.group(1)
                prompt = match.group(2).strip()
                # 转换为系统消息格式
                if command_type == "image":
                    message["role"] = "system"
                    message["content"] = f"用户请求生成图片:提示词:{prompt},生成成功"
                elif command_type == "video":
                    message["role"] = "system"
                    message["content"] = f"用户请求生成视频:提示词:{prompt},生成成功"
        # 如果有指令调用信息，将其转换为用户消息内容的一部分
        elif "command_info" in msg and msg["role"] == "user":
            command_info = msg["command_info"]
            if command_info.get("success"):
                # 将指令执行结果添加到消息内容中，让AI知道
                result_desc = ""
                if command_info["type"] == "image":
                    result_desc = f"已成功生成图片，URL：{command_info['result'].get('image_url', '')}"
                elif command_info["type"] == "video":
                    result_desc = f"已成功生成视频，URL：{command_info['result'].get('video_url', '')}"
                if result_desc:
                    message["content"] = f"{msg.get('content', '')}\n[系统提示：{result_desc}]"
        messages.append(message)
    
    # 返回流式响应，根据模式选择不同的LLM，传递位置信息和用户邮箱
    return Response(
        stream_with_context(llm_stream(messages, session_id, mode, location, user_email)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """获取对话历史"""
    # 检查是否登录
    user_email = session.get('email')
    if not user_email:
        return jsonify({'error': '未登录'}), 401
    
    # 获取当前会话文件名（从session中获取，如果没有则使用最新的）
    current_file = session.get('current_history_file')
    history, current_file = get_conversation_history(user_email, session_id, current_file)
    
    # 更新session中的当前会话文件名
    if current_file:
        session['current_history_file'] = current_file
        # 设置到线程本地存储
        set_current_file(user_email, current_file)
    
    # 处理历史记录，为包含图片描述的消息添加图片URL
    processed_history = []
    upload_dir = Path('static') / 'users' / 'chat_upload'
    safe_email = user_email.replace('@', '_at_').replace('.', '_')
    safe_email = secure_filename(safe_email)
    
    # 创建图片文件名到URL的映射
    image_map = {}
    if upload_dir.exists():
        for img_file in upload_dir.glob(f"{safe_email}_*"):
            if img_file.is_file():
                image_map[img_file.name] = url_for('static', filename=f"users/chat_upload/{img_file.name}")
    
    # 为向后兼容准备：获取所有图片按修改时间排序（用于旧数据）
    user_images_sorted = []
    if upload_dir.exists():
        for img_file in upload_dir.glob(f"{safe_email}_*"):
            if img_file.is_file():
                user_images_sorted.append({
                    'filename': img_file.name,
                    'url': url_for('static', filename=f"users/chat_upload/{img_file.name}"),
                    'mtime': img_file.stat().st_mtime
                })
        user_images_sorted.sort(key=lambda x: x['mtime'])
    
    # 用于向后兼容的索引（仅在没有文件名时使用）
    legacy_image_index = 0
    
    # 查找音频文件目录，基于文本内容匹配
    audio_dir = Path('static') / 'audio' / 'response_audio' / safe_email
    import hashlib
    import re
    
    # 为每个 assistant 消息查找对应的音频文件
    def find_audio_for_message(msg_content):
        """基于消息内容查找对应的音频文件"""
        if not msg_content or msg_content.strip() == '':
            return None
        
        # 过滤括号内容和星号（与TTS生成时保持一致）
        filtered_text = re.sub(r'[（(【\[].*?[）)\]\】]', '', msg_content)
        # 过滤掉星号
        filtered_text = re.sub(r'\*+', '', filtered_text)
        filtered_text = filtered_text.strip()
        
        if not filtered_text:
            return None
        
        # 生成文本哈希
        text_hash = hashlib.md5(filtered_text.encode('utf-8')).hexdigest()[:16]
        
        # 查找匹配的音频文件（支持两种格式：tts_{message_id}_{hash}.mp3 或 tts_{hash}.mp3）
        if audio_dir.exists():
            # 先查找带 message_id 的文件
            for audio_file in audio_dir.glob(f'tts_*_{text_hash}.mp3'):
                audio_url = url_for('static', filename=f"audio/response_audio/{safe_email}/{audio_file.name}")
                return audio_url
            
            # 再查找只有 hash 的文件
            hash_file = audio_dir / f'tts_{text_hash}.mp3'
            if hash_file.exists():
                audio_url = url_for('static', filename=f"audio/response_audio/{safe_email}/{hash_file.name}")
                return audio_url
        
        return None
    
    for msg in history:
        processed_msg = dict(msg)  # 复制消息
        
        # 跳过 system 和 tool 角色的消息（不在前端渲染）
        if msg.get('role') in ['system', 'tool']:
            continue
        
        # 跳过包含[已成功生成]标记的用户消息（不在前端显示）
        if msg.get('role') == 'user' and '[已成功生成]' in msg.get('content', ''):
            continue
        
        # 如果是用户消息且包含图片描述，添加图片URL
        if msg.get('role') == 'user' and '[图片内容：' in msg.get('content', ''):
            # 优先使用消息中保存的图片文件名进行匹配
            image_filename = msg.get('image_filename')
            if image_filename and image_filename in image_map:
                processed_msg['image_url'] = image_map[image_filename]
            # 如果没有保存的文件名，尝试按修改时间匹配（向后兼容）
            elif not image_filename and legacy_image_index < len(user_images_sorted):
                processed_msg['image_url'] = user_images_sorted[legacy_image_index]['url']
                legacy_image_index += 1
        
        # 如果是 assistant 消息，尝试查找对应的音频文件
        if msg.get('role') == 'assistant':
            msg_content = msg.get('content', '')
            audio_url = find_audio_for_message(msg_content)
            if audio_url:
                processed_msg['audio_url'] = audio_url
        
        # 如果消息包含 command_info，为生成的图片/视频创建 assistant 消息
        if 'command_info' in msg:
            command_info = msg['command_info']
            if command_info.get('success') and 'result' in command_info:
                result = command_info['result']
                # 创建 assistant 消息来显示生成的图片/视频
                assistant_msg = {
                    'role': 'assistant',
                    'content': '',
                    'timestamp': msg.get('timestamp', '')  # 使用原消息的时间戳
                }
                if command_info.get('type') == 'image' and 'image_url' in result:
                    assistant_msg['image_url'] = result['image_url']
                    assistant_msg['image_preview'] = True
                elif command_info.get('type') == 'video' and 'video_url' in result:
                    assistant_msg['video_url'] = result['video_url']
                    assistant_msg['video_preview'] = True
                # 将 assistant 消息添加到历史记录（在 user 消息之后）
                processed_history.append(processed_msg)  # 先添加 user 消息
                processed_history.append(assistant_msg)  # 再添加 assistant 消息
                continue  # 跳过后续处理，因为已经添加了
        
        processed_history.append(processed_msg)
    
    return jsonify({'history': processed_history, 'current_file': current_file})


@chat_bp.route('/clear/<session_id>', methods=['POST'])
def clear_history_route(session_id):
    """清空对话历史（创建新的会话文件）"""
    # 检查是否登录
    user_email = session.get('email')
    if not user_email:
        return jsonify({'error': '未登录'}), 401
    
    # 创建新的会话文件
    new_file = clear_history(user_email, session_id)
    
    # 更新session中的当前会话文件名
    if new_file:
        session['current_history_file'] = new_file
        # 设置到线程本地存储
        set_current_file(user_email, new_file)
    
    return jsonify({'success': True, 'current_file': new_file})


@chat_bp.route('/chat/upload-image', methods=['POST'])
def upload_image():
    """上传图片并识别"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
        
        # 检查文件是否存在
        if 'image' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 验证文件类型
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'不支持的文件格式，仅支持: {", ".join(allowed_extensions)}'}), 400
        
        # 确保上传目录存在
        upload_dir = os.path.join('static', 'users', 'chat_upload')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成文件名：邮箱_序号.扩展名
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        safe_email = secure_filename(safe_email)
        
        # 查找已存在的文件，确定序号
        existing_files = [f for f in os.listdir(upload_dir) if f.startswith(safe_email + '_')]
        if existing_files:
            # 提取最大序号
            max_num = 0
            for f in existing_files:
                try:
                    # 文件名格式：邮箱_序号.扩展名
                    parts = f.rsplit('.', 1)
                    if len(parts) == 2:
                        num_part = parts[0].rsplit('_', 1)[-1]
                        num = int(num_part)
                        if num > max_num:
                            max_num = num
                except:
                    pass
            file_num = max_num + 1
        else:
            file_num = 1
        
        filename = f"{safe_email}_{file_num}{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 调用图片识别（使用本地文件路径，自动转换为 base64）
        try:
            result = recognize_image(image_path=file_path)
            description = result.get('description', '无法识别图片内容')
        except Exception as e:
            print(f'图片识别失败: {e}')
            description = '图片识别失败，但已成功上传'
        
        # 生成图片URL
        image_url = url_for('static', filename=f"users/chat_upload/{filename}")
        
        return jsonify({
            'success': True,
            'description': description,
            'filename': filename,
            'image_url': image_url
        })
        
    except Exception as e:
        print(f'上传图片错误: {e}')
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@chat_bp.route('/chat/upload-video', methods=['POST'])
def upload_video():
    """上传视频"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
        
        # 检查文件是否存在
        if 'video' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 验证文件类型
        allowed_extensions = {'.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'不支持的文件格式，仅支持: {", ".join(allowed_extensions)}'}), 400
        
        # 确保上传目录存在
        upload_dir = os.path.join('static', 'users', 'chat_upload')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成文件名：邮箱_序号.扩展名
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        safe_email = secure_filename(safe_email)
        
        # 查找已存在的文件，确定序号
        existing_files = [f for f in os.listdir(upload_dir) if f.startswith(safe_email + '_')]
        if existing_files:
            # 提取最大序号
            max_num = 0
            for f in existing_files:
                try:
                    # 文件名格式：邮箱_序号.扩展名
                    parts = f.rsplit('.', 1)
                    if len(parts) == 2:
                        num_part = parts[0].rsplit('_', 1)[-1]
                        num = int(num_part)
                        if num > max_num:
                            max_num = num
                except:
                    pass
            file_num = max_num + 1
        else:
            file_num = 1
        
        filename = f"{safe_email}_{file_num}{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 生成访问URL
        video_url = url_for('static', filename=f'users/chat_upload/{filename}')
        
        return jsonify({
            'success': True,
            'video_url': video_url,
            'filename': filename
        })
        
    except Exception as e:
        print(f'上传视频错误: {e}')
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@chat_bp.route('/cleanup-empty-history', methods=['POST'])
def cleanup_empty_history():
    """手动清理空的历史记录文件"""
    # 检查是否登录（可选，如果需要权限控制）
    user_email = session.get('email')
    if not user_email:
        return jsonify({'error': '未登录'}), 401
    
    # 检查是否是管理员（可选，如果需要权限控制）
    # user_role = session.get('role')
    # if user_role != 2:  # 2 表示管理员
    #     return jsonify({'error': '无权限执行此操作'}), 403
    
    try:
        result = cleanup_empty_json_files()
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'deleted_count': result['deleted_count'],
                'error_count': result['error_count'],
                'total_size_freed': result['total_size_freed']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'清理失败: {str(e)}'}), 500


@chat_bp.route('/generate-image', methods=['POST'])
def generate_image_api():
    """生成图片API"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
        
        data = request.json
        prompt = data.get('prompt', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not prompt:
            return jsonify({'error': '提示词不能为空'}), 400
        
        # 直接调用API获取图片URL（不下载到临时文件）
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        
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
        from route.config.llm.history import get_conversation_history, save_message, set_current_file
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
            from route.config.llm.history import HISTORY_DIR
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


@chat_bp.route('/generate-video', methods=['POST'])
def generate_video_api():
    """生成视频API"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
        
        data = request.json
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
        import tempfile
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
        from route.config.llm.history import get_conversation_history, save_message, set_current_file, HISTORY_DIR
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


@chat_bp.route('/tts', methods=['POST'])
def tts_api():
    """TTS 语音合成API"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
        
        data = request.json
        text = data.get('text', '').strip()
        message_id = data.get('message_id', None)  # 可选的消息ID，用于缓存
        
        if not text:
            return jsonify({'error': '文本不能为空'}), 400
        
        # 过滤掉括号内的内容（角色扮演动作描述）和星号
        import re
        # 匹配中文括号、英文括号、方括号等
        filtered_text = re.sub(r'[（(【\[].*?[）)\]\】]', '', text)
        # 过滤掉星号
        filtered_text = re.sub(r'\*+', '', filtered_text)
        filtered_text = filtered_text.strip()
        
        if not filtered_text:
            return jsonify({'error': '过滤后文本为空'}), 400
        
        # 导入 TTS 模块
        import sys
        from pathlib import Path
        import hashlib
        tts_module_path = Path(__file__).parent.parent / 'components' / 'tts语音合成' / 'src.py'
        import importlib.util
        spec = importlib.util.spec_from_file_location("tts_src", str(tts_module_path))
        tts_src = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tts_src)
        
        # 创建配置
        config = tts_src.TTSConfig()
        
        # 确保音频目录存在
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        safe_email = secure_filename(safe_email)
        audio_dir = Path('static') / 'audio' / 'response_audio' / safe_email
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # 基于文本内容生成唯一ID（用于缓存）
        text_hash = hashlib.md5(filtered_text.encode('utf-8')).hexdigest()[:16]
        
        # 如果提供了 message_id，优先使用 message_id 作为文件名
        if message_id:
            filename = f"tts_{message_id}_{text_hash}.mp3"
        else:
            filename = f"tts_{text_hash}.mp3"
        
        output_file = audio_dir / filename
        
        # 检查文件是否已存在（缓存）
        if output_file.exists():
            relative_path = f"audio/response_audio/{safe_email}/{filename}"
            audio_url = url_for('static', filename=relative_path)
            return jsonify({
                'success': True,
                'audio_url': audio_url,
                'filename': filename,
                'cached': True
            })
        
        # 调用 TTS 生成语音
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(tts_src.submit_text(config, filtered_text, str(output_file)))
        finally:
            loop.close()
        
        # 检查文件是否生成成功
        if not output_file.exists():
            return jsonify({'error': '语音生成失败'}), 500
        
        # 生成访问URL
        relative_path = f"audio/response_audio/{safe_email}/{filename}"
        audio_url = url_for('static', filename=relative_path)
        
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'filename': filename,
            'cached': False
        })
        
    except Exception as e:
        print(f'TTS 生成错误: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'语音生成失败: {str(e)}'}), 500