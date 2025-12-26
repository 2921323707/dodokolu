# -*- coding: utf-8 -*-
"""
发送图片/表情包工具函数
"""
import random
import time
from typing import Dict, Any, Optional
from tools.send_pics.emoji_manager import (
    find_matching_emojis,
    get_emoji_info,
    get_emoji_url,
    load_emoji_database,
    get_favorite_images,
    get_favorite_image_url
)


def send_emoji(
    assistant_message: str = None,
    user_message: str = None,
    probability: float = 0.9,
    delay: float = 0.8,
    describe_probability: float = 0.5
) -> Dict[str, Any]:
    """
    发送表情包工具函数
    
    根据AI的回复内容匹配相关表情包，按照指定概率发送。
    如果匹配到表情包，会停留指定时间后返回表情包信息。
    有50%概率对发送的表情包进行二次描述。
    
    Args:
        assistant_message: AI的回复内容，用于匹配相关表情包（优先使用）
        user_message: 用户消息内容（向后兼容，不推荐使用）
        probability: 发送表情包的概率（默认0.9，即90%）
        delay: 停留时间（秒，默认0.8）
        describe_probability: 二次描述的概率（默认0.5，即50%）
    
    Returns:
        dict: 包含表情包信息的字典，如果没有发送则返回空字典
    """
    # 优先使用assistant_message，如果没有则使用user_message（向后兼容）
    message = assistant_message or user_message
    
    if not message:
        print("\n" + "="*60)
        print("❌ [表情包发送] 错误: 未提供消息内容")
        print("="*60 + "\n")
        return {
            "sent": False,
            "message": "未提供消息内容"
        }
    
    print("\n" + "="*60)
    print("🎭 [表情包发送] 开始处理表情包发送请求")
    print("="*60)
    print(f"📝 AI回复内容: {message}")
    if assistant_message:
        print(f"💬 匹配来源: AI的回复")
    elif user_message:
        print(f"💬 匹配来源: 用户消息（向后兼容）")
    print(f"⚙️  发送概率: {probability*100:.0f}%")
    print(f"⏱️  延迟时间: {delay}秒")
    
    # 检查是否应该发送表情包
    random_value = random.random()
    print(f"🎲 随机值: {random_value:.3f} (阈值: {probability:.3f})")
    
    if random_value > probability:
        print("❌ 概率检查未通过，不发送表情包")
        print("="*60 + "\n")
        return {
            "sent": False,
            "message": "未触发表情包发送"
        }
    
    print("✅ 概率检查通过，继续匹配表情包...")
    
    # 查找匹配的表情包
    print(f"🔍 正在匹配表情包...")
    matches = find_matching_emojis(message)
    
    if not matches:
        print("❌ 未找到匹配的表情包")
        print("="*60 + "\n")
        return {
            "sent": False,
            "message": "未找到匹配的表情包"
        }
    
    print(f"✅ 找到 {len(matches)} 个匹配的表情包")
    print(f"📊 匹配结果（前3个）:")
    for i, match in enumerate(matches[:3], 1):
        emoji = match['emoji']
        print(f"   {i}. ID: {emoji.get('id')}, 分数: {match['score']:.3f}, "
              f"描述: {emoji.get('description', '无')[:30]}")
    
    # 选择匹配度最高的表情包
    selected = matches[0]['emoji']
    emoji_id = selected['id']
    matched_score = matches[0]['score']
    
    print(f"\n🎯 选择表情包:")
    print(f"   ID: {emoji_id}")
    print(f"   分类: {selected.get('category', '未知')}")
    print(f"   描述: {selected.get('description', '无描述')}")
    print(f"   匹配分数: {matched_score:.3f}")
    print(f"   URL: {get_emoji_url(emoji_id)}")
    
    # 停留指定时间
    print(f"\n⏳ 等待 {delay} 秒后发送...")
    time.sleep(delay)
    print("✅ 延迟完成，准备发送")
    
    # 构建返回结果
    result = {
        "sent": True,
        "emoji_id": emoji_id,
        "emoji_url": get_emoji_url(emoji_id),
        "category": selected.get('category', '未知'),
        "description": selected.get('description', ''),
        "matched_score": matched_score,
        "delay": delay
    }
    
    # 50%概率进行二次描述
    describe_random = random.random()
    print(f"🎲 二次描述随机值: {describe_random:.3f} (阈值: {describe_probability:.3f})")
    
    if describe_random <= describe_probability:
        result["secondary_description"] = f"发送了表情包：{selected.get('description', '无描述')}"
        print(f"💬 将进行二次描述: {result['secondary_description']}")
    else:
        result["secondary_description"] = None
        print("💬 不进行二次描述")
    
    print(f"\n✅ 表情包发送成功！")
    print("="*60 + "\n")
    
    return result


def send_emoji_by_id(emoji_id: str) -> Dict[str, Any]:
    """
    根据ID直接发送表情包
    
    Args:
        emoji_id: 表情包ID（6位数字，如 "000001"）
    
    Returns:
        dict: 包含表情包信息的字典
    """
    print("\n" + "="*60)
    print("🎭 [表情包发送] 根据ID直接发送表情包")
    print("="*60)
    print(f"🆔 表情包ID: {emoji_id}")
    
    emoji_info = get_emoji_info(emoji_id)
    
    if not emoji_info:
        print(f"❌ 未找到ID为 {emoji_id} 的表情包")
        print("="*60 + "\n")
        return {
            "sent": False,
            "error": f"未找到ID为 {emoji_id} 的表情包"
        }
    
    print(f"✅ 找到表情包:")
    print(f"   分类: {emoji_info.get('category', '未知')}")
    print(f"   描述: {emoji_info.get('description', '无描述')}")
    print(f"   URL: {get_emoji_url(emoji_id)}")
    print(f"✅ 表情包发送成功！")
    print("="*60 + "\n")
    
    return {
        "sent": True,
        "emoji_id": emoji_id,
        "emoji_url": get_emoji_url(emoji_id),
        "category": emoji_info.get('category', '未知'),
        "description": emoji_info.get('description', '')
    }


def send_favorite_image() -> Dict[str, Any]:
    """
    从收藏图片目录中随机选择一张图片发送
    
    当用户询问AI最喜欢的图片时，从 static/imgs/fav_album 目录中随机选择一张图片。
    暂时没有图片描述。
    
    Returns:
        dict: 包含图片信息的字典，如果没有图片则返回错误信息
    """
    print("\n" + "="*60)
    print("🖼️  [收藏图片发送] 开始处理收藏图片发送请求")
    print("="*60)
    
    favorite_images = get_favorite_images()
    print(f"📁 收藏图片目录: static/imgs/fav_album")
    print(f"📚 找到 {len(favorite_images)} 张收藏图片")
    
    if not favorite_images:
        print("❌ 收藏图片目录中没有图片")
        print("="*60 + "\n")
        return {
            "sent": False,
            "error": "收藏图片目录中没有图片"
        }
    
    # 随机选择一张图片
    selected_image = random.choice(favorite_images)
    print(f"🎲 随机选择图片: {selected_image}")
    
    # 构建返回结果
    result = {
        "sent": True,
        "image_filename": selected_image,
        "image_url": get_favorite_image_url(selected_image),
        "description": None  # 暂时没有图片描述
    }
    
    print(f"✅ 图片信息:")
    print(f"   文件名: {result['image_filename']}")
    print(f"   URL: {result['image_url']}")
    print(f"✅ 收藏图片发送成功！")
    print("="*60 + "\n")
    
    return result

