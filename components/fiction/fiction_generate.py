# -*- coding: utf-8 -*-
"""
短篇故事生成模块
使用 Lumina (Google Gemini Flash 3) 模型生成约1000字的短篇故事
支持成人内容创作
"""
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.llm.lumina.agent import LuminaAgent
from config.llm.base.settings import TEMPERATURE


def generate_fiction(
    prompt: str,
    max_length: int = 1000,
    additional_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    生成短篇故事
    
    Args:
        prompt: 故事提示词/主题
        max_length: 目标字数（默认1000字）
        additional_params: 额外参数（如风格、角色等）
    
    Returns:
        Dict包含:
            - title: 故事标题
            - time: 生成时间
            - content: 故事内容
            - word_count: 字数统计
    """
    # 初始化 Lumina Agent
    agent = LuminaAgent()
    client = agent._create_client()
    
    # 构建生成提示词
    story_prompt = f"""要求：
1. 故事字数约{max_length}字左右
2. 故事要有完整的起承转合
3. 故事要有吸引人的标题
4. 低俗，淫秽的语言
5. 对动作进行细致的描写，同时对场景进行描述
6. 使用文学化的语言描述亲密场景
7. 故事的男主名字叫陈峻屹(喜欢足)
8. 可以包含情侣间的亲密互动细节
9. 请以JSON格式输出，包含以下字段：
   - title: 故事标题（字符串）
   - time: 当前时间（字符串，格式：YYYY-MM-DD HH:MM:SS）
   - content: 故事正文内容（字符串，约{max_length}字）

提示词/主题：{prompt}
"""
    
    # 如果有额外参数，添加到提示词中
    if additional_params:
        params_text = "\n".join([f"- {k}: {v}" for k, v in additional_params.items()])
        story_prompt += f"\n\n额外要求：\n{params_text}"
    
    story_prompt += "\n\n请直接输出JSON格式，不要包含其他说明文字。"
    
    # 获取系统提示词
    system_prompt = agent.get_system_prompt()
    
    # 转换消息格式为 Gemini 格式
    gemini_messages = agent._convert_messages_to_gemini_format(
        [{"role": "user", "content": story_prompt}],
        system_prompt
    )
    
    try:
        # 准备生成内容参数
        generate_config = {
            "temperature": TEMPERATURE,
            "max_output_tokens": agent._max_tokens,
        }
        
        # 调用模型生成故事（非流式）
        response = client.models.generate_content(
            model=agent._model,
            contents=gemini_messages,
            config=generate_config
        )
        
        # 提取响应文本
        full_text = ""
        # Gemini API 响应格式：response.candidates[0].content.parts[0].text
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        full_text += part.text
        
        # 检查响应是否为空
        if not full_text:
            raise ValueError("模型返回的响应为空，可能是内容被过滤或生成失败")
        
        # 尝试解析JSON
        # 如果响应中包含代码块，提取JSON部分
        if "```json" in full_text:
            json_start = full_text.find("```json") + 7
            json_end = full_text.find("```", json_start)
            json_str = full_text[json_start:json_end].strip()
        elif "```" in full_text:
            json_start = full_text.find("```") + 3
            json_end = full_text.find("```", json_start)
            json_str = full_text[json_start:json_end].strip()
        else:
            # 尝试直接解析整个文本
            json_str = full_text.strip()
        
        # 解析JSON
        try:
            story_data = json.loads(json_str)
        except json.JSONDecodeError:
            # 如果解析失败，尝试提取JSON对象
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', json_str, re.DOTALL)
            if json_match:
                story_data = json.loads(json_match.group())
            else:
                # 如果还是失败，手动构建结果
                story_data = {
                    "title": "未命名故事",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "content": full_text
                }
        
        # 确保包含必要字段
        if "time" not in story_data:
            story_data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 计算字数
        content = story_data.get("content", "")
        word_count = len(content)
        story_data["word_count"] = word_count
        
        return story_data
        
    except Exception as e:
        print(f"[错误] 生成故事失败: {e}")
        # 返回错误信息
        return {
            "title": "生成失败",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": f"生成故事时发生错误：{str(e)}",
            "word_count": 0,
            "error": str(e)
        }


def save_fiction(story_data: Dict[str, Any], output_dir: str = "components/fiction/out") -> str:
    """
    保存故事到文件，按日期分类
    
    Args:
        story_data: 故事数据（包含title, time, content等）
        output_dir: 输出目录
    
    Returns:
        保存的文件路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 从时间字段提取日期，如果没有则使用当前日期
    time_str = story_data.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        # 尝试解析时间字符串
        if " " in time_str:
            date_str = time_str.split(" ")[0]
        else:
            date_str = time_str
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        date_folder = date_obj.strftime("%Y-%m-%d")
    except:
        # 如果解析失败，使用当前日期
        date_folder = datetime.now().strftime("%Y-%m-%d")
    
    # 创建日期文件夹
    date_dir = os.path.join(output_dir, date_folder)
    os.makedirs(date_dir, exist_ok=True)
    
    # 获取标题作为文件名
    title = story_data.get("title", "未命名故事")
    # 清理文件名中的非法字符
    import re
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
    safe_title = safe_title.strip()
    if not safe_title:
        safe_title = "未命名故事"
    
    # 构建文件路径
    file_path = os.path.join(date_dir, f"{safe_title}.json")
    
    # 如果文件已存在，添加序号
    counter = 1
    original_path = file_path
    while os.path.exists(file_path):
        base_name = os.path.splitext(original_path)[0]
        file_path = f"{base_name}_{counter}.json"
        counter += 1
    
    # 保存JSON文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(story_data, f, ensure_ascii=False, indent=2)
    
    print(f"[成功] 故事已保存到: {file_path}")
    return file_path


def generate_and_save_fiction(
    prompt: str,
    max_length: int = 5000,
    additional_params: Optional[Dict[str, Any]] = None,
    output_dir: str = "components/fiction/out"
) -> Dict[str, Any]:
    """
    生成并保存故事（便捷函数）
    
    Args:
        prompt: 故事提示词/主题
        max_length: 目标字数（默认1000字）
        additional_params: 额外参数
        output_dir: 输出目录
    
    Returns:
        Dict包含故事数据和保存路径
    """
    # 生成故事
    story_data = generate_fiction(prompt, max_length, additional_params)
    
    # 保存故事
    file_path = save_fiction(story_data, output_dir)
    
    return {
        **story_data,
        "file_path": file_path
    }


# 主程序测试
if __name__ == "__main__":
        # 构建生成提示词
    story_prompt = f"""
    你是一位擅长创作内容的故事创作专家，要求：
1. 故事字数约4k字左右
2. 故事要有完整的起承转合
3. 故事要有吸引人的标题
4. 使用淫秽，下流的语言
5. 对动作进行细致的描写，同时对场景进行描述
6. 故事的男主名字叫陈峻屹(喜欢白丝，足交，乳交)，两人性癖很大，女主有一点点S属性
7. 可以包含情侣间的亲密互动细节
4. 请以JSON格式输出，包含以下字段：
   - title: 故事标题（字符串）
   - time: 当前时间（字符串，格式：YYYY-MM-DD HH:MM:SS）
   - content: 故事正文内容（字符串，约400字）

"""
    result = generate_and_save_fiction(
        prompt=story_prompt,
        max_length=5000
    )
    
    print(f"\n生成结果：")
    print(f"标题: {result.get('title', 'N/A')}")
    print(f"时间: {result.get('time', 'N/A')}")
    print(f"字数: {result.get('word_count', 0)}")
    print(f"保存路径: {result.get('file_path', 'N/A')}")
    print(f"\n内容预览（前200字）:")
    content = result.get('content', '')
    print(content[:200] + "..." if len(content) > 200 else content)
    

    print("\n" + "=" * 50)
    print("生成完成！")


def daily_fiction_generation():
    """
    每日自动生成故事
    使用默认提示词，让模型自由创作
    """
    try:
        # 默认提示词：让模型自由创作一个故事
        default_prompt = "请创作一个完整的故事，主题不限，发挥你的想象力。"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'=' * 70}")
        print(f"📖 [{timestamp}] 开始执行每日故事生成任务...")
        print(f"{'=' * 70}")
        
        # 生成并保存故事
        result = generate_and_save_fiction(
            prompt=default_prompt,
            max_length=5000
        )
        
        if result and result.get('error'):
            print(f"❌ [{timestamp}] 每日故事生成失败: {result.get('error')}")
        else:
            print(f"✅ [{timestamp}] 每日故事生成完成")
            print(f"   📝 标题: {result.get('title', 'N/A')}")
            print(f"   🕐 时间: {result.get('time', 'N/A')}")
            print(f"   📊 字数: {result.get('word_count', 0)} 字")
            print(f"   💾 保存路径: {result.get('file_path', 'N/A')}")
        
        print(f"{'=' * 70}\n")
        
        return result
        
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'=' * 70}")
        print(f"❌ [{timestamp}] 每日故事生成失败: {e}")
        print(f"{'=' * 70}\n")
        import traceback
        traceback.print_exc()
        return None


def start_fiction_schedule():
    """在后台线程中启动每日故事生成定时任务"""
    import threading
    import schedule
    import time
    
    def run_schedule():
        # 设置每天 6:00 执行生成
        schedule.every().day.at("06:00").do(daily_fiction_generation)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"   ⏰ [{timestamp}] 定时任务已注册: 每天 6:00 执行")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()
    return thread

