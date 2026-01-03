@echo off
chcp 65001 >nul
echo ========================================
echo 项目依赖安装脚本（Python 3.10+）
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10或更高版本
    pause
    exit /b 1
)

echo [1/6] 检查Python版本...
python --version
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [错误] Python版本过低，需要Python 3.10或更高版本
    pause
    exit /b 1
)
echo [✓] Python版本检查通过
echo.

echo [2/6] 升级pip和构建工具...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [警告] pip升级失败，将继续尝试安装依赖
)
echo.

echo [3/6] 安装基础工具和类型支持...
python -m pip install "typing-extensions>=4.8.0,<7.0.0"
if errorlevel 1 (
    echo [错误] typing-extensions 安装失败
    pause
    exit /b 1
)
echo [✓] 基础工具安装完成
echo.

echo [4/6] 安装Web框架及其核心依赖...
python -m pip install "Flask>=3.0.0,<7.0.0" "Werkzeug>=3.0.0,<6.0.0" "Jinja2>=3.1.2,<4.0.0"
if errorlevel 1 (
    echo [错误] Web框架核心依赖安装失败
    pause
    exit /b 1
)
python -m pip install "itsdangerous>=2.1.2,<6.0.0" "click>=8.1.7,<11.0.0" "blinker>=1.7.0,<5.0.0"
if errorlevel 1 (
    echo [错误] Web框架辅助依赖安装失败
    pause
    exit /b 1
)
python -m pip install "flask-cors>=4.0.0,<7.0.0" "MarkupSafe>=2.1.0,<3.0.0"
if errorlevel 1 (
    echo [错误] Web框架扩展依赖安装失败
    pause
    exit /b 1
)
echo [✓] Web框架依赖安装完成
echo.

echo [5/6] 安装OpenAI SDK及其异步依赖...
python -m pip install "openai>=1.12.0,<4.0.0"
if errorlevel 1 (
    echo [警告] OpenAI SDK安装失败，但将继续安装其他依赖
) else (
    echo [✓] OpenAI SDK安装完成
)
python -m pip install "trio>=0.22.0,<2.0.0" "httpx>=0.25.0,<3.0.0" "httpx-sse>=0.4.0,<2.0.0"
if errorlevel 1 (
    echo [警告] OpenAI SDK异步依赖部分安装失败
) else (
    echo [✓] OpenAI SDK异步依赖安装完成
)
python -m pip install "h11>=0.14.0,<2.0.0" "sniffio>=1.3.0,<3.0.0" "anyio>=4.0.0,<6.0.0"
if errorlevel 1 (
    echo [警告] OpenAI SDK底层依赖部分安装失败
) else (
    echo [✓] OpenAI SDK底层依赖安装完成
)
echo.

echo [6/6] 安装火山引擎SDK（豆包模型）...
REM 使用引号包裹包含方括号的包名，避免Windows批处理解析问题
REM 版本范围已更新为匹配 requirements.txt
python -m pip install "volcengine-python-sdk[ark]>=1.0.0,<3.0.0"
if errorlevel 1 (
    echo [警告] 火山引擎SDK安装失败，如果不需要豆包模型功能可以忽略
    echo [提示] 可以稍后手动安装: pip install "volcengine-python-sdk[ark]>=1.0.0,<3.0.0"
) else (
    echo [✓] 火山引擎SDK安装完成
)
echo.

echo [继续] 安装Anthropic SDK（Minimax API兼容）...
python -m pip install "anthropic>=0.18.0,<2.0.0"
if errorlevel 1 (
    echo [警告] Anthropic SDK安装失败
) else (
    echo [✓] Anthropic SDK安装完成
)
echo.

echo [继续] 安装Google Gemini SDK...
python -m pip install "google-genai>=0.2.0,<2.0.0"
if errorlevel 1 (
    echo [警告] Google Gemini SDK安装失败
) else (
    echo [✓] Google Gemini SDK安装完成
)
echo.

echo [继续] 安装HTTP请求库...
python -m pip install "requests>=2.31.0,<5.0.0" "charset-normalizer>=3.3.0,<5.0.0"
if errorlevel 1 (
    echo [警告] HTTP请求库部分安装失败
) else (
    echo [✓] HTTP请求库核心安装完成
)
python -m pip install "idna>=3.4,<5.0" "urllib3>=2.0.0,<4.0.0" "certifi>=2023.0.0"
if errorlevel 1 (
    echo [警告] HTTP请求库依赖部分安装失败
) else (
    echo [✓] HTTP请求库依赖安装完成
)
echo.

echo [继续] 安装环境变量和配置管理...
python -m pip install "python-dotenv>=1.0.0,<4.0.0"
if errorlevel 1 (
    echo [警告] python-dotenv安装失败
) else (
    echo [✓] python-dotenv安装完成
)
echo.

echo [继续] 安装RSS解析和定时任务...
python -m pip install "feedparser>=6.0.0,<9.0.0" "schedule>=1.2.0,<4.0.0"
if errorlevel 1 (
    echo [警告] RSS和定时任务库安装失败
) else (
    echo [✓] RSS和定时任务库安装完成
)
echo.

echo [继续] 安装WebSocket和异步通信...
python -m pip install "websockets>=12.0,<15.0"
if errorlevel 1 (
    echo [警告] websockets安装失败
) else (
    echo [✓] websockets安装完成
)
echo.

echo [继续] 安装容错和重试机制...
python -m pip install "tenacity>=8.2.0,<11.0.0" "backoff>=2.2.0,<4.0.0" "retry>=0.9.2,<2.0.0"
if errorlevel 1 (
    echo [警告] 重试库部分安装失败
) else (
    echo [✓] 重试库安装完成
)
echo.

echo [继续] 安装异常处理和日志增强...
python -m pip install "exceptiongroup>=1.1.0,<3.0.0"
if errorlevel 1 (
    echo [警告] exceptiongroup安装失败
) else (
    echo [✓] exceptiongroup安装完成
)
echo.

echo [继续] 安装工具库...
python -m pip install "packaging>=23.0,<27.0" "tqdm>=4.65.0,<6.0.0"
if errorlevel 1 (
    echo [警告] 工具库部分安装失败
) else (
    echo [✓] 工具库安装完成
)
echo.

echo ========================================
echo 依赖安装完成！
echo ========================================
echo.
echo 接下来的步骤：
echo 1. 复制 env.example 为 .env 并填入必要的API密钥
echo 2. 初始化数据库: python database/db_init.py
echo 3. 运行应用: python app.py
echo.
echo 提示：如果某些依赖安装失败，可以尝试：
echo   - 升级pip: python -m pip install --upgrade pip
echo   - 清理缓存: python -m pip cache purge
echo   - 使用国内镜像: python -m pip install [包名] -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
pause
