# -*- coding: utf-8 -*-
"""
GitHub API 路由
处理获取仓库最近一次提交的时间和 commit 备注
"""
import os
import requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# GitHub API 配置
GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN', '')  # 可选，用于提高速率限制
GITHUB_API_BASE_URL = 'https://api.github.com'

# 创建蓝图
github_api_bp = Blueprint('github_api', __name__)


def get_github_headers():
    """获取 GitHub API 请求头"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'dodokoru-app'
    }
    if GITHUB_API_TOKEN:
        headers['Authorization'] = f'token {GITHUB_API_TOKEN}'
    return headers


@github_api_bp.route('/latest-commit', methods=['GET'])
def get_latest_commit():
    """
    获取仓库最近一次提交的时间和 commit 备注
    
    查询参数:
        owner: 仓库所有者（必需）
        repo: 仓库名称（必需）
        branch: 分支名称（可选，默认为默认分支）
    
    返回:
        {
            "success": true,
            "data": {
                "sha": "commit hash",
                "message": "commit message",
                "author": {
                    "name": "author name",
                    "email": "author email"
                },
                "date": "2024-01-01T00:00:00Z",
                "url": "commit url"
            }
        }
    """
    try:
        # 获取查询参数
        owner = request.args.get('owner')
        repo = request.args.get('repo')
        branch = request.args.get('branch', None)
        
        # 验证必需参数
        if not owner or not repo:
            return jsonify({
                'success': False,
                'error': '缺少必需参数：owner 和 repo'
            }), 400
        
        # 构建 API 端点
        if branch:
            # 获取指定分支的最新提交
            url = f'{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/commits/{branch}'
        else:
            # 获取默认分支的最新提交
            url = f'{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/commits'
        
        # 发送请求
        headers = get_github_headers()
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        if response.status_code == 404:
            return jsonify({
                'success': False,
                'error': '仓库不存在或无权访问'
            }), 404
        
        if response.status_code == 403:
            return jsonify({
                'success': False,
                'error': 'API 速率限制已超，请稍后再试或配置 GITHUB_API_TOKEN'
            }), 403
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'GitHub API 请求失败: {response.status_code}'
            }), response.status_code
        
        # 解析响应
        if branch:
            # 单个提交对象
            commit_data = response.json()
        else:
            # 提交列表，取第一个
            commits = response.json()
            if not commits or len(commits) == 0:
                return jsonify({
                    'success': False,
                    'error': '仓库没有提交记录'
                }), 404
            commit_data = commits[0]
        
        # 提取所需信息
        commit_info = {
            'sha': commit_data.get('sha', ''),
            'message': commit_data.get('commit', {}).get('message', ''),
            'author': {
                'name': commit_data.get('commit', {}).get('author', {}).get('name', ''),
                'email': commit_data.get('commit', {}).get('author', {}).get('email', '')
            },
            'date': commit_data.get('commit', {}).get('author', {}).get('date', ''),
            'url': commit_data.get('html_url', '')
        }
        
        return jsonify({
            'success': True,
            'data': commit_info
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': '请求超时，请稍后再试'
        }), 504
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'网络请求失败: {str(e)}'
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@github_api_bp.route('/commits', methods=['GET'])
def get_commits():
    """
    获取仓库的提交列表（可选功能）
    
    查询参数:
        owner: 仓库所有者（必需）
        repo: 仓库名称（必需）
        branch: 分支名称（可选）
        per_page: 每页数量（可选，默认1，最多100）
        page: 页码（可选，默认1）
    """
    try:
        owner = request.args.get('owner')
        repo = request.args.get('repo')
        branch = request.args.get('branch', None)
        per_page = min(int(request.args.get('per_page', 1)), 100)
        page = int(request.args.get('page', 1))
        
        if not owner or not repo:
            return jsonify({
                'success': False,
                'error': '缺少必需参数：owner 和 repo'
            }), 400
        
        # 构建 API 端点
        url = f'{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/commits'
        params = {
            'per_page': per_page,
            'page': page
        }
        if branch:
            params['sha'] = branch
        
        headers = get_github_headers()
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'GitHub API 请求失败: {response.status_code}'
            }), response.status_code
        
        commits = response.json()
        commit_list = []
        
        for commit_data in commits:
            commit_info = {
                'sha': commit_data.get('sha', ''),
                'message': commit_data.get('commit', {}).get('message', ''),
                'author': {
                    'name': commit_data.get('commit', {}).get('author', {}).get('name', ''),
                    'email': commit_data.get('commit', {}).get('author', {}).get('email', '')
                },
                'date': commit_data.get('commit', {}).get('author', {}).get('date', ''),
                'url': commit_data.get('html_url', '')
            }
            commit_list.append(commit_info)
        
        return jsonify({
            'success': True,
            'data': commit_list,
            'count': len(commit_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500

