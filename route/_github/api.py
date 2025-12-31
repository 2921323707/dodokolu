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


def fetch_latest_commit(owner, repo, branch=None):
    """
    获取仓库最近一次提交的时间和 commit 备注（独立函数，可在 Flask 外部调用）
    
    参数:
        owner: 仓库所有者（必需）
        repo: 仓库名称（必需）
        branch: 分支名称（可选，默认为默认分支）
    
    返回:
        {
            "success": True/False,
            "data": {
                "sha": "commit hash",
                "message": "commit message",
                "author": {
                    "name": "author name",
                    "email": "author email"
                },
                "date": "2024-01-01T00:00:00Z",
                "url": "commit url"
            },
            "error": "错误信息（如果失败）"
        }
    """
    try:
        # 验证必需参数
        if not owner or not repo:
            return {
                'success': False,
                'error': '缺少必需参数：owner 和 repo'
            }
        
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
            return {
                'success': False,
                'error': '仓库不存在或无权访问'
            }
        
        if response.status_code == 403:
            return {
                'success': False,
                'error': 'API 速率限制已超，请稍后再试或配置 GITHUB_API_TOKEN'
            }
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'GitHub API 请求失败: {response.status_code}'
            }
        
        # 解析响应
        if branch:
            # 单个提交对象
            commit_data = response.json()
        else:
            # 提交列表，取第一个
            commits = response.json()
            if not commits or len(commits) == 0:
                return {
                    'success': False,
                    'error': '仓库没有提交记录'
                }
            commit_data = commits[0]
        
        # 提取所需信息
        # 优先使用顶层的author（GitHub用户信息），如果没有则使用commit.author
        commit_author = commit_data.get('commit', {}).get('author', {})
        top_author = commit_data.get('author', {})
        
        # 获取作者名称：优先使用GitHub用户名，然后是commit author name，最后尝试email前缀
        author_name = ''
        if top_author and top_author.get('login'):
            author_name = top_author.get('login')
        elif commit_author.get('name'):
            author_name = commit_author.get('name')
        elif commit_author.get('email'):
            # 如果name为空，尝试使用email的@之前的部分
            email = commit_author.get('email', '')
            if '@' in email:
                author_name = email.split('@')[0]
        
        # 如果还是没有，尝试使用committer信息
        if not author_name:
            commit_committer = commit_data.get('commit', {}).get('committer', {})
            if commit_committer.get('name'):
                author_name = commit_committer.get('name')
            elif commit_committer.get('email'):
                email = commit_committer.get('email', '')
                if '@' in email:
                    author_name = email.split('@')[0]
        
        # 最终如果还是没有，使用默认值
        if not author_name:
            author_name = '未知'
        
        # 获取作者邮箱
        author_email = commit_author.get('email', '') or commit_data.get('commit', {}).get('committer', {}).get('email', '')
        
        commit_info = {
            'sha': commit_data.get('sha', ''),
            'message': commit_data.get('commit', {}).get('message', ''),
            'author': {
                'name': author_name,
                'email': author_email
            },
            'date': commit_data.get('commit', {}).get('author', {}).get('date', ''),
            'url': commit_data.get('html_url', '')
        }
        
        return {
            'success': True,
            'data': commit_info
        }
        
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': '请求超时，请稍后再试'
        }
    
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'网络请求失败: {str(e)}'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }


@github_api_bp.route('/latest-commit', methods=['GET'])
def get_latest_commit():
    """
    获取仓库最近一次提交的时间和 commit 备注（Flask 路由）
    
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
    # 获取查询参数
    owner = request.args.get('owner')
    repo = request.args.get('repo')
    branch = request.args.get('branch', None)
    
    # 调用独立函数
    result = fetch_latest_commit(owner, repo, branch)
    
    # 根据结果返回相应的 HTTP 状态码
    if not result.get('success'):
        error = result.get('error', '未知错误')
        status_code = 400
        if '不存在' in error or '无权访问' in error or '没有提交记录' in error:
            status_code = 404
        elif '速率限制' in error:
            status_code = 403
        elif '超时' in error:
            status_code = 504
        elif '网络请求失败' in error or '服务器错误' in error:
            status_code = 500
        return jsonify(result), status_code
    
    return jsonify(result)


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
            # 优先使用顶层的author（GitHub用户信息），如果没有则使用commit.author
            commit_author = commit_data.get('commit', {}).get('author', {})
            top_author = commit_data.get('author', {})
            
            # 获取作者名称：优先使用GitHub用户名，然后是commit author name，最后尝试email前缀
            author_name = ''
            if top_author and top_author.get('login'):
                author_name = top_author.get('login')
            elif commit_author.get('name'):
                author_name = commit_author.get('name')
            elif commit_author.get('email'):
                email = commit_author.get('email', '')
                if '@' in email:
                    author_name = email.split('@')[0]
            
            # 如果还是没有，尝试使用committer信息
            if not author_name:
                commit_committer = commit_data.get('commit', {}).get('committer', {})
                if commit_committer.get('name'):
                    author_name = commit_committer.get('name')
                elif commit_committer.get('email'):
                    email = commit_committer.get('email', '')
                    if '@' in email:
                        author_name = email.split('@')[0]
            
            # 最终如果还是没有，使用默认值
            if not author_name:
                author_name = '未知'
            
            # 获取作者邮箱
            author_email = commit_author.get('email', '') or commit_data.get('commit', {}).get('committer', {}).get('email', '')
            
            commit_info = {
                'sha': commit_data.get('sha', ''),
                'message': commit_data.get('commit', {}).get('message', ''),
                'author': {
                    'name': author_name,
                    'email': author_email
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

