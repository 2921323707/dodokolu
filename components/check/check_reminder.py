# -*- coding: utf-8 -*-
"""
打卡提醒定时任务
每天9:00、15:00、21:00检查打卡状态，如果未完成则发送微信推送
"""
import schedule
import time
import threading
from datetime import date, datetime
from database import get_db_connection
from components.check.message_wechat_push import push_wechat_message


def check_and_remind():
    """检查今日打卡状态并发送提醒"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'=' * 70}")
        print(f"📋 [{timestamp}] 开始执行打卡提醒任务...")
        print(f"{'=' * 70}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            today = date.today().isoformat()
            
            # 获取所有活跃用户
            cursor.execute('''
                SELECT DISTINCT user_id FROM check_list WHERE is_active = 1
            ''')
            
            users = cursor.fetchall()
            total_users = len(users)
            success_count = 0
            failed_count = 0
            
            for user_row in users:
                user_id = user_row['user_id']
                
                # 获取该用户的待打卡清单
                cursor.execute('''
                    SELECT id, app_name
                    FROM check_list
                    WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
                
                check_items = cursor.fetchall()
                
                if not check_items:
                    continue
                
                # 检查每个清单项的今日打卡状态
                pending_items = []
                completed_items = []
                
                for item in check_items:
                    item_id = item['id']
                    app_name = item['app_name']
                    
                    # 查询今日打卡记录
                    cursor.execute('''
                        SELECT check_status
                        FROM check_record
                        WHERE user_id = ? AND check_list_id = ? AND check_date = ?
                    ''', (user_id, item_id, today))
                    
                    record = cursor.fetchone()
                    if record and record['check_status'] == 'completed':
                        completed_items.append(app_name)
                    else:
                        pending_items.append(app_name)
                
                # 如果有未完成的打卡项，发送提醒
                if pending_items:
                    # 获取用户邮箱（用于标识）
                    cursor.execute('''
                        SELECT email FROM user_profile WHERE id = ?
                    ''', (user_id,))
                    
                    user = cursor.fetchone()
                    if not user:
                        continue
                    
                    # 构建提醒消息
                    title = "📋 打卡提醒"
                    content = f"今日打卡状态检查\n\n"
                    content += f"✅ 已完成 ({len(completed_items)}/{len(check_items)}):\n"
                    if completed_items:
                        for app in completed_items:
                            content += f"  • {app}\n"
                    else:
                        content += "  暂无\n"
                    
                    content += f"\n⏰ 待完成 ({len(pending_items)}/{len(check_items)}):\n"
                    for app in pending_items:
                        content += f"  • {app}\n"
                    
                    content += f"\n请及时完成打卡任务！"
                    
                    # 发送微信推送
                    result = push_wechat_message(title=title, content=content)
                    
                    if result.get('success'):
                        success_count += 1
                        print(f"   ✅ 用户 {user['email']} - 提醒发送成功 ({len(pending_items)} 项待完成)")
                    else:
                        failed_count += 1
                        print(f"   ❌ 用户 {user['email']} - 提醒发送失败: {result.get('error_message')}")
            
            print(f"\n📊 任务统计: 总用户 {total_users}, 成功 {success_count}, 失败 {failed_count}")
            print(f"{'=' * 70}\n")
        
        finally:
            conn.close()
    
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'=' * 70}")
        print(f"❌ [{timestamp}] 打卡提醒任务执行失败: {str(e)}")
        print(f"{'=' * 70}\n")
        import traceback
        traceback.print_exc()


def start_check_reminder_schedule():
    """在后台线程中启动打卡提醒定时任务"""
    def run_schedule():
        # 设置三个时间点执行：9:00、15:00、21:00
        schedule.every().day.at("09:00").do(check_and_remind)
        schedule.every().day.at("15:00").do(check_and_remind)
        schedule.every().day.at("21:00").do(check_and_remind)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"   ⏰ [{timestamp}] 定时任务已注册: 每天 9:00、15:00、21:00 执行")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    """直接运行此文件时进行测试"""
    import sys
    
    # 如果传入参数 --now，立即执行一次
    if len(sys.argv) > 1 and sys.argv[1] == '--now':
        print("立即执行打卡提醒检查...")
        check_and_remind()
    else:
        # 否则启动定时任务
        print("启动定时任务模式")
        print("如需立即执行一次，请使用: python check_reminder.py --now")
        start_check_reminder_schedule()
        # 保持主线程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n用户中断任务")

