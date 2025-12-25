from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')


@pages_bp.route('/register')
def register_page():
    """注册页面"""
    return render_template('register.html')


@pages_bp.route('/email-verification')
def email_verification_page():
    """邮箱验证页面"""
    return render_template('email_access.html')


@pages_bp.route('/alert')
def alert_page():
    """提醒页面"""
    return render_template('alert.html')

