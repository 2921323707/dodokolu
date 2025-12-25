# -*- coding: utf-8 -*-
"""
提醒页面路由
提供番剧推荐数据和节日信息
"""
from flask import Blueprint, jsonify, render_template
from pathlib import Path
import json
from datetime import datetime
import calendar

alert_bp = Blueprint('alert', __name__, url_prefix='/alert')


@alert_bp.route('')
@alert_bp.route('/')
def alert_page():
    """提醒页面"""
    return render_template('alert.html')


def get_latest_comic_json():
    """获取最新的番剧JSON文件"""
    data_dir = Path(__file__).parent.parent.parent / 'components' / 'rss' / 'data' / 'json'
    
    if not data_dir.exists():
        return None
    
    # 查找所有JSON文件
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        return None
    
    # 按文件名排序（文件名格式：YYYY-MM-DD.json）
    json_files.sort(reverse=True)
    latest_file = json_files[0]
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取JSON文件失败: {e}")
        return None


def get_upcoming_holidays():
    """获取临近的节日（未来30天内）"""
    from datetime import date
    today = date.today()  # 只使用日期部分，不包含时间
    current_year = today.year
    
    # 定义节日列表（名称, 月, 日）
    holidays = [
        ("元旦", 1, 1),
        ("情人节", 2, 14),
        ("妇女节", 3, 8),
        ("植树节", 3, 12),
        ("清明节", 4, 5),
        ("劳动节", 5, 1),
        ("青年节", 5, 4),
        ("母亲节", 5, 15),  # 每年5月第二个星期日，这里简化为固定日期
        ("儿童节", 6, 1),
        ("端午节", 6, 10),  # 2024年，需要根据年份计算
        ("父亲节", 6, 16),  # 每年6月第三个星期日，这里简化为固定日期
        ("七夕节", 8, 10),  # 农历，这里简化为公历日期
        ("中秋节", 9, 17),  # 农历，这里简化为公历日期
        ("国庆节", 10, 1),
        ("万圣节", 10, 31),
        ("双十一", 11, 11),
        ("圣诞节", 12, 25),
        ("跨年", 12, 31),
    ]
    
    upcoming = []
    
    for holiday_name, month, day in holidays:
        # 计算今年的日期
        try:
            holiday_date = date(current_year, month, day)
            days_until = (holiday_date - today).days
            
            # 如果今年的节日已过，计算明年的
            if days_until < 0:
                holiday_date = date(current_year + 1, month, day)
                days_until = (holiday_date - today).days
            
            # 只返回未来30天内的节日（包括今天）
            if days_until >= 0 and days_until <= 30:
                upcoming.append({
                    "name": holiday_name,
                    "date": holiday_date.strftime("%Y-%m-%d"),
                    "days_until": days_until,
                    "display_date": holiday_date.strftime("%m.%d")  # 格式：MM.DD
                })
        except ValueError:
            # 日期无效（如2月30日），跳过
            continue
    
    # 按天数排序
    upcoming.sort(key=lambda x: x["days_until"])
    
    return upcoming[:1] if upcoming else []  # 只返回最近的1个节日


@alert_bp.route('/api/comics')
def get_comics():
    """获取最新番剧数据API"""
    comic_data = get_latest_comic_json()
    
    if comic_data:
        return jsonify({
            "success": True,
            "data": comic_data
        })
    else:
        return jsonify({
            "success": False,
            "message": "暂无番剧数据",
            "data": None
        }), 404


@alert_bp.route('/api/holidays')
def get_holidays():
    """获取临近节日数据API"""
    holidays = get_upcoming_holidays()
    
    return jsonify({
        "success": True,
        "data": holidays
    })

