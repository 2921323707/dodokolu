# -*- coding: utf-8 -*-
"""
相册API路由
"""
from flask import jsonify, request, session
from pathlib import Path
import os
import re
from route.album_route import album_bp
from route.album_route.utils import (
    CATEGORY_MAP,
    ALLOWED_EXTENSIONS,
    get_base_dir,
    check_image_permission
)


@album_bp.route('/api/images/<category>')
def get_images(category):
    """获取指定分类的图片列表API"""
    if category not in CATEGORY_MAP:
        return jsonify({
            "success": False,
            "message": "无效的分类",
            "data": []
        }), 400
    
    # 获取登录状态和角色
    user_id = session.get('user_id')
    is_logged_in = user_id is not None
    user_role = session.get('role', 0) if is_logged_in else 0
    is_admin = user_role == 2
    
    # 获取图片目录路径
    base_dir = get_base_dir(category)
    
    images = []
    
    # 遍历目录，查找所有图片文件
    if base_dir and base_dir.exists():
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                # 支持的图片格式
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
                    # 获取文件的完整路径
                    file_path = os.path.join(root, file)
                    # 获取相对路径
                    rel_path = os.path.relpath(file_path, base_dir)
                    # 获取文件修改时间
                    mtime = os.path.getmtime(file_path)
                    
                    # 判断图片类型：normal、abnormal 或其他
                    path_parts = rel_path.replace('\\', '/').split('/')
                    image_type = 'other'  # 默认类型
                    
                    if 'normal' in path_parts:
                        image_type = 'normal'
                    elif 'abnormal' in path_parts:
                        image_type = 'abnormal'
                    
                    # 权限检查：决定是否包含该图片以及是否需要模糊
                    should_include, needs_blur = check_image_permission(
                        category, image_type, is_logged_in, is_admin
                    )
                    
                    # 如果应该包含，添加到列表
                    if should_include:
                        # 转换为URL路径（使用正斜杠）
                        url_path = f"/static/imgs/album/{CATEGORY_MAP[category]}/{rel_path}".replace('\\', '/')
                        images.append({
                            "url": url_path,
                            "name": file,
                            "path": rel_path,
                            "type": image_type,  # 添加类型标记
                            "needs_blur": needs_blur,  # 标记是否需要模糊
                            "mtime": mtime  # 添加修改时间用于排序
                        })
    
    # 按修改时间排序（最新的在前）
    images.sort(key=lambda x: x['mtime'], reverse=True)
    
    # 限制最多返回12张图片
    images = images[:12]
    
    # 移除mtime字段（不需要返回给前端）
    for img in images:
        img.pop('mtime', None)
    
    return jsonify({
        "success": True,
        "data": images
    })


@album_bp.route('/api/upload', methods=['POST'])
def upload_image():
    """上传图片API（仅管理员）"""
    # 检查登录状态和权限
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "message": "请先登录"
        }), 401
    
    user_role = session.get('role', 0)
    if user_role != 2:
        return jsonify({
            "success": False,
            "message": "您没有管理员权限"
        }), 403
    
    # 获取表单数据
    category = request.form.get('category', '').strip()
    folder_type = request.form.get('folder_type', 'normal').strip()
    source = request.form.get('source', '0').strip() or '0'
    
    # 验证分类
    if category not in CATEGORY_MAP:
        return jsonify({
            "success": False,
            "message": "无效的分类"
        }), 400
    
    # 验证文件夹类型
    if folder_type not in ['normal', 'abnormal']:
        return jsonify({
            "success": False,
            "message": "无效的文件夹类型"
        }), 400
    
    # 检查文件是否存在
    if 'file' not in request.files:
        return jsonify({
            "success": False,
            "message": "没有上传文件"
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            "success": False,
            "message": "文件名为空"
        }), 400
    
    # 验证文件类型
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return jsonify({
            "success": False,
            "message": f"不支持的文件格式，支持的格式：{', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    try:
        # 构建目标目录路径
        base_dir = get_base_dir(category)
        
        # 只有anime和photo才需要normal/abnormal子文件夹
        # wallpaper和scene直接保存在分类目录下
        if category in ['anime', 'photo']:
            target_dir = base_dir / folder_type
            return_path = f"{CATEGORY_MAP[category]}/{folder_type}"
        else:
            # wallpaper和scene直接保存在分类目录
            target_dir = base_dir
            return_path = f"{CATEGORY_MAP[category]}"
        
        # 确保目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取当前文件夹中最大的序号
        max_number = 0
        if target_dir.exists():
            for existing_file in target_dir.iterdir():
                if existing_file.is_file():
                    # 匹配文件名格式：数字_来源.扩展名
                    match = re.match(r'^(\d+)_', existing_file.name)
                    if match:
                        file_number = int(match.group(1))
                        if file_number > max_number:
                            max_number = file_number
        
        # 生成新文件名：序号+1_来源.扩展名
        new_number = max_number + 1
        # 清理来源字符串，只保留字母、数字、下划线、中文字符
        safe_source = re.sub(r'[^\w\u4e00-\u9fa5]', '_', source)
        # 确保来源不为空
        if not safe_source:
            safe_source = '0'
        
        # 确保文件名安全（但保留序号和来源之间的下划线）
        filename_base = f"{new_number}_{safe_source}"
        # 只保留安全的字符
        filename_base = re.sub(r'[^\w\u4e00-\u9fa5._-]', '_', filename_base)
        new_filename = f"{filename_base}{file_ext}"
        
        # 构建完整路径
        file_path = target_dir / new_filename
        
        # 保存文件
        file.save(str(file_path))
        
        return jsonify({
            "success": True,
            "message": "上传成功",
            "data": {
                "filename": new_filename,
                "path": f"{return_path}/{new_filename}"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"上传失败：{str(e)}"
        }), 500

