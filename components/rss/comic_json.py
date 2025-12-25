# -*- coding: utf-8 -*-
"""
提取番剧名称，更新时间，URL地址，转化为json格式
读取 data/ 目录下今日最新的 txt 文件并转换为 JSON
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def find_latest_txt_file(data_dir: Path) -> Path:
    """找到 data 目录下最新的 txt 文件（按文件名日期）"""
    txt_files = list(data_dir.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"在 {data_dir} 目录下未找到任何 txt 文件")
    
    # 按文件名排序（文件名格式：YYYY-MM-DD.txt）
    txt_files.sort(reverse=True)
    return txt_files[0]


def parse_txt_file(file_path: Path) -> Dict[str, Any]:
    """解析 txt 文件，提取番剧信息"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 提取文件更新时间（第一行）
    update_time = ""
    if lines and lines[0].startswith("更新时间:"):
        update_time = lines[0].replace("更新时间:", "").strip()
    
    # 提取日期（从文件名）
    date_str = file_path.stem  # 去掉 .txt 扩展名
    
    # 解析番剧信息（从第3行开始，跳过空行）
    animes = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("更新时间:"):
            continue
        
        # 解析格式：番剧名称 - 更新时间 - URL地址
        # 使用正则表达式匹配，因为番剧名称可能包含 " - "
        # 匹配模式：开头是番剧名称（可能包含空格和短横线），然后是两个 " - " 分隔符
        match = re.match(r'^(.+?)\s+-\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+-\s+(https?://.+)', line)
        if match:
            name = match.group(1).strip()
            anime_update_time = match.group(2).strip()
            url = match.group(3).strip()
            
            animes.append({
                "name": name,
                "update_time": anime_update_time,
                "url": url
            })
        else:
            # 如果正则匹配失败，尝试简单的 split（可能格式不完全一致）
            parts = [p.strip() for p in line.split(" - ", 2)]
            if len(parts) >= 3:
                animes.append({
                    "name": parts[0],
                    "update_time": parts[1],
                    "url": parts[2]
                })
    
    return {
        "date": date_str,
        "file_update_time": update_time,
        "animes": animes
    }


def txt_to_json(data_dir: Path = None, output_file: Path = None, auto_save: bool = True) -> Dict[str, Any]:
    """
    读取 data/ 目录下今日最新的 txt 文件，提取字段转化为 JSON
    
    Args:
        data_dir: data 目录路径，默认为脚本同级目录下的 data 文件夹
        output_file: 输出 JSON 文件路径，如果为 None 且 auto_save=True，则自动保存到 data/json/日期.json
        auto_save: 是否自动保存文件，默认为 True
    
    Returns:
        解析后的 JSON 字典
    """
    if data_dir is None:
        data_dir = Path(__file__).parent / 'data'
    
    # 找到最新的 txt 文件
    latest_file = find_latest_txt_file(data_dir)
    print(f"读取文件: {latest_file}")
    
    # 解析文件
    result = parse_txt_file(latest_file)
    
    # 如果需要保存文件
    if auto_save or output_file:
        if output_file is None:
            # 自动保存到 data/json/日期.json
            json_dir = data_dir / 'json'
            json_dir.mkdir(exist_ok=True)  # 创建目录（如果不存在）
            output_file = json_dir / f"{result['date']}.json"
        
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"JSON 已保存到: {output_file}")
    
    return result


if __name__ == "__main__":
    # 示例用法
    try:
        # 转换为 JSON（自动保存到 data/json/日期.json）
        json_data = txt_to_json()
        
        # 输出到控制台
        print("\n提取的 JSON 数据：")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"错误: {e}")
