# -*- coding: utf-8 -*-
"""
获取 dodokolu 仓库的最新提交信息
调用 GitHub API 获取 https://github.com/2921323707/dodokolu 的提交时间和信息
"""
import sys
from pathlib import Path

# 设置 Windows 控制台编码为 UTF-8（解决 emoji 显示问题）
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入 GitHub API 函数
from route._github.api import fetch_latest_commit


def get_dodokolu_commit():
    """
    获取 dodokolu 仓库的最新提交信息
    
    返回:
        dict: 包含提交信息的字典，格式如下：
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
    # 仓库信息
    owner = '2921323707'
    repo = 'dodokolu'
    branch = 'main'  # 主分支
    
    # 调用 API 函数获取最新提交
    result = fetch_latest_commit(owner, repo, branch)
    
    return result


def print_commit_info():
    """打印提交信息（用于测试）"""
    print("=" * 80)
    print("获取 dodokolu 仓库最新提交信息")
    print("=" * 80)
    print(f"仓库: https://github.com/2921323707/dodokolu")
    print(f"分支: main")
    print("-" * 80)
    
    result = get_dodokolu_commit()
    
    if result.get('success'):
        data = result.get('data', {})
        print("\n✅ 成功获取提交信息:")
        print("-" * 80)
        print(f"  SHA: {data.get('sha', 'N/A')[:12]}...")
        print(f"  提交信息: {data.get('message', 'N/A').split(chr(10))[0]}")  # 只显示第一行
        print(f"  作者: {data.get('author', {}).get('name', 'N/A')} ({data.get('author', {}).get('email', 'N/A')})")
        print(f"  提交时间: {data.get('date', 'N/A')}")
        print(f"  提交链接: {data.get('url', 'N/A')}")
        print("-" * 80)
        
        # 显示完整提交信息（如果有多行）
        full_message = data.get('message', '')
        if '\n' in full_message:
            print("\n📄 完整提交信息:")
            print("-" * 80)
            for line in full_message.split('\n'):
                print(f"  {line}")
            print("-" * 80)
    else:
        error = result.get('error', '未知错误')
        print(f"\n❌ 获取提交信息失败: {error}")
        print("-" * 80)
    
    return result


if __name__ == "__main__":
    # 直接运行此文件时，打印提交信息
    print_commit_info()

