# -*- coding: utf-8 -*-
"""
Heaven 页面路由
"""
from flask import render_template
from route.heaven_route import heaven_bp


@heaven_bp.route('/movies')
def movies_index():
    """视频首页"""
    return render_template('heaven/movies/movies_index.html')

