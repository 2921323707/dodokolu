# -*- coding: utf-8 -*-
"""
LLM 配置管理
从根目录环境变量读取所有模型的密钥和配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量（从项目根目录）
# 从 route/config/llm/setting/__init__.py 向上5层到项目根目录
# __file__ -> setting -> llm -> config -> route -> 项目根目录
project_root = Path(__file__).parent.parent.parent.parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# ==================== OpenRouter API配置 ====================
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free')

# ==================== DeepSeek API配置 ====================
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

# ==================== 豆包 Seed-1.6 API配置 ====================
DOUBAO_API_KEY = os.getenv('DOUBAO_API_KEY', '') or os.getenv('ARK_API_KEY', '')  # 兼容官方文档中的 ARK_API_KEY
DOUBAO_BASE_URL = os.getenv('DOUBAO_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
DOUBAO_MODEL = os.getenv('DOUBAO_MODEL', 'doubao-seed-1-6-251015')

# ==================== Minimax API配置 ====================
MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL', 'https://api.minimaxi.com/anthropic')
MINIMAX_MODEL = os.getenv('MINIMAX_MODEL', 'MiniMax-M2.1')

# ==================== 通用配置 ====================
DEFAULT_MODE = os.getenv('DEFAULT_MODE', 'normal')
MAX_HISTORY_LENGTH = int(os.getenv('MAX_HISTORY_LENGTH', '50'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))

__all__ = [
    'OPENROUTER_API_KEY', 'OPENROUTER_BASE_URL', 'OPENROUTER_MODEL',
    'DEEPSEEK_API_KEY', 'DEEPSEEK_BASE_URL', 'DEEPSEEK_MODEL',
    'DOUBAO_API_KEY', 'DOUBAO_BASE_URL', 'DOUBAO_MODEL',
    'MINIMAX_API_KEY', 'MINIMAX_BASE_URL', 'MINIMAX_MODEL',
    'DEFAULT_MODE', 'MAX_HISTORY_LENGTH', 'TEMPERATURE'
]
