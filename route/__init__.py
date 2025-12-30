# -*- coding: utf-8 -*-
"""
路由模块统一导出
所有蓝图在此统一导出，方便主应用使用
"""
from route.chat_route import chat_bp
from route.image_route import image_bp
from route.login_route import login_bp
from route.alert.alert import alert_bp
from route.album_route import album_bp
from route.admin_route import admin_bp
from route.heaven_route import heaven_bp
from route.user_message import user_message_bp
from route._github import github_bp

__all__ = [
    'chat_bp',
    'image_bp',
    'login_bp',
    'alert_bp',
    'album_bp',
    'admin_bp',
    'heaven_bp',
    'user_message_bp',
    'github_bp'
]
