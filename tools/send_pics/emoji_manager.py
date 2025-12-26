# -*- coding: utf-8 -*-
"""
表情包管理模块
负责加载、匹配和管理表情包
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

# 表情包数据库缓存
_emoji_database = None
_emoji_base_path = None


def get_emoji_base_path() -> Path:
    """获取表情包基础路径"""
    global _emoji_base_path
    if _emoji_base_path is None:
        _emoji_base_path = Path(__file__).parent.parent.parent / 'static' / 'imgs' / '表情包'
    return _emoji_base_path


def load_emoji_database() -> List[Dict[str, Any]]:
    """
    加载表情包数据库
    
    Returns:
        list: 表情包信息列表
    """
    global _emoji_database
    
    if _emoji_database is not None:
        return _emoji_database
    
    json_path = get_emoji_base_path() / 'json_description' / 'emojis.json'
    
    if not json_path.exists():
        print(f"⚠️  [表情包数据库] 警告: JSON文件不存在: {json_path}")
        return []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            _emoji_database = json.load(f)
        print(f"📦 [表情包数据库] 成功加载 {len(_emoji_database)} 个表情包")
        return _emoji_database
    except Exception as e:
        print(f"❌ [表情包数据库] 加载失败: {e}")
        return []


def get_emoji_info(emoji_id: str) -> Optional[Dict[str, Any]]:
    """
    根据ID获取表情包信息
    
    Args:
        emoji_id: 表情包ID（6位数字，如 "000001"）
    
    Returns:
        dict: 表情包信息，如果不存在则返回None
    """
    database = load_emoji_database()
    for emoji in database:
        if emoji.get('id') == emoji_id:
            return emoji
    return None


def find_matching_emojis(user_message: str, threshold: float = 0.15) -> List[Dict[str, Any]]:
    """
    根据用户消息匹配相关表情包
    
    Args:
        user_message: 用户消息
        threshold: 匹配阈值（0-1），默认0.15（降低阈值使匹配更容易）
    
    Returns:
        list: 匹配的表情包列表，按匹配度排序
    """
    database = load_emoji_database()
    if not database:
        print("   ⚠️  表情包数据库为空")
        return []
    
    print(f"   📚 表情包数据库: {len(database)} 个表情包")
    print(f"   🎯 匹配阈值: {threshold}")
    
    user_message_lower = user_message.lower()
    matches = []
    
    for emoji in database:
        score = 0.0
        description = emoji.get('description', '').lower()
        category = emoji.get('category', '').lower()
        keywords = [k.lower() for k in emoji.get('keywords', [])]
        text_content = (emoji.get('text_content') or '').lower()
        usage = (emoji.get('usage') or '').lower()
        visual_description = (emoji.get('visual_description') or '').lower()
        
        # 检查描述是否包含用户消息中的关键词
        words = re.findall(r'\w+', user_message_lower)
        # 也提取中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', user_message_lower)
        all_words = words + chinese_chars
        
        for word in all_words:
            # 降低单词长度要求，单个中文字符也可以匹配
            min_length = 1 if len(re.findall(r'[\u4e00-\u9fff]', word)) > 0 else 2
            if len(word) >= min_length:
                # 关键词匹配（权重最高）
                if word in keywords:
                    score += 0.6
                # 文本内容匹配（权重较高）
                if text_content and word in text_content:
                    score += 0.5
                # 描述匹配
                if word in description:
                    score += 0.4
                # 使用场景匹配
                if usage and word in usage:
                    score += 0.4
                # 分类匹配
                if word in category:
                    score += 0.3
                # 视觉描述匹配（权重较低）
                if visual_description and word in visual_description:
                    score += 0.2
        
        # 检查完整短语匹配（提高匹配度）
        if description and any(word in description for word in all_words if len(word) >= 2):
            score += 0.3
        if text_content and any(word in text_content for word in all_words if len(word) >= 2):
            score += 0.4
        
        # 如果用户消息较短，降低匹配要求
        if len(user_message_lower) <= 10:
            score += 0.2
        
        # 如果分数超过阈值，添加到匹配列表
        if score >= threshold:
            matches.append({
                'emoji': emoji,
                'score': score
            })
            # 显示匹配详情（仅显示前5个）
            if len(matches) <= 5:
                print(f"      ✓ ID {emoji.get('id')}: 分数 {score:.3f} - {emoji.get('description', '无')[:40]}")
    
    # 按分数降序排序
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    if matches:
        print(f"   ✅ 匹配完成: 共 {len(matches)} 个表情包通过阈值")
    else:
        print(f"   ❌ 匹配完成: 没有表情包达到阈值 {threshold}")
    
    return matches


def get_emoji_file_path(emoji_id: str) -> Optional[Path]:
    """
    获取表情包文件路径
    
    Args:
        emoji_id: 表情包ID（6位数字，如 "000001"）
    
    Returns:
        Path: 表情包文件路径，如果不存在则返回None
    """
    emoji_file = get_emoji_base_path() / 'src' / 'all' / f"{emoji_id}id.jpg"
    if emoji_file.exists():
        return emoji_file
    return None


def get_emoji_url(emoji_id: str) -> str:
    """
    获取表情包的URL路径
    
    Args:
        emoji_id: 表情包ID
    
    Returns:
        str: 表情包的URL路径
    """
    return f"/static/imgs/表情包/src/all/{emoji_id}id.jpg"


def get_favorite_images() -> List[str]:
    """
    获取收藏图片目录中的所有图片文件名列表
    
    Returns:
        list: 图片文件名列表（不包含路径）
    """
    # 收藏图片目录已转移到 static/imgs/fav_album
    base_path = Path(__file__).parent.parent.parent / 'static' / 'imgs' / 'fav_album'
    fav_path = base_path
    
    if not fav_path.exists():
        return []
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    image_files = []
    for file in fav_path.iterdir():
        if file.is_file() and file.suffix.lower() in image_extensions:
            image_files.append(file.name)
    
    return image_files


def get_favorite_image_url(filename: str) -> str:
    """
    获取收藏图片的URL路径
    
    Args:
        filename: 图片文件名
    
    Returns:
        str: 图片的URL路径
    """
    # 对文件名进行URL编码，处理中文和特殊字符
    from urllib.parse import quote
    encoded_filename = quote(filename, safe='')
    return f"/static/imgs/fav_album/{encoded_filename}"
