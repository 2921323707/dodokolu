# -*- coding: utf-8 -*-
"""
Heaven 页面路由
"""
from flask import Blueprint, render_template

# 创建蓝图
heaven_pages_bp = Blueprint('heaven_pages', __name__)


@heaven_pages_bp.route('/movies')
def movies_index():
    """视频首页"""
    return render_template('heaven/movies/movies_index.html')

