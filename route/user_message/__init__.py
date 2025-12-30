# -*- coding: utf-8 -*-
"""
用户消息相关路由模块
"""
from flask import Blueprint
from .user_profile import user_profile_bp

# 创建主蓝图
user_message_bp = Blueprint('user_message', __name__)

# 注册所有子蓝图
user_message_bp.register_blueprint(user_profile_bp)

__all__ = ['user_message_bp']

