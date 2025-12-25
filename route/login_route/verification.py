from flask import Blueprint, request, jsonify
from components.email.email_sender import send_verification_code
import random
import string
import time
from threading import Lock

verification_bp = Blueprint('verification', __name__)

# 验证码存储（邮箱 -> {code, timestamp}）
verification_codes = {}
code_lock = Lock()
CODE_EXPIRE_TIME = 600  # 验证码有效期10分钟（秒）


@verification_bp.route('/api/send-verification-code', methods=['POST'])
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


@verification_bp.route('/api/verify-code', methods=['POST'])
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

