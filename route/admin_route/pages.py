# -*- coding: utf-8 -*-
"""
管理员页面路由
"""
from flask import Blueprint, render_template, session, redirect, url_for

admin_pages_bp = Blueprint('pages', __name__)


def check_admin():
    """检查管理员权限"""
    if 'user_id' not in session:
        return redirect(url_for('login.pages.login_page'))
    
    if session.get('role') != 2:
        return redirect(url_for('login.account.account_page'))
    
    return None


@admin_pages_bp.route('')
@admin_pages_bp.route('/')
def admin_index():
    """管理员首页"""
    result = check_admin()
    if result:
        return result
    return render_template('admin/admin_index.html')


@admin_pages_bp.route('/database')
def admin_database():
    """数据库管理页面"""
    result = check_admin()
    if result:
        return result
    return render_template('admin/admin_database.html')
