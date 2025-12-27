// 指令模式相关功能

// 全局变量（使用window对象确保全局作用域）
if (typeof window.selectedCommandType === 'undefined') {
    window.selectedCommandType = null;
}

// 插入指令到输入框
function insertCommand(type) {
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) return;

    // 在输入框当前光标位置插入指令，如果没有选中文本则在末尾添加
    const command = '/' + type + ' ';
    const start = chatInput.selectionStart;
    const end = chatInput.selectionEnd;
    const text = chatInput.value;

    // 插入指令
    chatInput.value = text.substring(0, start) + command + text.substring(end);

    // 设置光标位置到指令末尾
    const newPosition = start + command.length;
    chatInput.setSelectionRange(newPosition, newPosition);

    // 调整输入框高度
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';

    // 聚焦输入框
    chatInput.focus();
}

// 处理指令（无需密钥验证）
function processCommand(type) {
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) {
        return;
    }

    const inputValue = chatInput.value.trim();

    // 解析指令：/image prompt 或 /video prompt
    let prompt = '';
    if (inputValue.startsWith('/image ')) {
        prompt = inputValue.substring(7).trim();
        // 确保类型一致
        if (type !== 'image') {
            type = 'image';
        }
    } else if (inputValue.startsWith('/video ')) {
        prompt = inputValue.substring(7).trim();
        // 确保类型一致
        if (type !== 'video') {
            type = 'video';
        }
    } else if (inputValue === '/image' || inputValue === '/video') {
        // 如果只有指令没有提示词，提示用户
        alert('请输入提示词，例如：/' + type + ' 一只可爱的小猫');
        window.selectedCommandType = null;
        return;
    } else {
        // 如果输入框内容不符合预期，但type存在，使用type
        prompt = inputValue;
    }

    if (prompt && type) {
        // 清空输入框
        chatInput.value = '';
        chatInput.style.height = 'auto';
        // 执行生成
        executeGeneration(type, prompt);
    }

    // 重置选择
    window.selectedCommandType = null;
}

// 执行生成
async function executeGeneration(type, prompt) {
    // 检查登录状态
    try {
        const authResponse = await fetch('/api/auth-status');
        const authData = await authResponse.json();
        if (!authData.logged_in) {
            promptLoginRequired();
            return;
        }
    } catch (error) {
        console.error('检查登录状态失败:', error);
        promptLoginRequired();
        return;
    }

    // 显示用户消息
    addMessage('user', `/${type} ${prompt}`);

    // 创建加载消息
    const loadingMessageId = addGenerationLoadingMessage(type);

    try {
        const endpoint = type === 'image' ? '/api/generate-image' : '/api/generate-video';

        // 开始进度更新（估算时间）
        const estimatedTime = type === 'image' ? 30 : 70; // 图片约30秒，视频约70秒
        const progressInterval = startProgressUpdate(loadingMessageId, estimatedTime);

        // 发送生成请求
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                session_id: sessionId, // 传入session_id
                // 视频默认配置：5秒，无水印
                ...(type === 'video' ? { duration: 5, watermark: false } : {})
            })
        });

        // 清除进度更新
        if (progressInterval) {
            clearInterval(progressInterval);
        }

        if (!response.ok) {
            if (response.status === 401) {
                promptLoginRequired();
                updateGenerationLoadingMessage(loadingMessageId, '生成失败：请先登录', true);
                return;
            }
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || '生成失败');
        }

        const data = await response.json();

        // 移除加载消息
        removeGenerationLoadingMessage(loadingMessageId);

        if (data.success) {
            // 显示生成的内容
            if (type === 'image' && data.image_url) {
                addMessage('assistant', '', {
                    imageUrl: data.image_url,
                    imagePreview: true
                });
            } else if (type === 'video' && data.video_url) {
                addMessage('assistant', '', {
                    videoUrl: data.video_url,
                    videoPreview: true
                });
            } else {
                addMessage('assistant', '生成成功，但无法显示结果');
            }

            // 生成成功后，自动触发AI响应
            // 延迟一小段时间，确保历史记录已保存
            setTimeout(() => {
                // 自动发送一条消息，触发AI响应
                // 使用用户原来的指令，让AI知道指令已执行成功
                const chatInput = document.getElementById('chatInput');
                if (chatInput && typeof sendMessage === 'function') {
                    // 清理 prompt 中可能存在的 [已成功生成] 标记，避免重复
                    const cleanPrompt = prompt.replace(/\s*\[已成功生成\]\s*/g, '').trim();
                    // 临时设置输入框内容，然后发送
                    const originalValue = chatInput.value;
                    chatInput.value = `/${type} ${cleanPrompt} [已成功生成]`;
                    // 触发发送消息
                    sendMessage();
                    // 恢复输入框（sendMessage会清空输入框，所以这里不需要恢复）
                }
            }, 500); // 延迟500ms，确保后端历史记录已保存
        } else {
            throw new Error(data.error || '生成失败');
        }
    } catch (error) {
        console.error('生成错误:', error);
        updateGenerationLoadingMessage(loadingMessageId, `生成失败：${error.message}`, true);
    }
}

// 创建生成加载消息
function addGenerationLoadingMessage(type) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return null;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    const messageId = 'gen_' + Date.now() + '_' + Math.random();
    messageDiv.id = messageId;

    const avatar = createAIAvatarElement();
    messageDiv.appendChild(avatar);

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';

    const progressDiv = document.createElement('div');
    progressDiv.className = 'generation-progress';
    progressDiv.innerHTML = `
        <div class="generation-spinner"></div>
        <div class="generation-progress-text">正在生成${type === 'image' ? '图片' : '视频'}，请稍候...</div>
        <div class="generation-progress-time" id="progressTime_${messageId}">预计还需要 <span id="timeRemaining_${messageId}">--</span> 秒</div>
    `;

    messageContent.appendChild(progressDiv);
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);

    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageId;
}

// 更新生成加载消息
function updateGenerationLoadingMessage(messageId, text, isError = false) {
    const messageDiv = document.getElementById(messageId);
    if (!messageDiv) return;

    const messageContent = messageDiv.querySelector('.message-content');
    if (!messageContent) return;

    if (isError) {
        messageContent.innerHTML = `
            <div class="message-text" style="color: #ef4444;">${text}</div>
        `;
    } else {
        const progressDiv = messageContent.querySelector('.generation-progress');
        if (progressDiv) {
            const textDiv = progressDiv.querySelector('.generation-progress-text');
            if (textDiv) {
                textDiv.textContent = text;
            }
        }
    }
}

// 移除生成加载消息
function removeGenerationLoadingMessage(messageId) {
    const messageDiv = document.getElementById(messageId);
    if (messageDiv) {
        messageDiv.remove();
    }
}

// 开始进度更新
function startProgressUpdate(messageId, estimatedTime) {
    let remainingTime = estimatedTime;

    const interval = setInterval(() => {
        const timeElement = document.getElementById(`timeRemaining_${messageId}`);
        if (timeElement) {
            remainingTime = Math.max(0, remainingTime - 1);
            timeElement.textContent = remainingTime;

            if (remainingTime <= 0) {
                clearInterval(interval);
            }
        } else {
            clearInterval(interval);
        }
    }, 1000);

    return interval;
}


