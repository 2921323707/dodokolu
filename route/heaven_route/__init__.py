# -*- coding: utf-8 -*-
"""
Heaven 路由模块
提供视频展示功能
"""
from flask import Blueprint

# 创建蓝图
heaven_bp = Blueprint('heaven', __name__, url_prefix='/heaven')

# 导入路由（注册到蓝图）
from route.heaven_route import pages, api

