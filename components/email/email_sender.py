# -*- coding: utf-8 -*-
"""
QQ邮箱发送功能模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from email.header import Header
import os
from dotenv import load_dotenv

load_dotenv()


def send_email(to_email, subject, content, content_type='html', image_paths=None):
    """
    发送邮件
    
    Args:
        to_email (str): 收件人邮箱地址
        subject (str): 邮件主题
        content (str): 邮件内容
        content_type (str): 内容类型，'html' 或 'plain'，默认为 'html'
        image_paths (list): 可选，图片文件路径列表，将作为附件发送
    
    Returns:
        bool: 发送成功返回 True
    """
    # 读取配置
    smtp_server = os.getenv('QQ_EMAIL_SMTP_SERVER', 'smtp.qq.com')
    smtp_port = int(os.getenv('QQ_EMAIL_SMTP_PORT', '587'))
    sender_email = os.getenv('QQ_EMAIL_SENDER')
    sender_password = os.getenv('QQ_EMAIL_PASSWORD')
    sender_name = os.getenv('QQ_EMAIL_SENDER_NAME', '系统通知')
    
    if not sender_email or not sender_password:
        raise ValueError("请在 .env 文件中配置 QQ_EMAIL_SENDER 和 QQ_EMAIL_PASSWORD")
    
    # 检查是否有有效的图片附件
    valid_image_paths = []
    if image_paths:
        if isinstance(image_paths, str):
            # 兼容旧版本，单个路径
            if os.path.exists(image_paths):
                valid_image_paths = [image_paths]
        elif isinstance(image_paths, list):
            # 新版本，路径列表
            valid_image_paths = [path for path in image_paths if path and os.path.exists(path)]
    
    # 创建邮件（如果有附件，使用 MIMEMultipart）
    if valid_image_paths:
        message = MIMEMultipart()
        message['From'] = formataddr((sender_name, sender_email))
        message['To'] = to_email
        message['Subject'] = Header(subject, 'utf-8')
        
        # 添加邮件正文
        body = MIMEText(content, content_type, 'utf-8')
        message.attach(body)
        
        # 添加所有图片附件
        for image_path in valid_image_paths:
            file_ext = os.path.splitext(image_path)[1][1:].lower()
            # 将 jpg 转换为 jpeg（MIME 类型标准）
            if file_ext == 'jpg':
                mime_type = 'jpeg'
            else:
                mime_type = file_ext
            
            with open(image_path, 'rb') as f:
                mime = MIMEBase('image', mime_type)
                mime.set_payload(f.read())
                encoders.encode_base64(mime)
                mime.add_header('Content-Disposition', f'attachment; filename={os.path.basename(image_path)}')
                message.attach(mime)
    else:
        # 没有附件时使用简单的 MIMEText
        message = MIMEText(content, content_type, 'utf-8')
        message['From'] = formataddr((sender_name, sender_email))
        message['To'] = to_email
        message['Subject'] = Header(subject, 'utf-8')
    
    # 发送邮件
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [to_email], message.as_string())
        server.quit()
        return True
    except Exception as e:
        raise Exception(f"发送邮件失败: {str(e)}")


def send_verification_code(to_email, code):
    """
    发送验证码邮件
    
    Args:
        to_email (str): 收件人邮箱地址
        code (str): 验证码
    
    Returns:
        bool: 发送成功返回 True
    """
    subject = "dodokolu注册验证码"
    content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2196F3;">dodokolu通知</h2>
        <p>您的验证码是：</p>
        <div style="background-color: #f4f4f4; padding: 15px; text-align: center; margin: 20px 0; border-radius: 5px;">
            <h1 style="color: #2196F3; margin: 0; font-size: 32px;">{code}</h1>
        </div>
        <p style="color: #666; font-size: 12px;">验证码有效期为10分钟，请勿泄露给他人。</p>
    </body>
    </html>
    """
    return send_email(to_email, subject, content, 'html')
