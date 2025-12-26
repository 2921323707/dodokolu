# -*- coding: utf-8 -*-
"""
Heaven API路由
"""
from flask import jsonify
from pathlib import Path
import os
import logging
from route.heaven_route import heaven_bp

# 配置日志
logger = logging.getLogger(__name__)


@heaven_bp.route('/api/videos')
def get_videos():
    """获取视频列表API，增强容错处理"""
    try:
        # 获取视频目录路径
        video_dir = Path(__file__).parent.parent.parent / 'static' / 'video' / 'abnormal' / 'fav'
        
        videos = []
        
        # 检查目录是否存在，增强容错
        if not video_dir.exists():
            logger.warning(f"视频目录不存在: {video_dir}")
            return jsonify({
                "success": True,
                "data": [],
                "message": "视频目录不存在"
            })
        
        # 检查目录是否可读，增强容错
        if not os.access(video_dir, os.R_OK):
            logger.error(f"视频目录无读取权限: {video_dir}")
            return jsonify({
                "success": False,
                "message": "视频目录无读取权限",
                "data": []
            }), 403
        
        # 遍历目录，查找所有视频文件，增强容错
        try:
            for file in video_dir.iterdir():
                try:
                    # 检查是否为文件
                    if not file.is_file():
                        continue
                    
                    # 检查文件扩展名
                    file_ext = file.suffix.lower()
                    if file_ext not in ['.mp4', '.webm', '.ogg', '.mov', '.avi']:
                        continue
                    
                    # 检查文件是否可读
                    if not os.access(file, os.R_OK):
                        logger.warning(f"文件无读取权限，跳过: {file.name}")
                        continue
                    
                    # 获取文件名（不含扩展名）
                    filename_without_ext = file.stem
                    
                    # 解析文件名：来源_XXX.mp4，增强容错
                    try:
                        parts = filename_without_ext.split('_', 1)
                        source = parts[0] if len(parts) > 0 and parts[0] else 'unknown'
                        name = parts[1] if len(parts) > 1 and parts[1] else filename_without_ext
                    except Exception as parse_err:
                        logger.warning(f"解析文件名失败: {file.name}, 错误: {parse_err}")
                        source = 'unknown'
                        name = filename_without_ext
                    
                    # 获取文件修改时间，增强容错
                    try:
                        mtime = os.path.getmtime(file)
                    except (OSError, IOError) as mtime_err:
                        logger.warning(f"获取文件修改时间失败: {file.name}, 错误: {mtime_err}")
                        mtime = 0  # 使用默认值
                    
                    # 转换为URL路径
                    url_path = f"/static/video/abnormal/fav/{file.name}"
                    
                    videos.append({
                        "url": url_path,
                        "name": name,
                        "source": source,
                        "filename": file.name,
                        "mtime": mtime
                    })
                    
                except (OSError, IOError, PermissionError) as file_err:
                    # 单个文件处理失败，记录日志但继续处理其他文件
                    logger.warning(f"处理文件失败: {file.name if hasattr(file, 'name') else file}, 错误: {file_err}")
                    continue
                except Exception as file_err:
                    # 其他未预期的错误，记录日志但继续处理
                    logger.error(f"处理文件时发生未预期错误: {file.name if hasattr(file, 'name') else file}, 错误: {file_err}")
                    continue
                    
        except (OSError, IOError, PermissionError) as dir_err:
            logger.error(f"遍历目录失败: {video_dir}, 错误: {dir_err}")
            return jsonify({
                "success": False,
                "message": f"遍历目录失败: {str(dir_err)}",
                "data": []
            }), 500
        
        # 按修改时间排序（最新的在前），增强容错
        try:
            videos.sort(key=lambda x: x.get('mtime', 0), reverse=True)
        except Exception as sort_err:
            logger.warning(f"排序失败: {sort_err}，返回未排序列表")
            # 排序失败不影响返回结果
        
        # 移除mtime字段（不需要返回给前端），增强容错
        for video in videos:
            try:
                video.pop('mtime', None)
            except Exception as pop_err:
                logger.warning(f"移除字段失败: {pop_err}")
                continue
        
        return jsonify({
            "success": True,
            "data": videos
        })
        
    except PermissionError as perm_err:
        logger.error(f"权限错误: {perm_err}")
        return jsonify({
            "success": False,
            "message": f"权限错误: {str(perm_err)}",
            "data": []
        }), 403
    except (OSError, IOError) as io_err:
        logger.error(f"IO错误: {io_err}")
        return jsonify({
            "success": False,
            "message": f"文件系统错误: {str(io_err)}",
            "data": []
        }), 500
    except Exception as e:
        logger.error(f"获取视频列表失败: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"获取视频列表失败: {str(e)}",
            "data": []
        }), 500

