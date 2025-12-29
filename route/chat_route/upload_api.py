# -*- coding: utf-8 -*-
"""
上传API路由
处理图片和视频上传功能
"""
import os
from flask import Blueprint, request, jsonify, session, url_for
from werkzeug.utils import secure_filename
from route.chat_route.utils import recognize_image

# 创建蓝图
upload_api_bp = Blueprint('upload_api', __name__)


@upload_api_bp.route('/chat/upload-image', methods=['POST'])
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


@upload_api_bp.route('/chat/upload-video', methods=['POST'])
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

