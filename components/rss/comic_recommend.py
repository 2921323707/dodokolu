# -*- coding: utf-8 -*-
"""
番剧推荐脚本
每6小时自动执行（8:00, 14:00, 20:00, 2:00），从RSS源获取最新番剧信息，使用大模型整理后保存
"""
import json
import os
import requests
import feedparser
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import schedule
import time
import logging
import sys

# 处理导入问题：支持直接运行和作为模块导入
try:
    from components.rss.comic_json import txt_to_json
except ImportError:
    # 如果作为模块导入失败，尝试相对导入或添加路径
    try:
        from comic_json import txt_to_json
    except ImportError:
        # 添加项目根目录到路径
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from components.rss.comic_json import txt_to_json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comic_recommend.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# DEEPSEEK API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')


def load_rss_sources():
    """从 src.json 加载 RSS 源"""
    src_file = Path(__file__).parent / 'src.json'
    try:
        with open(src_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        rss_urls = []
        for item in data:
            if '番剧' in item:
                rss_urls.append(item['番剧'])
        logger.info(f"成功加载 {len(rss_urls)} 个 RSS 源")
        return rss_urls
    except Exception as e:
        logger.error(f"加载 RSS 源失败: {e}")
        return []


def fetch_rss_items(rss_url, max_items=20):
    """从 RSS 源获取前 N 条信息"""
    try:
        logger.info(f"正在获取 RSS 源: {rss_url}")
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()
        
        # 解析 RSS
        feed = feedparser.parse(response.content)
        
        items = []
        for entry in feed.entries[:max_items]:
            item = {
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')[:200] if entry.get('summary') else ''  # 限制长度
            }
            items.append(item)
        
        logger.info(f"成功获取 {len(items)} 条 RSS 条目")
        return items
    except Exception as e:
        logger.error(f"获取 RSS 源失败 {rss_url}: {e}")
        return []


def call_deepseek_api(rss_items):
    """调用 DEEPSEEK API 整理番剧信息"""
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置")
    
    # 构建提示词
    items_text = ""
    for i, item in enumerate(rss_items, 1):
        items_text += f"{i}. 标题: {item['title']}\n"
        items_text += f"   更新时间: {item['published']}\n"
        items_text += f"   URL: {item['link']}\n"
        if item['summary']:
            items_text += f"   简介: {item['summary']}\n"
        items_text += "\n"
    
    prompt = f"""请帮我整理以下番剧信息，提取今日推荐的番剧。

【重要格式要求】
输出格式必须严格按照以下格式，每行一个番剧，格式为：
番剧名称 - 更新时间 - URL地址

示例：
进击的巨人 最终季 - 2024-01-15 12:00:00 - https://example.com/episode1
鬼灭之刃 无限列车篇 - 2024-01-14 18:30:00 - https://example.com/episode2

【筛选要求】
1. 只选择最值得推荐的番剧，数量控制在5-10个之间
2. 绝对不要重复，如果有相同的番剧，只保留最新的一条
3. 优先推荐最新更新的番剧
4. 只输出推荐结果，不要添加任何解释性文字
5. 严格按照"番剧名称 - 更新时间 - URL地址"格式输出，使用中文短横线" - "分隔
6. 番剧名称别弄错

以下是 RSS 源获取的番剧信息：

{items_text}

请按照上述格式要求输出推荐结果（只输出推荐列表，不要其他内容）："""

    try:
        client = OpenAI(
            base_url=DEEPSEEK_BASE_URL,
            api_key=DEEPSEEK_API_KEY,
        )
        
        logger.info("正在调用 DEEPSEEK API 整理番剧信息...")
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的番剧推荐助手，擅长整理和筛选优质的番剧内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # 使用较低温度保证输出格式一致性
        )
        
        result = response.choices[0].message.content
        logger.info("成功获取大模型整理结果")
        return result.strip()
    except Exception as e:
        logger.error(f"调用 DEEPSEEK API 失败: {e}")
        raise


def save_recommendation(content):
    """保存推荐内容到文件"""
    # 获取当前日期
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    
    # 创建 data 目录（如果不存在）
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # 文件路径：年份-月份-日期.txt
    file_path = data_dir / f"{date_str}.txt"
    
    # 构建文件内容：开头是更新时间，然后是番剧信息
    current_time = today.strftime("%Y-%m-%d %H:%M:%S")
    file_content = f"更新时间: {current_time}\n\n{content}\n"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        logger.info(f"推荐内容已保存到: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        raise


def run_recommendation():
    """执行完整的推荐流程"""
    from datetime import datetime
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info("=" * 70)
        logger.info(f"📺 [{timestamp}] 开始执行番剧推荐任务...")
        logger.info("=" * 70)
        
        # 1. 加载 RSS 源
        rss_urls = load_rss_sources()
        if not rss_urls:
            logger.warning("   ⚠️  没有找到 RSS 源，任务结束")
            logger.info("=" * 70 + "\n")
            return
        
        logger.info(f"   📡 已加载 {len(rss_urls)} 个 RSS 源")
        
        # 2. 获取所有 RSS 源的信息
        all_items = []
        for rss_url in rss_urls:
            items = fetch_rss_items(rss_url, max_items=20)
            all_items.extend(items)
            logger.info(f"   📥 从 {rss_url} 获取了 {len(items)} 条信息")
        
        if not all_items:
            logger.warning("   ⚠️  未能获取到任何 RSS 条目，任务结束")
            logger.info("=" * 70 + "\n")
            return
        
        logger.info(f"   📊 总共获取 {len(all_items)} 条 RSS 条目")
        
        # 3. 调用大模型整理
        logger.info("   🤖 正在调用大模型整理推荐内容...")
        recommendation_content = call_deepseek_api(all_items)
        
        # 4. 保存到日期文件
        logger.info("   💾 正在保存推荐内容...")
        save_recommendation(recommendation_content)
        
        # 5. 将txt文件转换为json格式
        try:
            data_dir = Path(__file__).parent / 'data'
            json_data = txt_to_json(data_dir=data_dir, auto_save=True)
            logger.info(f"   ✅ JSON文件已成功生成: {json_data.get('date', 'unknown')}.json")
        except Exception as e:
            logger.error(f"   ❌ 转换JSON文件时发生错误: {e}", exc_info=True)
        
        logger.info(f"\n✅ [{timestamp}] 番剧推荐任务执行完成")
        logger.info("=" * 70 + "\n")
        
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.error("=" * 70)
        logger.error(f"❌ [{timestamp}] 执行推荐任务时发生错误: {e}")
        logger.error("=" * 70 + "\n", exc_info=True)


def schedule_job():
    """调度任务：每6小时执行一次（8:00, 14:00, 20:00, 2:00）"""
    # 设置四个时间点执行
    schedule.every().day.at("08:00").do(run_recommendation)
    schedule.every().day.at("14:00").do(run_recommendation)
    schedule.every().day.at("20:00").do(run_recommendation)
    schedule.every().day.at("02:00").do(run_recommendation)
    logger.info("已设置定时任务：每6小时执行番剧推荐（8:00, 14:00, 20:00, 2:00）")
    
    # 保持程序运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


def start_schedule_in_thread():
    """在后台线程中启动定时任务"""
    import threading
    from datetime import datetime
    
    def run_schedule():
        # 设置四个时间点执行
        schedule.every().day.at("08:00").do(run_recommendation)
        schedule.every().day.at("14:00").do(run_recommendation)
        schedule.every().day.at("20:00").do(run_recommendation)
        schedule.every().day.at("02:00").do(run_recommendation)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"   ⏰ [{timestamp}] 定时任务已注册: 每天 8:00、14:00、20:00、2:00 执行")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    import sys
    
    # 如果传入参数 --now，立即执行一次
    if len(sys.argv) > 1 and sys.argv[1] == '--now':
        run_recommendation()
    else:
        # 否则启动定时任务
        logger.info("启动定时任务模式")
        logger.info("如需立即执行一次，请使用: python comic_recommend.py --now")
        schedule_job()

