# -*- coding: utf-8 -*-
"""
相册路由模块
提供相册展示功能
"""
from flask import Blueprint
from .pages import album_pages_bp
from .api import album_api_bp

# 创建主蓝图
album_bp = Blueprint('album', __name__, url_prefix='/album')

# 注册所有子蓝图
album_bp.register_blueprint(album_pages_bp)
album_bp.register_blueprint(album_api_bp)

__all__ = ['album_bp']

