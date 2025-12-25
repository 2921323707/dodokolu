# -*- coding: utf-8 -*-
"""
管理员路由模块
"""
from flask import Blueprint
from .pages import admin_pages_bp
from .api import admin_api_bp
from .content_api import content_api_bp

# 创建主蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 注册所有子蓝图
admin_bp.register_blueprint(admin_pages_bp)
admin_bp.register_blueprint(admin_api_bp)
admin_bp.register_blueprint(content_api_bp)

__all__ = ['admin_bp']
