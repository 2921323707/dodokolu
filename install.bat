@echo off
chcp 65001 >nul
echo ========================================
echo 项目依赖安装脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10或更高版本
    pause
    exit /b 1
)

echo [1/5] 检查Python版本...
python --version
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [错误] Python版本过低，需要Python 3.10或更高版本
    pause
    exit /b 1
)
echo [✓] Python版本检查通过
echo.

echo [2/5] 升级pip和构建工具...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [警告] pip升级失败，将继续尝试安装依赖
)
echo.

echo [3/5] 安装基础依赖（排除火山引擎SDK）...
python -m pip install typing-extensions^>=4.8.0,^<5.0.0 Flask^>=3.0.0,^<6.0.0 Werkzeug^>=3.0.0,^<5.0.0 Jinja2^>=3.1.2,^<4.0.0 itsdangerous^>=2.1.2,^<5.0.0 click^>=8.1.7,^<10.0.0 blinker^>=1.7.0,^<4.0.0 flask-cors^>=4.0.0,^<6.0.0 MarkupSafe^>=2.1.0,^<3.0.0
if errorlevel 1 (
    echo [错误] 基础依赖安装失败
    pause
    exit /b 1
)
echo [✓] 基础依赖安装完成
echo.

echo [4/5] 安装OpenAI SDK及其依赖...
python -m pip install openai^>=1.12.0,^<3.0.0 trio^>=0.22.0,^<1.0.0 httpx^>=0.25.0,^<2.0.0 httpx-sse^>=0.4.0,^<1.0.0 h11^>=0.14.0,^<1.0.0 sniffio^>=1.3.0,^<2.0.0 anyio^>=4.0.0,^<5.0.0
if errorlevel 1 (
    echo [警告] OpenAI SDK依赖安装失败，但将继续安装其他依赖
)
echo [✓] OpenAI SDK依赖安装完成
echo.

echo [5/5] 安装火山引擎SDK（单独安装以避免命令过长）...
REM 使用引号包裹包含方括号的包名，避免Windows批处理解析问题
python -m pip install "volcengine-python-sdk[ark]>=1.0.0,<2.0.0"
if errorlevel 1 (
    echo [警告] 火山引擎SDK安装失败，如果不需要豆包模型功能可以忽略
    echo [提示] 可以稍后手动安装: pip install "volcengine-python-sdk[ark]>=1.0.0,<2.0.0"
) else (
    echo [✓] 火山引擎SDK安装完成
)
echo.

echo [继续] 安装Anthropic SDK...
python -m pip install anthropic^>=0.18.0,^<1.0.0
if errorlevel 1 (
    echo [警告] Anthropic SDK安装失败
) else (
    echo [✓] Anthropic SDK安装完成
)
echo.

echo [继续] 安装HTTP请求库...
python -m pip install requests^>=2.31.0,^<4.0.0 charset-normalizer^>=3.3.0,^<4.0.0 idna^>=3.4,^<4.0 urllib3^>=2.0.0,^<3.0.0 certifi^>=2023.0.0
if errorlevel 1 (
    echo [警告] HTTP请求库安装失败
) else (
    echo [✓] HTTP请求库安装完成
)
echo.

echo [继续] 安装其他依赖...
python -m pip install python-dotenv^>=1.0.0,^<3.0.0 feedparser^>=6.0.0,^<8.0.0 schedule^>=1.2.0,^<3.0.0 websockets^>=12.0,^<14.0 tenacity^>=8.2.0,^<10.0.0 backoff^>=2.2.0,^<3.0.0 retry^>=0.9.2,^<1.0.0 exceptiongroup^>=1.1.0,^<2.0.0 packaging^>=23.0,^<25.0 setuptools^>=68.0.0 wheel^>=0.40.0 tqdm^>=4.65.0,^<5.0.0
if errorlevel 1 (
    echo [警告] 部分依赖安装失败
) else (
    echo [✓] 其他依赖安装完成
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
pause

