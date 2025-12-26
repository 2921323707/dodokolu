# -*- coding: utf-8 -*-
"""
聊天相关路由
"""
from flask import Blueprint, request, jsonify, Response, stream_with_context
from route.config.llm import get_conversation_history, save_message, llm_stream, clear_history

# 创建蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api')


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    mode = data.get('mode', 'normal')  # 获取模式参数，默认为unnormal
    location = data.get('location', None)  # 获取用户位置信息
    
    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400
    
    # 保存用户消息
    save_message(session_id, "user", user_message)
    
    # 获取对话历史（不包括系统提示词）
    history = get_conversation_history(session_id)
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history if msg["role"] != "system"]
    
    # 返回流式响应，根据模式选择不同的LLM，传递位置信息
    return Response(
        stream_with_context(llm_stream(messages, session_id, mode, location)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """获取对话历史"""
    history = get_conversation_history(session_id)
    return jsonify({'history': history})


@chat_bp.route('/clear/<session_id>', methods=['POST'])
def clear_history_route(session_id):
    """清空对话历史"""
    clear_history(session_id)
    return jsonify({'success': True})

