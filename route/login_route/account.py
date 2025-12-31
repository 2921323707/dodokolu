from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from database import get_db_connection
from components.cloudfare.turnstile import verify_turnstile_token, get_turnstile_site_key
from components.gd_location import reverse_geocode
import os
import json

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


@account_bp.route('/api/account/agents', methods=['GET'])
def get_agents():
    """获取所有智能体实例及其详细信息（包括模型信息）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    try:
        from config.llm.base.registry import list_agents, AGENT_REGISTRY
        from config.llm.agent_config import get_all_agent_status
        from config.llm.base.settings import DEEPSEEK_MODEL, MINIMAX_MODEL
        
        # 获取所有智能体信息
        agents_info = list_agents()
        # 获取所有智能体状态
        agents_status = get_all_agent_status()
        
        # 过滤掉向后兼容的别名，只显示主要智能体
        # 主要智能体：suheyao, mimico, lumina
        # 向后兼容别名：normal, default（这些是 suheyao 的别名，应该被过滤）
        main_agents = {'suheyao', 'mimico', 'lumina'}
        
        # 构建智能体列表
        agents_list = []
        for agent_name, agent_info in agents_info.items():
            # 跳过向后兼容的别名
            if agent_name not in main_agents:
                continue
            # 获取智能体实例以获取模型信息
            agent_instance = AGENT_REGISTRY.get(agent_name)
            model_name = '未知'
            
            # 根据智能体名称确定模型
            if agent_name == 'suheyao':
                model_name = DEEPSEEK_MODEL or 'deepseek-chat'
            elif agent_name == 'mimico':
                model_name = MINIMAX_MODEL or 'MiniMax-M2.1'
            elif agent_instance and hasattr(agent_instance, '_model'):
                model_name = agent_instance._model
            
            # 获取在线状态
            is_online = agents_status.get(agent_name, True)
            
            agents_list.append({
                'name': agent_info.get('name', agent_name),
                'description': agent_info.get('description', ''),
                'model': model_name,
                'is_online': is_online,
                'status': '在线' if is_online else '离线',
                'key': agent_name  # 内部使用的key
            })
        
        return jsonify({
            'success': True,
            'agents': agents_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取智能体列表失败: {str(e)}'
        }), 500


@account_bp.route('/api/account/chat-history/files', methods=['GET'])
def get_chat_history_files():
    """获取当前用户的所有聊天历史文件列表"""
    user_id = session.get('user_id')
    user_email = session.get('email')
    if not user_id or not user_email:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    try:
        from pathlib import Path
        from config.llm.base.history import HISTORY_DIR
        
        # 将邮箱转换为安全格式
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        user_dir = HISTORY_DIR / safe_email
        
        if not user_dir.exists():
            return jsonify({
                'success': True,
                'files': []
            })
        
        # 获取所有 JSON 文件
        json_files = list(user_dir.glob('*.json'))
        files_list = []
        
        for file_path in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                # 读取文件以获取基本信息
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    message_count = len(content) if isinstance(content, list) else 0
                
                # 获取文件修改时间
                mtime = file_path.stat().st_mtime
                from datetime import datetime
                modified_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                files_list.append({
                    'filename': file_path.name,
                    'message_count': message_count,
                    'modified_time': modified_time,
                    'size': file_path.stat().st_size
                })
            except Exception as e:
                # 跳过无法读取的文件
                continue
        
        return jsonify({
            'success': True,
            'files': files_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取聊天记录文件列表失败: {str(e)}'
        }), 500


@account_bp.route('/api/account/chat-history/content', methods=['GET'])
def get_chat_history_content():
    """获取指定聊天历史文件的内容"""
    user_id = session.get('user_id')
    user_email = session.get('email')
    if not user_id or not user_email:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'success': False, 'message': '文件名不能为空'}), 400
    
    try:
        from pathlib import Path
        from config.llm.base.history import HISTORY_DIR
        import os
        
        # 将邮箱转换为安全格式
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        user_dir = HISTORY_DIR / safe_email
        
        # 安全检查：确保文件名不包含路径分隔符
        if os.path.sep in filename or os.path.altsep and os.path.altsep in filename:
            return jsonify({'success': False, 'message': '无效的文件名'}), 400
        
        file_path = user_dir / filename
        
        if not file_path.exists():
            return jsonify({'success': False, 'message': '文件不存在'}), 404
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': filename
        })
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'message': '文件格式错误，无法解析 JSON'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'读取聊天记录失败: {str(e)}'
        }), 500


@account_bp.route('/api/account/location', methods=['POST'])
def get_location_info():
    """根据经纬度获取格式化地址信息"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.json or {}
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    
    if longitude is None or latitude is None:
        return jsonify({'success': False, 'message': '经纬度参数缺失'}), 400
    
    try:
        # 调用逆地理编码API
        result = reverse_geocode(float(longitude), float(latitude))
        
        if result.get('status') == '1' and result.get('regeocode'):
            regeocode = result['regeocode']
            address_component = regeocode.get('addressComponent', {})
            
            # 构建格式化地址信息
            formatted_address = regeocode.get('formatted_address', '')
            
            # 构建详细地址组件
            province = address_component.get('province', '')
            city = address_component.get('city', '')
            district = address_component.get('district', '')
            township = address_component.get('township', '')
            
            # 拼接地址字符串（去掉空的层级）
            address_parts = [province, city, district, township]
            address_parts = [part for part in address_parts if part]
            location_text = ' '.join(address_parts) if address_parts else formatted_address
            
            return jsonify({
                'success': True,
                'data': {
                    'formatted_address': formatted_address,
                    'location': location_text,
                    'province': province,
                    'city': city,
                    'district': district,
                    'township': township
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('info', '获取位置信息失败')
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取位置信息失败: {str(e)}'
        }), 500