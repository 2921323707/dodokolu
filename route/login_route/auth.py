from flask import Blueprint, request, jsonify, session
from database import get_db_connection
from route.config.llm.history import create_history_file
import sqlite3

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['POST'])
def login_api():
    """登录API"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        # 从数据库查询用户
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, password, email, role
                FROM user_profile 
                WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
            
            # 验证密码（暂时明文比较）
            if user['password'] != password:
                return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
            
            # 登录成功，设置session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            # 清除旧的会话文件，让系统自动加载最新的历史记录
            if 'current_history_file' in session:
                del session['current_history_file']
            
            return jsonify({
                'success': True, 
                'message': '登录成功',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500


@auth_bp.route('/api/register', methods=['POST'])
def register_api():
    """注册API：写入用户画像表"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not email or not password:
            return jsonify({'success': False, 'message': '用户名、邮箱和密码不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 检查是否已存在
            cursor.execute('''
                SELECT id FROM user_profile 
                WHERE username = ? OR email = ?
            ''', (username, email))
            exist = cursor.fetchone()
            if exist:
                return jsonify({'success': False, 'message': '用户名或邮箱已存在'}), 409
            
            # 插入用户
            cursor.execute('''
                INSERT INTO user_profile (username, password, email, role)
                VALUES (?, ?, ?, ?)
            ''', (username, password, email, 0))
            conn.commit()
            
            # 创建用户的历史记录文件
            try:
                create_history_file(email)
            except Exception as e:
                print(f'创建历史记录文件失败: {e}')
                # 不影响注册流程，仅记录错误
            
            return jsonify({'success': True, 'message': '注册成功'})
        except sqlite3.IntegrityError:
            conn.rollback()
            return jsonify({'success': False, 'message': '用户名或邮箱已存在'}), 409
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500


@auth_bp.route('/api/auth-status', methods=['GET'])
def auth_status():
    """获取当前登录状态"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': True, 'logged_in': False})
    
    # 确保会话中有角色信息
    role = session.get('role')
    if role is None:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT role FROM user_profile WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            role = user['role'] if user else 0
            session['role'] = role
        finally:
            conn.close()
    return jsonify({
        'success': True,
        'logged_in': True,
        'user': {
            'id': user_id,
            'username': session.get('username'),
            'email': session.get('email'),
            'role': role
        }
    })

