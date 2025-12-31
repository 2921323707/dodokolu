# -*- coding: utf-8 -*-
"""
GitHub API 测试文件
测试获取仓库最近一次提交的时间和 commit 备注
"""
import os
import sys
import requests
from pathlib import Path
from datetime import datetime

# 设置 Windows 控制台编码为 UTF-8（解决 emoji 显示问题）
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 确保环境变量已设置（如果 .env 文件存在）
from dotenv import load_dotenv
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# GitHub API 配置
GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN', '')
GITHUB_API_BASE_URL = 'https://api.github.com'


def get_github_headers():
    """获取 GitHub API 请求头"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'dodokoru-app'
    }
    if GITHUB_API_TOKEN:
        headers['Authorization'] = f'token {GITHUB_API_TOKEN}'
    return headers


def test_get_latest_commit(owner, repo, branch=None):
    """
    测试获取仓库最近一次提交
    
    参数:
        owner: 仓库所有者
        repo: 仓库名称
        branch: 分支名称（可选）
    """
    print("=" * 80)
    print(f"测试获取最新提交: {owner}/{repo}")
    if branch:
        print(f"分支: {branch}")
    print("=" * 80)
    
    try:
        # 构建 API 端点
        if branch:
            url = f'{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/commits/{branch}'
        else:
            url = f'{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/commits'
        
        # 发送请求
        headers = get_github_headers()
        print(f"\n📡 请求 URL: {url}")
        print(f"🔑 使用 Token: {'是' if GITHUB_API_TOKEN else '否（匿名访问）'}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        print(f"\n📊 响应状态码: {response.status_code}")
        
        if response.status_code == 404:
            print("❌ 错误: 仓库不存在或无权访问")
            return False
        
        if response.status_code == 403:
            print("❌ 错误: API 速率限制已超，请稍后再试或配置 GITHUB_API_TOKEN")
            print(f"   响应内容: {response.text[:200]}")
            return False
        
        if response.status_code != 200:
            print(f"❌ 错误: GitHub API 请求失败: {response.status_code}")
            print(f"   响应内容: {response.text[:200]}")
            return False
        
        # 解析响应
        if branch:
            commit_data = response.json()
        else:
            commits = response.json()
            if not commits or len(commits) == 0:
                print("❌ 错误: 仓库没有提交记录")
                return False
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
        
        # 格式化日期
        try:
            date_obj = datetime.fromisoformat(commit_info['date'].replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            formatted_date = commit_info['date']
        
        # 显示结果
        print("\n" + "✅" * 40)
        print("📝 提交信息:")
        print("-" * 80)
        print(f"  SHA: {commit_info['sha'][:12]}...")
        print(f"  提交信息: {commit_info['message'].split(chr(10))[0]}")  # 只显示第一行
        print(f"  作者: {commit_info['author']['name']} ({commit_info['author']['email']})")
        print(f"  提交时间: {formatted_date}")
        print(f"  提交链接: {commit_info['url']}")
        print("-" * 80)
        
        # 显示完整提交信息（如果有多行）
        full_message = commit_info['message']
        if '\n' in full_message:
            print("\n📄 完整提交信息:")
            print("-" * 80)
            for line in full_message.split('\n'):
                print(f"  {line}")
            print("-" * 80)
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ 错误: 请求超时，请稍后再试")
        return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 错误: 网络请求失败: {str(e)}")
        return False
    
    except Exception as e:
        print(f"❌ 错误: 服务器错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_repositories():
    """测试多个仓库"""
    print("\n" + "=" * 80)
    print("测试多个仓库")
    print("=" * 80)
    
    # 测试用例：包括您的仓库和一些知名的公开仓库
    test_cases = [
        {'owner': '2921323707', 'repo': 'dodokolu', 'branch': 'main'},
        {'owner': 'octocat', 'repo': 'Hello-World'},
        {'owner': 'microsoft', 'repo': 'vscode'},
        {'owner': 'facebook', 'repo': 'react'},
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_count}]")
        branch = test_case.get('branch', None)
        if test_get_latest_commit(test_case['owner'], test_case['repo'], branch):
            success_count += 1
        print()  # 空行分隔
    
    print("=" * 80)
    print(f"测试完成: {success_count}/{total_count} 成功")
    print("=" * 80)


def test_custom_repository():
    """测试自定义仓库（需要用户输入）"""
    print("\n" + "=" * 80)
    print("测试自定义仓库")
    print("=" * 80)
    
    try:
        owner = input("请输入仓库所有者 (owner): ").strip()
        repo = input("请输入仓库名称 (repo): ").strip()
        branch = input("请输入分支名称 (可选，直接回车使用默认分支): ").strip()
        
        if not owner or not repo:
            print("❌ 错误: owner 和 repo 不能为空")
            return
        
        branch = branch if branch else None
        test_get_latest_commit(owner, repo, branch)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GitHub API 测试套件")
    print("=" * 80)
    print("\n本测试将调用 GitHub API 获取仓库最近一次提交的时间和 commit 备注")
    print("\n提示:")
    print("  - 如果配置了 GITHUB_API_TOKEN，每小时可请求 5000 次")
    print("  - 如果未配置 Token，每小时只能请求 60 次（匿名访问）")
    print("  - 建议在 .env 文件中配置 GITHUB_API_TOKEN 以提高速率限制")
    print()
    
    try:
        # 测试 1: 测试您的仓库
        print("\n【测试 1】测试您的仓库 (2921323707/dodokolu)")
        print("-" * 80)
        test_get_latest_commit('2921323707', 'dodokolu', 'main')
        
        # 测试 2: 测试知名的公开仓库（作为对比）
        print("\n【测试 2】测试知名公开仓库 (octocat/Hello-World)")
        print("-" * 80)
        test_get_latest_commit('octocat', 'Hello-World')
        
        # 测试 3: 测试多个仓库（可选，取消注释以运行）
        # print("\n【测试 3】测试多个仓库")
        # print("-" * 80)
        # test_multiple_repositories()
        
        # 测试 4: 测试自定义仓库（可选，取消注释以运行）
        # print("\n【测试 4】测试自定义仓库")
        # print("-" * 80)
        # test_custom_repository()
        
        print("\n" + "=" * 80)
        print("✅ 测试完成")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

