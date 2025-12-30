from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from database import get_db_connection
from components.cloudfare.turnstile import verify_turnstile_token, get_turnstile_site_key
import os

account_bp = Blueprint('account', __name__)


@account_bp.route('/account')
def account_page():
    """账户页面"""
    if 'user_id' not in session:
        return redirect(url_for('login.pages.login_page'))
    return render_template('account.html')


@account_bp.route('/api/account/profile', methods=['GET'])
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


@account_bp.route('/api/account/apply-creator', methods=['POST'])
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


@account_bp.route('/api/account/logout', methods=['POST'])
def logout():
    """退出登录"""
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录'})


@account_bp.route('/api/account/change-password', methods=['POST'])
def change_password():
    """修改密码（需要登录）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json or {}
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    
    if not old_password or not new_password:
        return jsonify({'success': False, 'message': '旧密码和新密码不能为空'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度至少6位'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 验证旧密码
        cursor.execute('SELECT password FROM user_profile WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 验证密码（暂时明文比较）
        if user['password'] != old_password:
            return jsonify({'success': False, 'message': '旧密码错误'}), 401
        
        # 更新密码
        cursor.execute('UPDATE user_profile SET password = ? WHERE id = ?', (new_password, user_id))
        conn.commit()
        
        return jsonify({'success': True, 'message': '密码修改成功'})
    finally:
        conn.close()


@account_bp.route('/api/account/change-password-by-username', methods=['POST'])
def change_password_by_username():
    """通过用户名修改密码（不需要登录）"""
    data = request.json or {}
    username = data.get('username', '').strip()
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    
    if not username or not old_password or not new_password:
        return jsonify({'success': False, 'message': '用户名、旧密码和新密码不能为空'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度至少6位'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 验证用户名和旧密码
        cursor.execute('SELECT id, password FROM user_profile WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': '用户名不存在'}), 404
        
        # 验证密码（暂时明文比较）
        if user['password'] != old_password:
            return jsonify({'success': False, 'message': '旧密码错误'}), 401
        
        # 更新密码
        cursor.execute('UPDATE user_profile SET password = ? WHERE id = ?', (new_password, user['id']))
        conn.commit()
        
        return jsonify({'success': True, 'message': '密码修改成功'})
    finally:
        conn.close()


@account_bp.route('/api/account/verify-admin', methods=['POST'])
def verify_admin():
    """验证管理员身份（Turnstile 验证为可选，如果未配置则跳过）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json or {}
    turnstile_token = data.get('turnstile_token', '').strip()
    
    # 如果配置了 Turnstile，则进行验证；否则跳过
    secret_key = os.getenv('CLOUDFLARE_TURNSTILE_SECRET_KEY')  # 检查是否配置了 Turnstile
    if secret_key and turnstile_token:
        # 验证 Turnstile token
        remote_ip = request.remote_addr
        turnstile_result = verify_turnstile_token(turnstile_token, remote_ip)
        
        if not turnstile_result.get('success'):
            error_codes = turnstile_result.get('error_codes', [])
            return jsonify({
                'success': False,
                'message': '人机验证失败',
                'error_codes': error_codes
            }), 400
    elif secret_key and not turnstile_token:
        # 配置了 Turnstile 但没有提供 token
        return jsonify({'success': False, 'message': '人机验证token缺失'}), 400
    
    # 验证管理员身份
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT role FROM user_profile WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # role 为 2 表示管理员
        if user['role'] != 2:
            return jsonify({'success': False, 'message': '您不是管理员，无权限访问'}), 403
        
        return jsonify({'success': True, 'message': '管理员验证通过'})
    finally:
        conn.close()


@account_bp.route('/api/account/turnstile-site-key', methods=['GET'])
def get_turnstile_site_key_api():
    """获取 Turnstile 站点密钥（用于前端渲染）"""
    site_key = get_turnstile_site_key()
    # 如果未配置，返回空字符串，前端会跳过 Turnstile 验证
    return jsonify({'success': True, 'site_key': site_key or ''})


@account_bp.route('/api/account/password', methods=['GET'])
def get_password():
    """获取当前用户的密码（用于密码预览）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT password FROM user_profile WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        return jsonify({'success': True, 'password': user['password']})
    finally:
        conn.close()
