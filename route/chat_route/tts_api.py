# -*- coding: utf-8 -*-
"""
TTS 语音合成API路由
"""
import os
import re
import hashlib
import asyncio
import importlib.util
from pathlib import Path
from flask import Blueprint, request, jsonify, session, url_for
from werkzeug.utils import secure_filename

# 创建蓝图
tts_api_bp = Blueprint('tts_api', __name__)


@tts_api_bp.route('/tts', methods=['POST'])
def tts_api():
    """TTS 语音合成API"""
    try:
        # 检查是否登录
        user_email = session.get('email')
        if not user_email:
            return jsonify({'error': '登录了吗，就想榨干我的Token(￣へ￣)'}), 401
        
        data = request.json
        text = data.get('text', '').strip()
        message_id = data.get('message_id', None)  # 可选的消息ID，用于缓存
        
        if not text:
            return jsonify({'error': '文本不能为空'}), 400
        
        # 过滤掉括号内的内容（角色扮演动作描述）和星号
        # 匹配中文括号、英文括号、方括号等
        filtered_text = re.sub(r'[（(【\[].*?[）)\]\】]', '', text)
        # 过滤掉星号
        filtered_text = re.sub(r'\*+', '', filtered_text)
        filtered_text = filtered_text.strip()
        
        if not filtered_text:
            return jsonify({'error': '过滤后文本为空'}), 400
        
        # 导入 TTS 模块
        tts_module_path = Path(__file__).parent.parent.parent / 'components' / 'tts语音合成' / 'src.py'
        spec = importlib.util.spec_from_file_location("tts_src", str(tts_module_path))
        tts_src = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tts_src)
        
        # 创建配置
        config = tts_src.TTSConfig()
        
        # 确保音频目录存在
        safe_email = user_email.replace('@', '_at_').replace('.', '_')
        safe_email = secure_filename(safe_email)
        audio_dir = Path('static') / 'audio' / 'response_audio' / safe_email
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # 基于文本内容生成唯一ID（用于缓存）
        text_hash = hashlib.md5(filtered_text.encode('utf-8')).hexdigest()[:16]
        
        # 如果提供了 message_id，优先使用 message_id 作为文件名
        if message_id:
            filename = f"tts_{message_id}_{text_hash}.mp3"
        else:
            filename = f"tts_{text_hash}.mp3"
        
        output_file = audio_dir / filename
        
        # 检查文件是否已存在（缓存）
        if output_file.exists():
            relative_path = f"audio/response_audio/{safe_email}/{filename}"
            audio_url = url_for('static', filename=relative_path)
            return jsonify({
                'success': True,
                'audio_url': audio_url,
                'filename': filename,
                'cached': True
            })
        
        # 调用 TTS 生成语音
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(tts_src.submit_text(config, filtered_text, str(output_file)))
        finally:
            loop.close()
        
        # 检查文件是否生成成功
        if not output_file.exists():
            return jsonify({'error': '语音生成失败'}), 500
        
        # 生成访问URL
        relative_path = f"audio/response_audio/{safe_email}/{filename}"
        audio_url = url_for('static', filename=relative_path)
        
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'filename': filename,
            'cached': False
        })
        
    except Exception as e:
        print(f'TTS 生成错误: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'语音生成失败: {str(e)}'}), 500

