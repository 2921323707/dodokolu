from flask import Blueprint, render_template, request, jsonify, session
from components.email.email_sender import send_email
from datetime import datetime
import os
from werkzeug.utils import secure_filename

feedback_bp = Blueprint('feedback', __name__)

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@feedback_bp.route('/feedback')
def feedback_page():
    """反馈页面"""
    return render_template('feedback.html')


@feedback_bp.route('/api/feedback', methods=['POST'])
def feedback_api():
    """反馈提交API"""
    try:
        # 验证登录状态
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录', 'require_login': True}), 401
        
        # 获取表单数据（支持文件上传，使用 request.form）
        feedback_content = request.form.get('content', '').strip()
        feedback_contact = request.form.get('contact', '').strip()
        
        if not feedback_content:
            return jsonify({'success': False, 'message': '反馈内容不能为空'}), 400
        
        # 获取用户信息
        username = session.get('username', '')
        user_email = session.get('email', '')
        
        # 处理图片上传（支持多张图片，最多3张）
        image_paths = []
        if 'images' in request.files:
            image_files = request.files.getlist('images')
            
            # 限制最多3张图片
            if len(image_files) > 3:
                return jsonify({'success': False, 'message': '最多只能上传3张图片'}), 400
            
            # 确保目录存在
            upload_dir = os.path.join('static', 'users', 'feed_back')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 处理每张图片
            for idx, image_file in enumerate(image_files):
                if image_file and image_file.filename and allowed_file(image_file.filename):
                    # 根据用户邮箱确定文件扩展名
                    file_ext = image_file.filename.rsplit('.', 1)[1].lower()
                    # 使用用户邮箱作为文件名，添加序号以区分多张图片
                    if user_email:
                        # 将邮箱地址中的特殊字符替换为下划线，保留邮箱格式
                        safe_email = user_email.replace('@', '_at_').replace('.', '_')
                        # 进一步清理，确保文件名安全
                        safe_email = secure_filename(safe_email)
                        filename = f"{safe_email}_{idx + 1}.{file_ext}"
                    else:
                        # 如果没有邮箱，使用用户ID
                        filename = f"user_{user_id}_{idx + 1}.{file_ext}"
                    
                    image_path = os.path.join(upload_dir, filename)
                    image_file.save(image_path)
                    image_paths.append(image_path)
        
        # 构建HTML邮件内容
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>用户反馈</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #fff5f7;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 8px rgba(255, 105, 180, 0.15);
                }}
                .header {{
                    border-bottom: 3px solid #ff69b4;
                    padding-bottom: 15px;
                    margin-bottom: 25px;
                }}
                .header h1 {{
                    color: #ff69b4;
                    margin: 0;
                    font-size: 24px;
                }}
                .info-section {{
                    background-color: #ffe4e1;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                }}
                .info-row {{
                    margin-bottom: 10px;
                    display: flex;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #c2185b;
                    min-width: 100px;
                }}
                .info-value {{
                    color: #1e293b;
                }}
                .content-section {{
                    margin-top: 25px;
                }}
                .content-label {{
                    font-weight: 600;
                    color: #c2185b;
                    margin-bottom: 10px;
                    display: block;
                }}
                .content-text {{
                    background-color: #ffe4e1;
                    padding: 15px;
                    border-radius: 6px;
                    border-left: 4px solid #ff69b4;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    line-height: 1.8;
                    color: #1e293b;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ffc0cb;
                    text-align: center;
                    color: #d4a5b8;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>用户反馈</h1>
                </div>
                
                <div class="info-section">
                    <div class="info-row">
                        <span class="info-label">提交时间：</span>
                        <span class="info-value">{current_time}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">提交用户：</span>
                        <span class="info-value">{username}</span>
                    </div>
                    {f'<div class="info-row"><span class="info-label">用户邮箱：</span><span class="info-value">{user_email}</span></div>' if user_email else ''}
                    {f'<div class="info-row"><span class="info-label">联系方式：</span><span class="info-value">{feedback_contact}</span></div>' if feedback_contact else ''}
                </div>
                
                <div class="content-section">
                    <span class="content-label">反馈内容：</span>
                    <div class="content-text">{feedback_content}</div>
                </div>
                
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿直接回复。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 发送邮件到指定邮箱
        recipient_email = '2921323707@qq.com'
        subject = f'用户反馈 - {username}'
        
        try:
            # 如果有图片，将图片路径列表传递给邮件发送函数
            send_email(recipient_email, subject, html_content, 'html', image_paths=image_paths if image_paths else None)
            return jsonify({'success': True, 'message': '反馈提交成功'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'发送邮件失败: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'处理反馈失败: {str(e)}'}), 500

