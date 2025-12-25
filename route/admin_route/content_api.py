# -*- coding: utf-8 -*-
"""
相册内容管理API路由
"""
import os
from flask import Blueprint, request, jsonify, session
from pathlib import Path
from database import get_db_connection
from route.album_route.utils import CATEGORY_MAP, get_base_dir, ALLOWED_EXTENSIONS

content_api_bp = Blueprint('content_api', __name__, url_prefix='/api/content')


def check_admin_api():
    """检查管理员权限（API）"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    if session.get('role') != 2:
        return jsonify({'success': False, 'message': '无权限访问'}), 403
    
    return None


# ==================== 类别管理API ====================

@content_api_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有类别配置"""
    result = check_admin_api()
    if result:
        return result
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, category_key, display_name, is_visible, created_at, updated_at
            FROM album_category_config
            ORDER BY category_key
        ''')
        
        categories = []
        from tools.time_tools import convert_row_datetime_fields
        for row in cursor.fetchall():
            row_dict = {
                'id': row['id'],
                'category_key': row['category_key'],
                'display_name': row['display_name'],
                'is_visible': bool(row['is_visible']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            # 转换时间字段从UTC到本地时间（UTC+8）
            row_dict = convert_row_datetime_fields(row_dict)
            categories.append(row_dict)
        
        conn.close()
        
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取类别列表失败: {str(e)}'}), 500


@content_api_bp.route('/categories/<category_key>', methods=['PUT'])
def update_category(category_key):
    """更新类别配置"""
    result = check_admin_api()
    if result:
        return result
    
    if category_key not in CATEGORY_MAP:
        return jsonify({'success': False, 'message': '无效的类别'}), 400
    
    try:
        data = request.json
        display_name = data.get('display_name')
        is_visible = data.get('is_visible')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if display_name is not None:
            updates.append('display_name = ?')
            values.append(display_name)
        
        if is_visible is not None:
            updates.append('is_visible = ?')
            values.append(1 if is_visible else 0)
        
        if not updates:
            conn.close()
            return jsonify({'success': False, 'message': '没有要更新的字段'}), 400
        
        from tools.time_tools import get_current_time
        updates.append('updated_at = ?')
        values.append(get_current_time())
        values.append(category_key)
        sql = f"UPDATE album_category_config SET {', '.join(updates)} WHERE category_key = ?"
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


# ==================== 图片管理API ====================

@content_api_bp.route('/images/<category_key>', methods=['GET'])
def get_category_images(category_key):
    """获取类别下的所有图片"""
    result = check_admin_api()
    if result:
        return result
    
    if category_key not in CATEGORY_MAP:
        return jsonify({'success': False, 'message': '无效的类别'}), 400
    
    try:
        # 获取文件系统中的图片
        base_dir = get_base_dir(category_key)
        images = []
        
        if base_dir and base_dir.exists():
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, base_dir).replace('\\', '/')
                        url_path = f"/static/imgs/album/{CATEGORY_MAP[category_key]}/{rel_path}"
                        
                        # 获取数据库中的配置
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT display_name, is_visible
                            FROM album_image_config
                            WHERE category_key = ? AND image_path = ?
                        ''', (category_key, rel_path))
                        config = cursor.fetchone()
                        conn.close()
                        
                        images.append({
                            'path': rel_path,
                            'name': file,
                            'url': url_path,
                            'display_name': config['display_name'] if config else None,
                            'is_visible': bool(config['is_visible']) if config else True
                        })
        
        return jsonify({'success': True, 'images': images})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取图片列表失败: {str(e)}'}), 500


@content_api_bp.route('/images/<category_key>', methods=['PUT'])
def update_image(category_key):
    """更新图片配置"""
    result = check_admin_api()
    if result:
        return result
    
    if category_key not in CATEGORY_MAP:
        return jsonify({'success': False, 'message': '无效的类别'}), 400
    
    try:
        data = request.json
        image_path = data.get('image_path')
        display_name = data.get('display_name')
        is_visible = data.get('is_visible')
        
        if not image_path:
            return jsonify({'success': False, 'message': '缺少image_path字段'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否存在
        cursor.execute('''
            SELECT id FROM album_image_config
            WHERE category_key = ? AND image_path = ?
        ''', (category_key, image_path))
        
        # 使用INSERT OR REPLACE简化逻辑
        final_display_name = display_name if display_name is not None else None
        final_is_visible = 1 if (is_visible is None or is_visible) else 0
        
        from tools.time_tools import get_current_time
        cursor.execute('''
            INSERT OR REPLACE INTO album_image_config (category_key, image_path, display_name, is_visible, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (category_key, image_path, final_display_name, final_is_visible, get_current_time()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@content_api_bp.route('/images/<category_key>/rename', methods=['POST'])
def rename_image(category_key):
    """重命名图片文件"""
    result = check_admin_api()
    if result:
        return result
    
    if category_key not in CATEGORY_MAP:
        return jsonify({'success': False, 'message': '无效的类别'}), 400
    
    try:
        data = request.json
        old_path = data.get('old_path')
        new_name = data.get('new_name')
        
        if not old_path or not new_name:
            return jsonify({'success': False, 'message': '缺少必要字段'}), 400
        
        # 验证新文件名
        if not new_name.endswith(tuple(ALLOWED_EXTENSIONS)):
            return jsonify({'success': False, 'message': '新文件名必须是图片格式'}), 400
        
        base_dir = get_base_dir(category_key)
        old_file = base_dir / old_path
        new_file = base_dir / Path(old_path).parent / new_name
        
        if not old_file.exists():
            return jsonify({'success': False, 'message': '文件不存在'}), 404
        
        if new_file.exists():
            return jsonify({'success': False, 'message': '目标文件名已存在'}), 400
        
        # 重命名文件
        os.rename(str(old_file), str(new_file))
        
        # 更新数据库中的路径
        new_rel_path = os.path.relpath(new_file, base_dir).replace('\\', '/')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 更新图片配置
        from tools.time_tools import get_current_time
        cursor.execute('''
            UPDATE album_image_config
            SET image_path = ?, updated_at = ?
            WHERE category_key = ? AND image_path = ?
        ''', (new_rel_path, get_current_time(), category_key, old_path))
        
        # 更新用户权限
        cursor.execute('''
            UPDATE album_user_permission
            SET image_path = ?
            WHERE category_key = ? AND image_path = ?
        ''', (new_rel_path, category_key, old_path))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '重命名成功', 'new_path': new_rel_path})
    except Exception as e:
        return jsonify({'success': False, 'message': f'重命名失败: {str(e)}'}), 500


# ==================== 用户权限管理API ====================

@content_api_bp.route('/permissions', methods=['GET'])
def get_permissions():
    """获取用户权限列表"""
    result = check_admin_api()
    if result:
        return result
    
    try:
        category_key = request.args.get('category_key')
        image_path = request.args.get('image_path')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = '''
            SELECT p.id, p.user_id, p.category_key, p.image_path, u.username
            FROM album_user_permission p
            LEFT JOIN user_profile u ON p.user_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if category_key:
            sql += ' AND p.category_key = ?'
            params.append(category_key)
        
        if image_path:
            sql += ' AND p.image_path = ?'
            params.append(image_path)
        
        sql += ' ORDER BY p.category_key, p.image_path, u.username'
        
        cursor.execute(sql, params)
        
        permissions = []
        for row in cursor.fetchall():
            permissions.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'category_key': row['category_key'],
                'image_path': row['image_path']
            })
        
        conn.close()
        
        return jsonify({'success': True, 'permissions': permissions})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取权限列表失败: {str(e)}'}), 500


@content_api_bp.route('/permissions', methods=['POST'])
def add_permission():
    """添加用户权限"""
    result = check_admin_api()
    if result:
        return result
    
    try:
        data = request.json
        user_id = data.get('user_id')
        category_key = data.get('category_key')
        image_path = data.get('image_path')  # 可选，如果为空则表示整个类别
        
        if not user_id or not category_key:
            return jsonify({'success': False, 'message': '缺少必要字段'}), 400
        
        if category_key not in CATEGORY_MAP:
            return jsonify({'success': False, 'message': '无效的类别'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute('SELECT id FROM user_profile WHERE id = ?', (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 插入权限（如果image_path为None，表示整个类别）
        cursor.execute('''
            INSERT OR IGNORE INTO album_user_permission (user_id, category_key, image_path)
            VALUES (?, ?, ?)
        ''', (user_id, category_key, image_path))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '添加成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@content_api_bp.route('/permissions/<permission_id>', methods=['DELETE'])
def delete_permission(permission_id):
    """删除用户权限"""
    result = check_admin_api()
    if result:
        return result
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM album_user_permission WHERE id = ?', (permission_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@content_api_bp.route('/users', methods=['GET'])
def get_users():
    """获取所有用户列表（用于权限管理）"""
    result = check_admin_api()
    if result:
        return result
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email FROM user_profile ORDER BY username')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row['id'],
                'username': row['username'],
                'email': row['email']
            })
        
        conn.close()
        
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户列表失败: {str(e)}'}), 500
