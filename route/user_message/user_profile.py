# -*- coding: utf-8 -*-
"""
用户资料相关路由
处理用户头像上传、获取等功能
"""
from flask import Blueprint, request, jsonify, session
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime
import os

user_profile_bp = Blueprint('user_profile', __name__, url_prefix='/api/user')


def _get_user_avatar_dir(email):
    """获取用户头像文件夹路径"""
    avatar_dir = Path('database') / 'avator'
    avatar_dir.mkdir(parents=True, exist_ok=True)
    # 将邮箱中的特殊字符替换为安全字符，用于文件夹名
    safe_email = email.replace('@', '_at_').replace('.', '_')
    user_avatar_dir = avatar_dir / safe_email
    user_avatar_dir.mkdir(parents=True, exist_ok=True)
    return user_avatar_dir


def _get_latest_avatar(email):
    """获取用户最新的头像文件路径"""
    user_avatar_dir = _get_user_avatar_dir(email)
    if not user_avatar_dir.exists():
        return None
    
    # 获取所有图片文件
    image_files = []
    for ext in ['.png', '.jpg', '.jpeg']:
        image_files.extend(list(user_avatar_dir.glob(f'*{ext}')))
        image_files.extend(list(user_avatar_dir.glob(f'*{ext.upper()}')))
    
    if not image_files:
        return None
    
    # 按修改时间排序，返回最新的
    latest_file = max(image_files, key=lambda f: f.stat().st_mtime)
    return latest_file


@user_profile_bp.route('/avatar', methods=['GET'])
def get_user_avatar():
    """获取用户头像URL"""
    user_email = session.get('email')
    if not user_email:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    try:
        latest_avatar = _get_latest_avatar(user_email)
        if latest_avatar and latest_avatar.exists():
            # 生成URL路径：database/avator/邮箱文件夹/文件名
            safe_email = user_email.replace('@', '_at_').replace('.', '_')
            avatar_url = f'/database/avator/{safe_email}/{latest_avatar.name}'
            return jsonify({
                'success': True,
                'avatar_url': avatar_url,
                'has_avatar': True
            })
        else:
            return jsonify({
                'success': True,
                'avatar_url': None,
                'has_avatar': False
            })
    except Exception as e:
        print(f'获取头像失败: {e}')
        return jsonify({
            'success': True,
            'avatar_url': None,
            'has_avatar': False
        })


@user_profile_bp.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    """上传用户头像"""
    user_email = session.get('email')
    if not user_email:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    # 检查文件是否存在
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': '没有上传文件'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'}), 400
    
    # 验证文件类型
    allowed_extensions = {'.jpg', '.jpeg', '.png'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'success': False, 'message': f'不支持的文件格式，仅支持: {", ".join(allowed_extensions)}'}), 400
    
    try:
        # 获取用户头像文件夹
        user_avatar_dir = _get_user_avatar_dir(user_email)
        
        # 生成文件名：时间戳.扩展名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}{file_ext}"
        file_path = user_avatar_dir / filename
        
        # 保存文件
        file.save(str(file_path))
        
        # 生成访问URL
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        avatar_url = f'/database/avator/{safe_email}/{filename}'
        
        return jsonify({
            'success': True,
            'message': '头像上传成功',
            'avatar_url': avatar_url
        })
    except Exception as e:
        print(f'上传头像失败: {e}')
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'}), 500

