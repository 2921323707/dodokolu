# -*- coding: utf-8 -*-
"""
小说阅读功能API路由
处理小说列表获取和内容读取
"""
import os
import json
from pathlib import Path
from flask import Blueprint, request, jsonify, send_from_directory

# 创建蓝图
fiction_api_bp = Blueprint('fiction_api', __name__)

# 小说输出目录
FICTION_OUT_DIR = Path(__file__).parent.parent.parent.parent / 'components' / 'fiction' / 'out'


@fiction_api_bp.route('/fiction/list', methods=['GET'])
def get_fiction_list():
    """获取所有小说列表，按日期分类"""
    try:
        if not FICTION_OUT_DIR.exists():
            return jsonify({
                'success': True,
                'data': {}
            })
        
        # 按日期分类的文章列表
        fiction_data = {}
        
        # 遍历所有日期文件夹
        for date_folder in sorted(FICTION_OUT_DIR.iterdir(), reverse=True):
            if not date_folder.is_dir():
                continue
            
            date_str = date_folder.name
            articles = []
            
            # 遍历该日期下的所有 JSON 文件
            for json_file in sorted(date_folder.glob('*.json'), reverse=True):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        article_data = json.load(f)
                    
                    # 提取基本信息
                    articles.append({
                        'title': article_data.get('title', json_file.stem),
                        'filename': json_file.name,
                        'date': date_str,
                        'time': article_data.get('time', ''),
                        'word_count': article_data.get('word_count', 0)
                    })
                except Exception as e:
                    print(f"读取文件 {json_file} 失败: {e}")
                    continue
            
            if articles:
                fiction_data[date_str] = articles
        
        return jsonify({
            'success': True,
            'data': fiction_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取小说列表失败: {str(e)}'
        }), 500


@fiction_api_bp.route('/fiction/article', methods=['GET'])
def get_fiction_article():
    """获取指定小说的完整内容"""
    try:
        date = request.args.get('date')
        filename = request.args.get('filename')
        
        if not date or not filename:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：date 和 filename'
            }), 400
        
        # 构建文件路径
        file_path = FICTION_OUT_DIR / date / filename
        
        # 安全检查：确保文件在指定目录内
        try:
            file_path.resolve().relative_to(FICTION_OUT_DIR.resolve())
        except ValueError:
            return jsonify({
                'success': False,
                'error': '无效的文件路径'
            }), 400
        
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': article_data
        })
        
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'error': '文件格式错误'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'读取文章失败: {str(e)}'
        }), 500

