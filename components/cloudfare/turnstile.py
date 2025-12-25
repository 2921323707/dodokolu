# -*- coding: utf-8 -*-
"""
Cloudflare Turnstile 人机验证组件
"""
import os
import requests
from typing import Optional, Dict


def verify_turnstile_token(token: str, remote_ip: Optional[str] = None) -> Dict[str, any]:
    """
    验证 Cloudflare Turnstile token
    
    Args:
        token: 前端返回的 Turnstile token
        remote_ip: 用户的 IP 地址（可选，但推荐使用以提高安全性）
    
    Returns:
        dict: {
            'success': bool,  # 验证是否成功
            'error_codes': list,  # 错误代码列表（如果有）
            'challenge_ts': str,  # 挑战时间戳
            'hostname': str  # 主机名
        }
    """
    secret_key = os.getenv('CLOUDFLARE_TURNSTILE_SECRET_KEY')
    
    if not secret_key:
        return {
            'success': False,
            'error_codes': ['missing-secret'],
            'message': 'Cloudflare Turnstile secret key not configured'
        }
    
    if not token:
        return {
            'success': False,
            'error_codes': ['missing-input-response'],
            'message': 'Token is required'
        }
    
    # 准备验证请求数据
    data = {
        'secret': secret_key,
        'response': token
    }
    
    if remote_ip:
        data['remoteip'] = remote_ip
    
    try:
        # 发送验证请求到 Cloudflare
        response = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data=data,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            'success': result.get('success', False),
            'error_codes': result.get('error-codes', []),
            'challenge_ts': result.get('challenge_ts'),
            'hostname': result.get('hostname')
        }
    except requests.RequestException as e:
        return {
            'success': False,
            'error_codes': ['network-error'],
            'message': f'Network error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error_codes': ['internal-error'],
            'message': f'Internal error: {str(e)}'
        }


def get_turnstile_site_key() -> Optional[str]:
    """
    获取 Cloudflare Turnstile 站点密钥（用于前端）
    
    Returns:
        str: 站点密钥，如果未配置则返回 None
    """
    return os.getenv('CLOUDFLARE_TURNSTILE_SITE_KEY')

