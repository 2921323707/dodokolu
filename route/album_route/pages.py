# -*- coding: utf-8 -*-
"""
相册页面路由
"""
from flask import render_template
from route.album_route import album_bp


@album_bp.route('')
@album_bp.route('/')
def album_index():
    """相册首页"""
    return render_template('album_show/album_index.html')


@album_bp.route('/pic_expand')
def pic_expand():
    """图片展开详情页"""
    return render_template('album_show/album_pic_expand.html')

