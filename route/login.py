from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from components.email.email_sender import send_verification_code, send_email
from database import get_db_connection
from route.config.llm.history import create_history_file
import random
import string
import time
import sqlite3
from threading import Lock
from datetime import datetime

login_bp = Blueprint('login', __name__)

# 验证码存储（邮箱 -> {code, timestamp}）
verification_codes = {}
code_lock = Lock()
CODE_EXPIRE_TIME = 600  # 验证码有效期10分钟（秒）


@login_bp.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')


@login_bp.route('/register')
def register_page():
    """注册页面"""
    return render_template('register.html')


@login_bp.route('/email-verification')
def email_verification_page():
    """邮箱验证页面"""
    return render_template('email_access.html')


@login_bp.route('/alert')
def alert_page():
    """提醒页面"""
    return render_template('alert.html')

@login_bp.route('/feedback')
def feedback_page():
    """反馈页面"""
    return render_template('feedback.html')


@login_bp.route('/api/feedback', methods=['POST'])
def feedback_api():
    """反馈提交API"""
    try:
        # 验证登录状态
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录', 'require_login': True}), 401
        
        data = request.json
        feedback_content = data.get('content', '').strip()
        feedback_contact = data.get('contact', '').strip()
        
        if not feedback_content:
            return jsonify({'success': False, 'message': '反馈内容不能为空'}), 400
        
        # 获取用户信息
        username = session.get('username', '')
        user_email = session.get('email', '')
        
        # 构建HTML邮件内容
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>用户反馈</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #fff5f7;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 8px rgba(255, 105, 180, 0.15);
                }}
                .header {{
                    border-bottom: 3px solid #ff69b4;
                    padding-bottom: 15px;
                    margin-bottom: 25px;
                }}
                .header h1 {{
                    color: #ff69b4;
                    margin: 0;
                    font-size: 24px;
                }}
                .info-section {{
                    background-color: #ffe4e1;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                }}
                .info-row {{
                    margin-bottom: 10px;
                    display: flex;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #c2185b;
                    min-width: 100px;
                }}
                .info-value {{
                    color: #1e293b;
                }}
                .content-section {{
                    margin-top: 25px;
                }}
                .content-label {{
                    font-weight: 600;
                    color: #c2185b;
                    margin-bottom: 10px;
                    display: block;
                }}
                .content-text {{
                    background-color: #ffe4e1;
                    padding: 15px;
                    border-radius: 6px;
                    border-left: 4px solid #ff69b4;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    line-height: 1.8;
                    color: #1e293b;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ffc0cb;
                    text-align: center;
                    color: #d4a5b8;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>用户反馈</h1>
                </div>
                
                <div class="info-section">
                    <div class="info-row">
                        <span class="info-label">提交时间：</span>
                        <span class="info-value">{current_time}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">提交用户：</span>
                        <span class="info-value">{username}</span>
                    </div>
                    {f'<div class="info-row"><span class="info-label">用户邮箱：</span><span class="info-value">{user_email}</span></div>' if user_email else ''}
                    {f'<div class="info-row"><span class="info-label">联系方式：</span><span class="info-value">{feedback_contact}</span></div>' if feedback_contact else ''}
                </div>
                
                <div class="content-section">
                    <span class="content-label">反馈内容：</span>
                    <div class="content-text">{feedback_content}</div>
                </div>
                
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿直接回复。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 发送邮件到指定邮箱
        recipient_email = '2921323707@qq.com'
        subject = f'用户反馈 - {username}'
        
        try:
            send_email(recipient_email, subject, html_content, 'html')
            return jsonify({'success': True, 'message': '反馈提交成功'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'发送邮件失败: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'处理反馈失败: {str(e)}'}), 500

@login_bp.route('/account')
def account_page():
    """账户页面"""
    if 'user_id' not in session:
        return redirect(url_for('login.login_page'))
    return render_template('account.html')


@login_bp.route('/api/account/profile', methods=['GET'])
def account_profile():
    """返回当前用户的完整资料（不含敏感字段）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''
            SELECT id, username, email, created_at
            FROM user_profile
            WHERE id = ?
            ''',
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 仅返回必要字段，避免暴露密码
        profile = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at']
        }
        return jsonify({'success': True, 'data': profile})
    finally:
        conn.close()


@login_bp.route('/api/account/apply-creator', methods=['POST'])
def apply_creator():
    """通过邀请码申请创作者 / 管理员"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401

    data = request.json or {}
    invite_code = str(data.get('invite_code', '')).strip()

    code_role_map = {
        '888888': 1,  # 朋友 / 创作者
        '999999': 2   # 管理员
    }

    if invite_code not in code_role_map:
        return jsonify({'success': False, 'message': '邀请码无效'}), 400

    new_role = code_role_map[invite_code]

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE user_profile SET role = ? WHERE id = ?', (new_role, user_id))
        conn.commit()
        session['role'] = new_role
        role_label = '创作者' if new_role == 1 else '管理员' if new_role == 2 else '用户'
        return jsonify({'success': True, 'message': f'身份已更新为：{role_label}', 'role': new_role, 'role_label': role_label})
    finally:
        conn.close()


@login_bp.route('/api/auth-status', methods=['GET'])
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


@login_bp.route('/api/send-verification-code', methods=['POST'])
def send_verification_code_api():
    """发送验证码API"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        # 生成6位数字验证码
        code = ''.join(random.choices(string.digits, k=6))
        
        # 存储验证码（带时间戳）
        with code_lock:
            verification_codes[email] = {
                'code': code,
                'timestamp': time.time()
            }
        
        # 发送验证码邮件
        try:
            send_verification_code(email, code)
            return jsonify({'success': True, 'message': 'Verification code sent successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Failed to send email: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@login_bp.route('/api/verify-code', methods=['POST'])
def verify_code_api():
    """验证验证码API"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        code = data.get('code', '').strip()
        
        if not email or not code:
            return jsonify({'success': False, 'message': 'Email and code are required'}), 400
        
        with code_lock:
            if email not in verification_codes:
                return jsonify({'success': False, 'message': 'Verification code not found or expired'}), 400
            
            stored_data = verification_codes[email]
            stored_code = stored_data['code']
            timestamp = stored_data['timestamp']
            
            # 检查验证码是否过期
            if time.time() - timestamp > CODE_EXPIRE_TIME:
                del verification_codes[email]
                return jsonify({'success': False, 'message': 'Verification code has expired'}), 400
            
            # 验证验证码
            if code == stored_code:
                # 验证成功，删除验证码
                del verification_codes[email]
                return jsonify({'success': True, 'message': 'Verification successful'})
            else:
                return jsonify({'success': False, 'message': 'Invalid verification code'}), 400
                
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@login_bp.route('/api/register', methods=['POST'])
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


@login_bp.route('/api/login', methods=['POST'])
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


