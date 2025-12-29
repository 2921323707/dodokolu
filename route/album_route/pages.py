# -*- coding: utf-8 -*-
"""
相册页面路由
"""
from flask import Blueprint, render_template

# 创建蓝图
album_pages_bp = Blueprint('album_pages', __name__)


@album_pages_bp.route('')
@album_pages_bp.route('/')
def album_index():
    """相册首页"""
    return render_template('album_show/album_index.html')


@album_pages_bp.route('/pic_expand')
def pic_expand():
    """图片展开详情页"""
    return render_template('album_show/album_pic_expand.html')

