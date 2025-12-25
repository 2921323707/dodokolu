# AI 对话助手

一款轻量级的 AI 对话助手应用，支持持续对话、记忆功能和画图功能。

## 功能特性

- 🤖 **AI 对话**：基于 OpenRouter API 的智能对话
- 💾 **对话记忆**：自动保存对话历史，支持上下文理解
- 🎨 **画图功能**：支持图片生成（待开发）
- 📱 **响应式设计**：完美支持手机端和桌面端
- 🎨 **简洁 UI**：现代化设计，界面简洁美观

## 技术栈

- **后端**：Flask + OpenAI SDK
- **前端**：原生 HTML/CSS/JavaScript
- **API**：OpenRouter.ai

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在 `app.py` 中已经配置了 API Key，如果需要修改，请编辑以下部分：

```python
api_key="your-api-key-here"
```

### 3. 运行应用

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问：`http://localhost:5000`

## 项目结构

```
.
├── app.py              # Flask 后端主文件
├── llm_test.py        # 原始测试文件
├── requirements.txt    # Python 依赖
├── README.md          # 项目说明
├── templates/         # HTML 模板
│   └── index.html     # 主页面
└── static/            # 静态文件
    └── css/
        └── style.css  # 样式文件
```

## API 接口

### POST /api/chat
发送聊天消息

**请求体：**
```json
{
    "message": "用户消息",
    "session_id": "session_id"
}
```

**响应：** Server-Sent Events (SSE) 流式响应

### GET /api/history/<session_id>
获取对话历史

### POST /api/clear/<session_id>
清空对话历史

### POST /api/image
生成图片（开发中）

## 使用说明

1. **开始对话**：在聊天框输入消息，点击发送或按 Enter 键
2. **查看历史**：对话历史会自动保存，刷新页面后会恢复
3. **清空历史**：点击"清空历史"按钮清空当前对话
4. **生成图片**：在画图区输入描述，点击"生成图片"按钮

## 注意事项

- 确保网络连接正常，应用需要访问 OpenRouter API
- 对话历史存储在内存中，重启服务后会清空
- 如需持久化存储，可以修改 `conversation_history` 的存储方式

## 开发说明

### 修改提示词

在 `app.py` 中修改 `SYSTEM_PROMPT` 变量即可。

### 修改模型

在 `app.py` 的 `llm_stream` 函数中修改 `model` 参数。

### 自定义样式

编辑 `static/css/style.css` 文件即可自定义界面样式。

## 许可证

MIT License

