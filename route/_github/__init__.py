# -*- coding: utf-8 -*-
"""
GitHub API 路由模块
提供获取仓库最近一次提交信息的功能
"""
from flask import Blueprint
from .api import github_api_bp

# 创建主蓝图
github_bp = Blueprint('github', __name__, url_prefix='/api/github')

# 注册子蓝图
github_bp.register_blueprint(github_api_bp)

__all__ = ['github_bp']

