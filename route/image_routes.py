# -*- coding: utf-8 -*-
"""
图片生成相关路由
"""
from flask import Blueprint, request, jsonify

# 创建蓝图
image_bp = Blueprint('image', __name__, url_prefix='/api')


@image_bp.route('/image', methods=['POST'])
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

