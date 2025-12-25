// 消息显示和管理功能

// 添加消息到界面
function addMessage(role, content = '', options = {}) {
    const { loading = false } = options;
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    const messageId = 'msg_' + Date.now() + '_' + Math.random();
    messageDiv.id = messageId;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '我' : 'AI';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';

    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.textContent = content;

    if (loading && role === 'assistant') {
        // 等待流式内容时显示加载动画
        const loadingWrap = document.createElement('div');
        loadingWrap.className = 'message-loading';
        loadingWrap.innerHTML = `
            <span class="loader-dot"></span>
            <span class="loader-dot"></span>
            <span class="loader-dot"></span>
        `;
        messageContent.appendChild(loadingWrap);
        messageText.style.display = 'none';
        messageDiv.dataset.loading = 'true';
    }

    messageContent.appendChild(messageText);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);

    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageId;
}

// 追加内容到消息
function appendToMessage(messageId, content) {
    const messageDiv = document.getElementById(messageId);
    if (!messageDiv) return;

    const messageText = messageDiv.querySelector('.message-text');
    const loadingWrap = messageDiv.querySelector('.message-loading');

    // 首次收到内容时移除加载动画
    if (loadingWrap) {
        loadingWrap.remove();
        if (messageText) {
            messageText.style.display = '';
            messageText.textContent = '';
        }
        delete messageDiv.dataset.loading;
    }

    if (messageText) {
        messageText.textContent += content;
        // 滚动到底部
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// 重置消息区域为初始状态
function resetMessages() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="message assistant">
            <div class="message-avatar">AI</div>
            <div class="message-content">
                <div class="message-text"><期待你的输入ing></div>
            </div>
        </div>
    `;
}

