# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from flask_cors import CORS
from route.chat_routes import chat_bp
from route.image_routes import image_bp
from route.login_route import login_bp
from route.alert.alert import alert_bp
from route.album_route import album_bp
from database import init_database
from route.config.maintenance.maintenance import MAINTENANCE_PAGES

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 用于 session，建议改为环境变量
CORS(app)  # 允许跨域请求

# 初始化数据库（如果不存在则创建）
init_database()

# 启动番剧推荐定时任务（在后台线程中运行）
try:
    from components.rss.comic_recommend import start_schedule_in_thread
    start_schedule_in_thread()
    print("番剧推荐定时任务已启动（每天早上8:00执行）")
except Exception as e:
    print(f"启动番剧推荐定时任务失败: {e}")
    # 不影响主应用启动

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

@app.route('/')
def index():
    """主页面（通用路由）"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

