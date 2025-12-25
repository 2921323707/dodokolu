from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from database import get_db_connection

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

