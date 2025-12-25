# -*- coding: utf-8 -*-
"""
相册路由模块
提供相册展示功能
"""
from flask import Blueprint

# 创建蓝图
album_bp = Blueprint('album', __name__, url_prefix='/album')

# 导入路由（注册到蓝图）
from route.album_route import pages, api

