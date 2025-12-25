# dodokolu

这是一个集成了主流AI模型调用的个人网站，支持持续对话、记忆功能和多种实用功能。

## 功能特性

- 🤖 **AI 对话**：基于 OpenRouter 和 DeepSeek API 的智能对话
- 💾 **对话记忆**：自动保存对话历史，支持上下文理解
- 📰 **RSS 订阅**：最新番剧订阅和推荐
- 🖼️ **相册功能**：图片展示和管理
- 📧 **邮件通知**：支持邮件发送功能
- 📱 **响应式设计**：完美支持手机端和桌面端
- 🎨 **简洁 UI**：现代化设计，界面简洁美观

## 技术栈

- **后端**：Flask + OpenAI SDK
- **前端**：原生 HTML/CSS/JavaScript
- **API**：OpenRouter.ai / DeepSeek API
- **数据库**：SQLite

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp env.example .env
```

编辑 `.env` 文件，填入以下配置：
- OpenRouter API Key
- DeepSeek API Key
- Tavily API Key（可选，用于搜索功能）
- QQ 邮箱配置（可选，用于邮件功能）

### 3. 初始化数据库

```bash
python database/db_init.py
```

### 4. 运行应用

```bash
python app.py
```

### 5. 访问应用

打开浏览器访问：`http://localhost:5000`

## 项目结构

```
.
├── app.py              # Flask 后端主文件
├── components/         # 功能组件
│   ├── email/         # 邮件发送组件
│   └── rss/           # RSS 订阅组件
├── database/          # 数据库相关
├── route/             # 路由模块
│   ├── login_route/   # 登录相关路由
│   ├── album_route/   # 相册相关路由
│   └── config/        # 配置相关
├── static/            # 静态文件
│   ├── css/           # 样式文件
│   ├── js/            # JavaScript 文件
│   └── imgs/          # 图片资源
├── templates/         # HTML 模板
└── tools/             # 工具函数
```

## 注意事项

- 确保网络连接正常，应用需要访问外部 API
- 相册图片已通过 `.gitignore` 忽略，不会提交到仓库
- 环境变量文件 `.env` 包含敏感信息，请勿提交到版本控制

## 许可证

MIT License
