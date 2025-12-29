# -*- coding: utf-8 -*-
"""
Heaven 路由模块
提供视频展示功能
"""
from flask import Blueprint
from .pages import heaven_pages_bp
from .api import heaven_api_bp

# 创建主蓝图
heaven_bp = Blueprint('heaven', __name__, url_prefix='/heaven')

# 注册所有子蓝图
heaven_bp.register_blueprint(heaven_pages_bp)
heaven_bp.register_blueprint(heaven_api_bp)

__all__ = ['heaven_bp']

