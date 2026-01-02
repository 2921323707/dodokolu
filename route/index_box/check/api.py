# -*- coding: utf-8 -*-
"""
打卡功能API路由
处理打卡截图识别和微信推送功能
"""
import os
import base64
from datetime import datetime, date
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from components.check.recognition import analyze_check_in_screenshot
from components.check.message_wechat_push import push_wechat_message
from database import get_db_connection

# 创建蓝图
check_api_bp = Blueprint('check_api', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in [ext.lstrip('.') for ext in ALLOWED_EXTENSIONS]


@check_api_bp.route('/check/analyze', methods=['POST'])
def analyze_check_in():
    """分析打卡截图"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
        # 检查文件是否存在
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空'
            }), 400
        
        # 验证文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'不支持的文件格式，仅支持: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # 读取文件并转换为 base64
        file_bytes = file.read()
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')
        
        # 根据文件扩展名确定 MIME 类型
        file_ext = os.path.splitext(file.filename)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(file_ext, 'image/jpeg')
        image_base64 = f"data:{mime_type};base64,{file_base64}"
        
        # 调用识别函数
        result = analyze_check_in_screenshot(image_base64=image_base64)
        
        # 如果识别成功，尝试更新打卡状态
        if result.get('success') and result.get('app_name') != 'unknown':
            try:
                # 内部调用更新状态函数
                user_id = session.get('user_id')
                if user_id:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    try:
                        # 查找匹配的清单项
                        app_name = result.get('app_name', 'unknown')
                        cursor.execute('''
                            SELECT id FROM check_list
                            WHERE user_id = ? AND app_name = ? AND is_active = 1
                            LIMIT 1
                        ''', (user_id, app_name))
                        
                        item = cursor.fetchone()
                        if item:
                            check_list_id = item['id']
                            today = date.today().isoformat()
                            check_in_status = result.get('check_in_status', 'unknown')
                            check_in_date = result.get('check_in_date', 'unknown')
                            details = result.get('details', '')
                            confidence = result.get('confidence', 'medium')
                            
                            # 判断打卡状态
                            if check_in_status == 'success':
                                status = 'completed'
                            elif check_in_status == 'failed':
                                status = 'failed'
                            else:
                                status = 'pending'
                            
                            # 插入或更新打卡记录
                            cursor.execute('''
                                INSERT OR REPLACE INTO check_record
                                (user_id, check_list_id, check_date, check_status, app_name, check_in_date, details, confidence)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (user_id, check_list_id, today, status, app_name, check_in_date, details, confidence))
                            
                            conn.commit()
                    finally:
                        conn.close()
            except Exception as e:
                # 更新状态失败不影响识别结果返回
                print(f"更新打卡状态失败: {str(e)}")
        
        return jsonify({
            'success': result.get('success', False),
            'data': {
                'app_name': result.get('app_name', 'unknown'),
                'check_in_status': result.get('check_in_status', 'unknown'),
                'check_in_date': result.get('check_in_date', 'unknown'),
                'details': result.get('details', ''),
                'confidence': result.get('confidence', 'medium')
            },
            'error': result.get('error', '') if not result.get('success') else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'分析失败: {str(e)}'
        }), 500


@check_api_bp.route('/check/push', methods=['POST'])
def push_message():
    """推送微信消息"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
        data = request.json
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title:
            return jsonify({
                'success': False,
                'error': '标题不能为空'
            }), 400
        
        if not content:
            return jsonify({
                'success': False,
                'error': '内容不能为空'
            }), 400
        
        # 调用推送函数
        result = push_wechat_message(title=title, content=content)
        
        return jsonify({
            'success': result.get('success', False),
            'error_code': result.get('error_code', -1),
            'error_message': result.get('error_message', '未知错误')
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'推送失败: {str(e)}'
        }), 500


@check_api_bp.route('/check/list', methods=['GET'])
def get_check_list():
    """获取用户的打卡清单（包含今日打卡状态）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 获取今日日期
            today = date.today().isoformat()
            
            # 获取用户的打卡清单
            cursor.execute('''
                SELECT id, app_name, is_active, created_at, updated_at
                FROM check_list
                WHERE user_id = ? AND is_active = 1
                ORDER BY created_at ASC
            ''', (user_id,))
            
            items = []
            for row in cursor.fetchall():
                item_id = row['id']
                app_name = row['app_name']
                
                # 查询今日打卡状态
                cursor.execute('''
                    SELECT check_status, check_in_date, details, confidence
                    FROM check_record
                    WHERE user_id = ? AND check_list_id = ? AND check_date = ?
                ''', (user_id, item_id, today))
                
                record = cursor.fetchone()
                status = record['check_status'] if record else 'pending'
                check_in_date = record['check_in_date'] if record else None
                details = record['details'] if record else None
                confidence = record['confidence'] if record else None
                
                items.append({
                    'id': item_id,
                    'app_name': app_name,
                    'status': status,
                    'check_in_date': check_in_date,
                    'details': details,
                    'confidence': confidence,
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            return jsonify({
                'success': True,
                'data': items
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取清单失败: {str(e)}'
        }), 500


@check_api_bp.route('/check/list', methods=['POST'])
def create_check_item():
    """创建打卡清单项"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
        data = request.json
        app_name = data.get('app_name', '').strip()
        
        if not app_name:
            return jsonify({
                'success': False,
                'error': '应用名称不能为空'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在相同的应用名称
            cursor.execute('''
                SELECT id FROM check_list
                WHERE user_id = ? AND app_name = ? AND is_active = 1
            ''', (user_id, app_name))
            
            if cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': '该应用已存在于清单中'
                }), 400
            
            # 创建新项
            cursor.execute('''
                INSERT INTO check_list (user_id, app_name, is_active)
                VALUES (?, ?, 1)
            ''', (user_id, app_name))
            
            item_id = cursor.lastrowid
            conn.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'id': item_id,
                    'app_name': app_name,
                    'status': 'pending'
                }
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'创建失败: {str(e)}'
        }), 500


@check_api_bp.route('/check/list/<int:item_id>', methods=['PUT'])
def update_check_item(item_id):
    """更新打卡清单项"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
        data = request.json
        app_name = data.get('app_name', '').strip()
        
        if not app_name:
            return jsonify({
                'success': False,
                'error': '应用名称不能为空'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 检查项是否存在且属于当前用户
            cursor.execute('''
                SELECT id FROM check_list
                WHERE id = ? AND user_id = ?
            ''', (item_id, user_id))
            
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': '清单项不存在'
                }), 404
            
            # 检查新名称是否与其他项冲突
            cursor.execute('''
                SELECT id FROM check_list
                WHERE user_id = ? AND app_name = ? AND is_active = 1 AND id != ?
            ''', (user_id, app_name, item_id))
            
            if cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': '该应用名称已存在'
                }), 400
            
            # 更新项
            cursor.execute('''
                UPDATE check_list
                SET app_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (app_name, item_id, user_id))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'id': item_id,
                    'app_name': app_name
                }
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新失败: {str(e)}'
        }), 500


@check_api_bp.route('/check/list/<int:item_id>', methods=['DELETE'])
def delete_check_item(item_id):
    """删除打卡清单项（软删除）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 检查项是否存在且属于当前用户
            cursor.execute('''
                SELECT id FROM check_list
                WHERE id = ? AND user_id = ?
            ''', (item_id, user_id))
            
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'error': '清单项不存在'
                }), 404
            
            # 软删除（设置is_active=0）
            cursor.execute('''
                UPDATE check_list
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (item_id, user_id))
            
            conn.commit()
            
            return jsonify({
                'success': True
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }), 500


@check_api_bp.route('/check/update-status', methods=['POST'])
def update_check_status():
    """更新打卡状态（识别成功后调用）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
        data = request.json
        app_name = data.get('app_name', '').strip()
        check_in_status = data.get('check_in_status', 'unknown')
        check_in_date = data.get('check_in_date', 'unknown')
        details = data.get('details', '')
        confidence = data.get('confidence', 'medium')
        
        if not app_name or app_name == 'unknown':
            return jsonify({
                'success': False,
                'error': '应用名称无效'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 查找匹配的清单项
            cursor.execute('''
                SELECT id FROM check_list
                WHERE user_id = ? AND app_name = ? AND is_active = 1
                LIMIT 1
            ''', (user_id, app_name))
            
            item = cursor.fetchone()
            if not item:
                return jsonify({
                    'success': False,
                    'error': '未找到匹配的打卡清单项'
                }), 404
            
            check_list_id = item['id']
            today = date.today().isoformat()
            
            # 判断打卡状态
            if check_in_status == 'success':
                status = 'completed'
            elif check_in_status == 'failed':
                status = 'failed'
            else:
                status = 'pending'
            
            # 插入或更新打卡记录
            cursor.execute('''
                INSERT OR REPLACE INTO check_record
                (user_id, check_list_id, check_date, check_status, app_name, check_in_date, details, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, check_list_id, today, status, app_name, check_in_date, details, confidence))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'check_list_id': check_list_id,
                    'status': status
                }
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新状态失败: {str(e)}'
        }), 500

