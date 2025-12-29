# -*- coding: utf-8 -*-
"""
聊天核心API路由
处理聊天、历史记录、清空历史等功能
"""
import json
import re
from pathlib import Path
from flask import Blueprint, request, jsonify, Response, stream_with_context, session, url_for
from werkzeug.utils import secure_filename
from config.llm.base.history import get_conversation_history, save_message, clear_history, set_current_file
from config.llm.base.history.cleanup import cleanup_empty_json_files
from config.llm import llm_stream  # 向后兼容

# 创建蓝图
chat_api_bp = Blueprint('chat_api', __name__)


@chat_api_bp.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    # 检查是否登录
    user_email = session.get('email')
    if not user_email:
        return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
    
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    mode = data.get('mode', 'normal')  # 获取模式参数，默认为normal
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


@chat_api_bp.route('/history/<session_id>', methods=['GET'])
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
    
    # 第一遍遍历：收集所有收藏图片tool消息，建立与assistant消息的映射关系
    # key: assistant消息在history中的索引，value: 收藏图片信息列表
    favorite_images_map = {}
    for i, msg in enumerate(history):
        if msg.get('role') == 'tool' and msg.get('name') == 'send_favorite_image':
            try:
                # 解析tool消息的content字段（JSON格式）
                tool_content = json.loads(msg.get('content', '{}'))
                if tool_content.get('sent') and tool_content.get('image_url'):
                    # 查找该tool消息之前的最近一个assistant消息的索引
                    for j in range(i - 1, -1, -1):
                        if history[j].get('role') == 'assistant':
                            if j not in favorite_images_map:
                                favorite_images_map[j] = []
                            favorite_images_map[j].append({
                                'image_url': tool_content.get('image_url'),
                                'description': tool_content.get('description'),
                                'timestamp': msg.get('timestamp', '')
                            })
                            break
            except (json.JSONDecodeError, ValueError):
                pass
    
    # 第二遍遍历：处理消息并插入收藏图片
    for i, msg in enumerate(history):
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
        
        # 如果是assistant消息，检查是否有对应的收藏图片，如果有则添加
        if msg.get('role') == 'assistant' and i in favorite_images_map:
            for fav_img in favorite_images_map[i]:
                favorite_img_msg = {
                    'role': 'assistant',
                    'content': fav_img.get('description', '') if fav_img.get('description') else '',
                    'image_url': fav_img['image_url'],
                    'timestamp': fav_img.get('timestamp', msg.get('timestamp', ''))
                }
                processed_history.append(favorite_img_msg)
    
    return jsonify({'history': processed_history, 'current_file': current_file})


@chat_api_bp.route('/clear/<session_id>', methods=['POST'])
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


@chat_api_bp.route('/cleanup-empty-history', methods=['POST'])
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

