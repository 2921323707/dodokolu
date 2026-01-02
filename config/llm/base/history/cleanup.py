# -*- coding: utf-8 -*-
"""
清理空的历史记录文件
每天 0:00 自动删除所有空的 JSON 文件
"""
import json
import logging
from pathlib import Path

# 历史记录文件存储目录（与 history/__init__.py 中的定义保持一致）
HISTORY_DIR = Path(__file__).parent.parent.parent.parent.parent / 'database' / 'history' / 'chat_history'

logger = logging.getLogger(__name__)


def is_empty_json_file(file_path):
    """
    检查 JSON 文件是否为空
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 如果文件为空（内容为 [] 或文件不存在），返回 True
    """
    try:
        if not file_path.exists():
            return True
        
        # 检查文件大小，如果文件很小（只有 []），可能是空文件
        if file_path.stat().st_size <= 2:  # [] 只有 2 个字符
            return True
        
        # 读取文件内容并检查
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # 如果内容为空或只是 []
            if not content or content == '[]':
                return True
            
            # 尝试解析 JSON，如果是空数组，则认为是空文件
            try:
                data = json.loads(content)
                if isinstance(data, list) and len(data) == 0:
                    return True
            except json.JSONDecodeError:
                # 如果 JSON 解析失败，可能是损坏的文件，也删除
                return True
        
        return False
    except Exception as e:
        logger.error(f'检查文件 {file_path} 时出错: {e}')
        return False


def cleanup_empty_json_files():
    """
    清理所有空的 JSON 文件
    
    Returns:
        dict: 清理结果统计
    """
    from datetime import datetime
    
    deleted_count = 0
    error_count = 0
    total_size_freed = 0
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info("=" * 70)
        logger.info(f"🧹 [{timestamp}] 开始执行历史记录清理任务...")
        logger.info("=" * 70)
        
        if not HISTORY_DIR.exists():
            logger.info(f'   ℹ️  历史记录目录不存在: {HISTORY_DIR}')
            logger.info("=" * 70 + "\n")
            return {
                'success': True,
                'deleted_count': 0,
                'error_count': 0,
                'total_size_freed': 0,
                'message': '历史记录目录不存在'
            }
        
        # 遍历所有用户文件夹
        for user_dir in HISTORY_DIR.iterdir():
            if not user_dir.is_dir():
                continue
            
            # 遍历用户文件夹中的所有 JSON 文件
            for json_file in user_dir.glob('*.json'):
                try:
                    # 检查文件是否为空
                    if is_empty_json_file(json_file):
                        # 获取文件大小（用于统计）
                        file_size = json_file.stat().st_size
                        # 删除文件
                        json_file.unlink()
                        deleted_count += 1
                        total_size_freed += file_size
                        logger.info(f'   🗑️  已删除空文件: {json_file.name}')
                except Exception as e:
                    error_count += 1
                    logger.error(f'   ❌ 删除文件 {json_file.name} 时出错: {e}')
        
        # 格式化文件大小
        size_str = f"{total_size_freed} 字节"
        if total_size_freed > 1024:
            size_str = f"{total_size_freed / 1024:.2f} KB"
        if total_size_freed > 1024 * 1024:
            size_str = f"{total_size_freed / (1024 * 1024):.2f} MB"
        
        result = {
            'success': True,
            'deleted_count': deleted_count,
            'error_count': error_count,
            'total_size_freed': total_size_freed,
            'message': f'清理完成：删除了 {deleted_count} 个空文件，释放了 {size_str}'
        }
        
        logger.info(f"\n📊 任务统计:")
        logger.info(f"   ✅ 删除文件数: {deleted_count}")
        logger.info(f"   ❌ 错误数量: {error_count}")
        logger.info(f"   💾 释放空间: {size_str}")
        logger.info("=" * 70 + "\n")
        
        return result
        
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f'清理空文件时发生错误: {e}'
        logger.error("=" * 70)
        logger.error(f"❌ [{timestamp}] {error_msg}")
        logger.error("=" * 70 + "\n", exc_info=True)
        return {
            'success': False,
            'deleted_count': deleted_count,
            'error_count': error_count,
            'total_size_freed': total_size_freed,
            'message': error_msg
        }


def start_cleanup_schedule():
    """
    启动定时清理任务（在后台线程中运行）
    每天 0:00 执行清理
    """
    import threading
    import schedule
    import time
    from datetime import datetime
    
    def run_schedule():
        # 设置每天 0:00 执行清理
        schedule.every().day.at("00:00").do(cleanup_empty_json_files)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"   ⏰ [{timestamp}] 定时任务已注册: 每天 0:00 执行")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 如果传入参数 --now，立即执行一次
    if len(sys.argv) > 1 and sys.argv[1] == '--now':
        print("开始清理空的 JSON 文件...")
        result = cleanup_empty_json_files()
        print(result['message'])
    else:
        # 否则启动定时任务
        print("启动定时任务模式")
        print("如需立即执行一次，请使用: python cleanup.py --now")
        start_cleanup_schedule()
        # 保持程序运行
        try:
            while True:
                import time
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n程序已停止")

