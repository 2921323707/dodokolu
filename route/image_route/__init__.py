# -*- coding: utf-8 -*-
"""
图片路由模块
提供表情包相关功能
"""
from flask import Blueprint
from .api import image_api_bp

# 创建主蓝图
image_bp = Blueprint('image', __name__, url_prefix='/api')

# 注册所有子蓝图
image_bp.register_blueprint(image_api_bp)

__all__ = ['image_bp']

