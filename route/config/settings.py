# -*- coding: utf-8 -*-
"""
应用配置常量
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# ==================== API配置 ====================

# OpenRouter API配置（unnormal模式）
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free')

# DeepSeek API配置（normal模式）
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

# ==================== 应用配置 ====================

DEFAULT_MODE = os.getenv('DEFAULT_MODE', 'unnormal')
MAX_HISTORY_LENGTH = int(os.getenv('MAX_HISTORY_LENGTH', '50'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))

