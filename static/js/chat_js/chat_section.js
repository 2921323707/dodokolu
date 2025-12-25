// 聊天区域API调用和主要功能

// 发送消息
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const message = chatInput.value.trim();

    if (!message || isStreaming) return;

    // 添加用户消息到界面
    addMessage('user', message);
    chatInput.value = '';
    chatInput.style.height = 'auto';
    sendBtn.disabled = true;
    isStreaming = true;

    try {
        // 创建AI消息占位符，等待流式内容时显示加载动画
        const assistantMessageId = addMessage('assistant', '', { loading: true });

        // 检查是否需要包含位置信息（如果消息与天气相关）
        const locationContext = isWeatherRelated(message) ? getLocationContext() : null;
        
        // 发送请求到后端
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                mode: currentMode,
                location: userLocation ? {
                    latitude: userLocation.latitude,
                    longitude: userLocation.longitude
                } : null
            })
        });

        if (!response.ok) {
            throw new Error('请求失败');
        }

        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.content) {
                            appendToMessage(assistantMessageId, data.content);
                        }
                        if (data.done) {
                            isStreaming = false;
                            sendBtn.disabled = false;
                        }
                    } catch (e) {
                        console.error('解析数据错误:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('发送消息错误:', error);
        addMessage('assistant', '抱歉，发生了错误。请稍后重试。');
        isStreaming = false;
        sendBtn.disabled = false;
    }
}

// 加载历史记录
async function loadHistory() {
    try {
        const response = await fetch(`/api/history/${sessionId}`);
        const data = await response.json();

        if (data.history && data.history.length > 0) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = ''; // 清空初始消息

            data.history.forEach(msg => {
                if (msg.role !== 'system') {
                    addMessage(msg.role, msg.content);
                }
            });
        }
    } catch (error) {
        console.error('加载历史记录错误:', error);
    }
}

// 清空历史
async function clearHistory() {
    if (!confirm('确定要清空对话历史吗？')) return;

    try {
        const response = await fetch(`/api/clear/${sessionId}`, {
            method: 'POST'
        });

        if (response.ok) {
            resetMessages();
        }
    } catch (error) {
        console.error('清空历史错误:', error);
    }
}

// 未登录提示封装
function promptLoginRequired() {
    alert('请先登录');
    window.location.href = '/login';
}

// 校验unnormal模式权限：登录 + 具有高级角色（创作者/管理员等）
async function canSwitchToUnnormal() {
    try {
        const resp = await fetch('/api/auth-status');
        if (!resp.ok) {
            throw new Error('auth status request failed');
        }
        const data = await resp.json();
        if (!data.logged_in) {
            promptLoginRequired();
            return false;
        }
        const role = data.user?.role ?? 0;
        // role 为 0 表示普通用户，其它值（1: 创作者, 2/9: 管理员等）视为有权限
        if (role === 0) {
            alert('当前账号无权限切换到 unnormal 模式，请联系管理员或填写邀请码升级身份');
            return false;
        }
        return true;
    } catch (error) {
        console.error('检查模式权限失败:', error);
        alert('检查模式权限失败，请稍后重试');
        return false;
    }
}

// 切换模式（只有管理员可切到unnormal）
async function toggleMode() {
    const modeText = document.getElementById('modeText');
    const modeToggleBtn = document.getElementById('modeToggleBtn');
    const previousSessionId = sessionId;

    // 切换到unnormal前进行鉴权
    if (currentMode === 'normal') {
        const allow = await canSwitchToUnnormal();
        if (!allow) return;
        currentMode = 'unnormal';
    } else {
        currentMode = 'normal';
    }

    if (modeText) {
        modeText.textContent = currentMode;
    }
    
    // 更新按钮样式
    if (modeToggleBtn) {
        if (currentMode === 'normal') {
            modeToggleBtn.classList.add('active');
        } else {
            modeToggleBtn.classList.remove('active');
        }
    }

    // 切换模式时重置会话：新 sessionId + 清空历史
    sessionId = createSessionId();
    try {
        await fetch(`/api/clear/${previousSessionId}`, { method: 'POST' });
    } catch (error) {
        console.warn('清理上一会话历史失败:', error);
    }
    resetMessages();
    isStreaming = false;
    const sendBtn = document.getElementById('sendBtn');
    if (sendBtn) sendBtn.disabled = false;

    console.log('模式已切换为:', currentMode, '会话已重置为:', sessionId);
}

