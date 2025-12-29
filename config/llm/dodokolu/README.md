# Dodokolu 智能体 - 苏禾瑶

这是苏禾瑶智能体的专属实现模块。

## 目录结构

```
dodokolu/
├── __init__.py      # 自动注册 SuheyaoAgent
├── agent.py         # SuheyaoAgent 实现
├── prompt.py        # 苏禾瑶专属提示词
└── README.md       # 本文档
```

## 功能特性

- 基于 DeepSeek 模型
- 支持工具调用（天气、搜索、表情包等）
- 自动表情包匹配
- 收藏图片发送
- 流式响应输出

## 使用方式

```python
from config.llm.base import get_agent

# 获取苏禾瑶智能体
agent = get_agent('suheyao')  # 或 'normal', 'default'

# 使用智能体
for chunk in agent.stream_response(messages, session_id, location, email):
    yield chunk
```

## 提示词定制

提示词定义在 `prompt.py` 中的 `SYSTEM_PROMPT_BASE`，可以根据需要修改。

## 工具支持

- `get_weather`: 获取天气信息
- `search_web`: 联网搜索
- `send_emoji`: 自动表情包匹配（已集成到流式输出中）
- `send_favorite_image`: 发送收藏图片

