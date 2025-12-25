from flask import Blueprint
from .auth import auth_bp
from .verification import verification_bp
from .account import account_bp
from .feedback import feedback_bp
from .pages import pages_bp

# 创建主蓝图
login_bp = Blueprint('login', __name__)

# 注册所有子蓝图
login_bp.register_blueprint(auth_bp)
login_bp.register_blueprint(verification_bp)
login_bp.register_blueprint(account_bp)
login_bp.register_blueprint(feedback_bp)
login_bp.register_blueprint(pages_bp)

__all__ = ['login_bp']

