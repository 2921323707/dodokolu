// 消息显示和管理功能

// 添加消息到界面
function addMessage(role, content = '', options = {}) {
    const { loading = false, imageUrl = null, imagePreview = false } = options;
    const chatMessages = document.getElementById('chatMessages');

    // 如果有图片预览，创建图片消息（支持用户和AI）
    if (imagePreview && imageUrl) {
        // 从内容中移除 [图片] 标记
        const textContent = content.replace(/\n?\[图片\]/g, '').trim();

        // 创建图片消息（只显示图片）
        const imageMessageDiv = document.createElement('div');
        imageMessageDiv.className = `message ${role} message-image-only`;
        const imageMessageId = 'msg_' + Date.now() + '_' + Math.random();
        imageMessageDiv.id = imageMessageId;

        const imageAvatar = document.createElement('div');
        imageAvatar.className = 'message-avatar';
        imageAvatar.textContent = role === 'user' ? '我' : 'AI';

        const imageMessageContent = document.createElement('div');
        imageMessageContent.className = 'message-content message-image-content';

        const imagePreviewDiv = document.createElement('div');
        imagePreviewDiv.className = 'message-image-preview-full';
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = '图片';
        imagePreviewDiv.appendChild(img);
        imageMessageContent.appendChild(imagePreviewDiv);

        imageMessageDiv.appendChild(imageAvatar);
        imageMessageDiv.appendChild(imageMessageContent);
        chatMessages.appendChild(imageMessageDiv);

        // 如果有文本内容，创建文本消息（只显示文本）
        let textMessageId = null;
        if (textContent) {
            const textMessageDiv = document.createElement('div');
            textMessageDiv.className = `message ${role}`;
            textMessageId = 'msg_' + Date.now() + '_' + Math.random();
            textMessageDiv.id = textMessageId;

            const textAvatar = document.createElement('div');
            textAvatar.className = 'message-avatar';
            textAvatar.textContent = role === 'user' ? '我' : 'AI';

            const textMessageContent = document.createElement('div');
            textMessageContent.className = 'message-content';

            const messageText = document.createElement('div');
            messageText.className = 'message-text';
            messageText.textContent = textContent;

            textMessageContent.appendChild(messageText);
            textMessageDiv.appendChild(textAvatar);
            textMessageDiv.appendChild(textMessageContent);
            chatMessages.appendChild(textMessageDiv);
        }

        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // 返回文本消息的 ID（如果有），否则返回图片消息的 ID
        return textMessageId || imageMessageId;
    }

    // 正常消息处理（没有图片预览）
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
                <div class="message-text">期待你的输入ing</div>
            </div>
        </div>
    `;
}

