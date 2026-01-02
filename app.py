# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
from route import (
    chat_bp,
    image_bp,
    login_bp,
    alert_bp,
    album_bp,
    admin_bp,
    heaven_bp,
    user_message_bp,
    github_bp,
    check_api_bp,
    fiction_api_bp
)
from database import init_database
from config.maintenance.maintenance import MAINTENANCE_PAGES

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 用于 session，建议改为环境变量
CORS(app)  # 允许跨域请求

# 初始化数据库（如果不存在则创建）
init_database()

# ============================================================================
# 定时任务初始化
# ============================================================================
from datetime import datetime
import os

def init_scheduled_tasks():
    """初始化所有定时任务"""
    tasks = [
        {
            'name': '番剧推荐',
            'module': 'components.rss.comic_recommend',
            'function': 'start_schedule_in_thread',
            'schedule': '每天 8:00、14:00、20:00、2:00',
            'description': '自动推荐好看的番剧'
        },
        {
            'name': '历史记录清理',
            'module': 'config.llm.base.history.cleanup',
            'function': 'start_cleanup_schedule',
            'schedule': '每天 0:00',
            'description': '自动清理空的 JSON 文件'
        },
        {
            'name': '打卡提醒',
            'module': 'components.check.check_reminder',
            'function': 'start_check_reminder_schedule',
            'schedule': '每天 9:00、15:00、21:00',
            'description': '检查打卡状态并发送提醒'
        },
        {
            'name': '每日故事生成',
            'module': 'components.fiction.fiction_generate',
            'function': 'start_fiction_schedule',
            'schedule': '每天 6:00',
            'description': '自动生成一篇新故事'
        }
    ]
    
    print("\n" + "=" * 70)
    print("🚀 正在启动定时任务...")
    print("=" * 70)
    
    success_count = 0
    failed_count = 0
    
    for task in tasks:
        try:
            module = __import__(task['module'], fromlist=[task['function']])
            func = getattr(module, task['function'])
            func()
            success_count += 1
            print(f"✅ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {task['name']} - 启动成功")
            print(f"   📅 执行时间: {task['schedule']}")
            print(f"   📝 功能说明: {task['description']}")
        except Exception as e:
            failed_count += 1
            print(f"❌ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {task['name']} - 启动失败: {e}")
    
    print("=" * 70)
    print(f"📊 定时任务启动完成: 成功 {success_count}/{len(tasks)}, 失败 {failed_count}/{len(tasks)}")
    print("=" * 70 + "\n")

# 只在主进程中初始化定时任务，避免 Flask 重载时重复执行
# 使用环境变量标记，确保只执行一次
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    # 第一次启动时执行
    init_scheduled_tasks()

# 维护模式检查中间件
@app.before_request
def check_maintenance_mode():
    # 排除静态文件（CSS、JS、图片等），确保维护页面能正常加载
    if request.path.startswith('/static'):
        return None
    
    # 检查当前路径是否在维护列表中
    current_path = request.path
    for maintenance_path in MAINTENANCE_PAGES:
        # 精确匹配
        if current_path == maintenance_path:
            return render_template('error/maintenance.html'), 503
        # 前缀匹配（确保是路径分隔符，避免错误匹配）
        # 例如：'/api' 匹配 '/api/chat'，但不匹配 '/api123'
        if current_path.startswith(maintenance_path + '/'):
            return render_template('error/maintenance.html'), 503
    
    return None

# 注册蓝图
app.register_blueprint(chat_bp)
app.register_blueprint(image_bp)
app.register_blueprint(login_bp)
app.register_blueprint(alert_bp)
app.register_blueprint(album_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(heaven_bp)
app.register_blueprint(user_message_bp)
app.register_blueprint(github_bp)
app.register_blueprint(check_api_bp)
app.register_blueprint(fiction_api_bp)

@app.route('/')
def index():
    """主页面（通用路由）"""
    return render_template('index.html')


@app.route('/check')
def check_page():
    """每日打卡页面"""
    return render_template('index_box/check.html')


@app.route('/fiction_show')
def fiction_show_page():
    """小说阅读页面"""
    return render_template('index_box/fiction_show.html')


@app.route('/anime_show')
def daily_article_page():
    """每日一文页面"""
    return render_template('index_box/fiction_show.html')


@app.route('/miku_study')
def miku_study_page():
    """miku伴学页面"""
    return render_template('index_box/.html')


@app.route('/custom')
def custom_page():
    """待定义页面"""
    return render_template('index_box/.html')


@app.route('/database/avator/<path:filename>')
def serve_avatar(filename):
    """提供头像文件访问"""
    # 从路径中提取邮箱文件夹和文件名
    # filename 格式：邮箱文件夹/文件名
    parts = filename.split('/', 1)
    if len(parts) == 2:
        email_folder, avatar_file = parts
        avatar_dir = Path('database') / 'avator' / email_folder
        if avatar_dir.exists() and (avatar_dir / avatar_file).exists():
            return send_from_directory(str(avatar_dir), avatar_file)
    return 'File not found', 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

