# Lumina 智能体

这是基于 Google Gemini Flash 3 的智能体实现模块。

## 目录结构

```
lumina/
├── __init__.py      # 自动注册 LuminaAgent
├── agent.py         # LuminaAgent 实现
├── prompt.py        # Lumina 专属提示词
└── README.md       # 本文档
```

## 功能特性

- 基于 Google Gemini Flash 3 模型
- 支持工具调用（天气、搜索等）
- 流式响应输出
- 收藏图片发送

## 配置要求

在 `.env` 文件中配置以下环境变量：

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

### 获取 API 密钥

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录你的 Google 账号
3. 创建新的 API 密钥
4. 将密钥复制到 `.env` 文件中

### 模型名称

- `gemini-2.0-flash-exp` - Gemini Flash 3 实验版本（推荐）
- `gemini-1.5-flash` - Gemini 1.5 Flash
- `gemini-1.5-pro` - Gemini 1.5 Pro

## 使用方式

```python
from config.llm.base import get_agent

# 获取 Lumina 智能体
agent = get_agent('lumina')

# 使用智能体
for chunk in agent.stream_response(messages, session_id, location, email):
    yield chunk
```

## 提示词定制

提示词定义在 `prompt.py` 中的 `SYSTEM_PROMPT_BASE`，可以根据需要修改。

## 工具支持

Lumina 智能体支持以下工具：

- `search_web` - 网络搜索
- `get_weather` - 天气查询
- `send_favorite_image` - 发送收藏图片

## API 说明

Google Gemini API 使用 `google-generativeai` SDK，支持以下特性：

- 流式响应
- 函数调用（工具调用）
- 多轮对话
- 系统提示词

## 依赖安装

确保已安装 `google-generativeai` 包：

```bash
pip install google-generativeai
```

## 注意事项

1. Gemini API 需要有效的 API 密钥
2. 工具调用最多支持 5 轮，避免无限循环
3. 系统提示词会自动包含时间信息
4. 支持收藏图片发送

