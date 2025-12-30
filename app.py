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
    github_bp
)
from database import init_database
from config.maintenance.maintenance import MAINTENANCE_PAGES

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 用于 session，建议改为环境变量
CORS(app)  # 允许跨域请求

# 初始化数据库（如果不存在则创建）
init_database()

# 启动番剧推荐定时任务（在后台线程中运行）
try:
    from components.rss.comic_recommend import start_schedule_in_thread
    start_schedule_in_thread()
    print("番剧推荐小助手已经启动")
    print("会在每天的 8:00、14:00、20:00 和 2:00 准时为你推荐好看的番剧")
except Exception as e:
    print(f"启动番剧推荐定时任务失败: {e}")

# 启动历史记录清理定时任务（在后台线程中运行）
try:
    from config.llm.base.history.cleanup import start_cleanup_schedule
    start_cleanup_schedule()
    print("历史记录清理任务已经启动")
    print("会在每天的 0:00 自动清理空的 JSON 文件")
except Exception as e:
    print(f"启动历史记录清理定时任务失败: {e}")

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

@app.route('/')
def index():
    """主页面（通用路由）"""
    return render_template('index.html')


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

