# Undefined 智能体

这是基于 Minimax API 的智能体实现模块，使用 Anthropic SDK 进行调用。

## 目录结构

```
undefined/
├── __init__.py      # 自动注册 UndefinedAgent
├── agent.py         # UndefinedAgent 实现
├── prompt.py        # Undefined 专属提示词
├── reference.py     # 参考调用代码
└── README.md       # 本文档
```

## 功能特性

- 基于 Minimax API（使用 Anthropic SDK 兼容接口）
- Minimax M2.1 是完整的 agentic model，自带以下能力：
  - 联网搜索：可以直接获取最新的网络信息
  - 天气查询：可以查询任意地点的天气信息
  - 时间查询：可以获取当前时间信息
- 不需要任何外部工具
- 流式响应输出（模拟）

## 配置要求

在 `.env` 文件中配置以下环境变量：

```env
MINIMAX_BASE_URL=https://api.minimaxi.com/anthropic
MINIMAX_API_KEY=your_minimax_api_key_here
```

## 使用方式

```python
from config.llm.base import get_agent

# 获取 Undefined 智能体
agent = get_agent('undefined')

# 使用智能体
for chunk in agent.stream_response(messages, session_id, location, email):
    yield chunk
```

## 提示词定制

提示词定义在 `prompt.py` 中的 `SYSTEM_PROMPT_BASE`，可以根据需要修改。

## 工具支持

**注意**：Minimax M2.1 是完整的 agentic model，自带以下能力，不需要任何外部工具：
- 联网搜索：可以直接获取最新的网络信息
- 天气查询：可以查询任意地点的天气信息
- 时间查询：可以获取当前时间信息

因此，此智能体不提供任何外部工具接口。

## API 说明

Minimax API 使用 Anthropic SDK 兼容接口，支持以下特性：

- 模型：`MiniMax-M2.1`
- 支持 thinking、text、tool_use 三种内容块类型
- 工具调用需要将完整的 `response.content` 回传到消息历史

## 参考代码

详细的使用示例请参考 `reference.py` 文件。

