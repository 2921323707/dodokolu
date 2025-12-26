# -*- coding: utf-8 -*-
"""
聊天相关路由
"""
import os
import importlib.util
from pathlib import Path
from flask import Blueprint, request, jsonify, Response, stream_with_context, session, url_for
from werkzeug.utils import secure_filename
from route.config.llm import get_conversation_history, save_message, llm_stream, clear_history

# 导入 seed1.8.py 模块（文件名包含点号，需要特殊处理）
# 从当前文件位置（route/chat_routes.py）计算到 seed1.8.py 的路径
current_file_dir = Path(__file__).parent  # route/
seed_module_path = current_file_dir / 'config' / 'llm' / 'model' / 'multi_content' / 'seed1.8.py'
spec = importlib.util.spec_from_file_location("seed1_8", str(seed_module_path))
seed1_8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed1_8)
recognize_image = seed1_8.recognize_image

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
    
    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400
    
    # 保存用户消息
    save_message(session_id, "user", user_message)
    
    # 获取对话历史（不包括系统提示词）
    history = get_conversation_history(session_id)
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history if msg["role"] != "system"]
    
    # 返回流式响应，根据模式选择不同的LLM，传递位置信息
    return Response(
        stream_with_context(llm_stream(messages, session_id, mode, location)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """获取对话历史"""
    history = get_conversation_history(session_id)
    return jsonify({'history': history})


@chat_bp.route('/clear/<session_id>', methods=['POST'])
def clear_history_route(session_id):
    """清空对话历史"""
    clear_history(session_id)
    return jsonify({'success': True})


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
        
        return jsonify({
            'success': True,
            'description': description,
            'filename': filename
        })
        
    except Exception as e:
        print(f'上传图片错误: {e}')
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

