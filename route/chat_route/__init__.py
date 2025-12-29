# -*- coding: utf-8 -*-
"""
聊天路由模块
提供聊天、历史记录、上传、生成等功能
"""
from flask import Blueprint
from .api import chat_api_bp
from .upload_api import upload_api_bp
from .generation_api import generation_api_bp
from .tts_api import tts_api_bp

# 创建主蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api')

# 注册所有子蓝图
chat_bp.register_blueprint(chat_api_bp)
chat_bp.register_blueprint(upload_api_bp)
chat_bp.register_blueprint(generation_api_bp)
chat_bp.register_blueprint(tts_api_bp)

__all__ = ['chat_bp']

