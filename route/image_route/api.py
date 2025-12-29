# -*- coding: utf-8 -*-
"""
图片API路由
提供表情包相关功能
"""
from flask import Blueprint, request, jsonify, session
from tools.send_pics.emoji_manager import (
    load_emoji_database,
    get_emoji_info,
    get_emoji_url,
    find_matching_emojis
)
from tools.send_pics.send_pics import send_emoji_by_id

# 创建蓝图
image_api_bp = Blueprint('image_api', __name__)


@image_api_bp.route('/image', methods=['POST'])
def generate_image():
    """生成图片（画图功能，暂时返回占位）"""
    data = request.json
    prompt = data.get('prompt', '')
    
    # 这里可以集成图片生成 API
    # 暂时返回占位响应
    return jsonify({
        'message': '画图功能开发中',
        'prompt': prompt
    })


@image_api_bp.route('/emojis', methods=['GET'])
def get_emojis():
    """获取所有表情包列表"""
    try:
        database = load_emoji_database()
        # 只返回基本信息，不包含完整路径
        emojis = []
        for emoji in database:
            emojis.append({
                'id': emoji.get('id'),
                'category': emoji.get('category'),
                'description': emoji.get('description'),
                'url': get_emoji_url(emoji.get('id'))
            })
        return jsonify({
            'success': True,
            'emojis': emojis,
            'total': len(emojis)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@image_api_bp.route('/emoji/<emoji_id>', methods=['GET'])
def get_emoji(emoji_id):
    """根据ID获取表情包信息"""
    try:
        emoji_info = get_emoji_info(emoji_id)
        if not emoji_info:
            return jsonify({
                'success': False,
                'error': f'未找到ID为 {emoji_id} 的表情包'
            }), 404
        
        return jsonify({
            'success': True,
            'emoji': {
                'id': emoji_info.get('id'),
                'category': emoji_info.get('category'),
                'description': emoji_info.get('description'),
                'keywords': emoji_info.get('keywords', []),
                'url': get_emoji_url(emoji_id)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@image_api_bp.route('/emoji/match', methods=['POST'])
def match_emojis():
    """根据用户消息匹配表情包"""
    try:
        data = request.json
        user_message = data.get('message', '')
        threshold = data.get('threshold', 0.3)
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            }), 400
        
        matches = find_matching_emojis(user_message, threshold)
        
        result = []
        for match in matches:
            emoji = match['emoji']
            result.append({
                'id': emoji.get('id'),
                'category': emoji.get('category'),
                'description': emoji.get('description'),
                'url': get_emoji_url(emoji.get('id')),
                'score': match['score']
            })
        
        return jsonify({
            'success': True,
            'matches': result,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@image_api_bp.route('/emoji/send', methods=['POST'])
def send_emoji_route():
    """手动发送表情包（根据ID）"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({'error': '请先登录'}), 401
        
        data = request.json
        emoji_id = data.get('emoji_id')
        
        if not emoji_id:
            return jsonify({
                'success': False,
                'error': '表情包ID不能为空'
            }), 400
        
        result = send_emoji_by_id(emoji_id)
        
        if result.get('sent'):
            return jsonify({
                'success': True,
                'emoji': {
                    'id': result.get('emoji_id'),
                    'url': result.get('emoji_url'),
                    'category': result.get('category'),
                    'description': result.get('description')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '发送失败')
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

