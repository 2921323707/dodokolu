# -*- coding: utf-8 -*-
"""
相册工具函数和常量
"""
from pathlib import Path
import os


# 分类映射
CATEGORY_MAP = {
    'anime': 'anime',
    'wallpaper': 'wallpaper',
    'photo': 'photo',
    'scene': 'scene'
}

# 支持的图片格式
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


def get_base_dir(category):
    """获取指定分类的图片目录路径"""
    if category not in CATEGORY_MAP:
        return None
    return Path(__file__).parent.parent.parent / 'static' / 'imgs' / 'album' / CATEGORY_MAP[category]


def check_image_permission(category, image_type, is_logged_in, is_admin):
    """
    检查图片权限
    
    Args:
        category: 分类（anime, photo, wallpaper, scene）
        image_type: 图片类型（normal, abnormal, other）
        is_logged_in: 是否已登录
        is_admin: 是否是管理员
    
    Returns:
        tuple: (should_include, needs_blur)
            should_include: 是否应该包含该图片
            needs_blur: 是否需要模糊显示
    """
    should_include = False
    needs_blur = False
    
    if category == 'anime':
        # anime: 未登录时模糊显示，登录后非管理员只能看normal，管理员可以看全部
        if image_type == 'normal':
            if is_logged_in:
                should_include = True
            else:
                # 未登录：返回但标记需要模糊
                should_include = True
                needs_blur = True
        elif image_type == 'abnormal':
            if is_admin:
                should_include = True
            else:
                # 登录但非管理员或未登录：不返回abnormal图片
                should_include = False
        else:
            # 其他类型：未登录时模糊，登录后正常
            if is_logged_in:
                should_include = True
            else:
                should_include = True
                needs_blur = True
    elif category == 'photo':
        # photo: 未登录时模糊显示，登录后非管理员只能看normal，管理员可以看全部
        if image_type == 'normal':
            if is_logged_in:
                should_include = True
            else:
                # 未登录：返回但标记需要模糊
                should_include = True
                needs_blur = True
        elif image_type == 'abnormal':
            if is_admin:
                should_include = True
            else:
                # 登录但非管理员或未登录：不返回abnormal图片
                should_include = False
        else:
            # 其他类型：未登录时模糊，登录后正常
            if is_logged_in:
                should_include = True
            else:
                should_include = True
                needs_blur = True
    elif category == 'wallpaper':
        # wallpaper: 无需登录，所有人都可以看
        should_include = True
    elif category == 'scene':
        # scene: 无需登录，所有人都可以看
        should_include = True
    
    return should_include, needs_blur

