# -*- coding: utf-8 -*-
"""
QQ邮箱发送功能模块
"""
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
import os
from dotenv import load_dotenv

load_dotenv()


def send_email(to_email, subject, content, content_type='html'):
    """
    发送邮件
    
    Args:
        to_email (str): 收件人邮箱地址
        subject (str): 邮件主题
        content (str): 邮件内容
        content_type (str): 内容类型，'html' 或 'plain'，默认为 'html'
    
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
    
    # 创建邮件
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
