// 聊天记录功能
document.addEventListener('DOMContentLoaded', function () {
    // 加载聊天记录文件列表
    async function loadChatHistoryFiles() {
        const chatHistoryLoading = document.getElementById('chatHistoryLoading');
        const chatHistoryError = document.getElementById('chatHistoryError');
        const chatHistoryContainer = document.getElementById('chatHistoryContainer');
        const chatHistorySelect = document.getElementById('chatHistorySelect');
        const chatHistoryContent = document.getElementById('chatHistoryContent');

        if (!chatHistoryLoading || !chatHistoryError || !chatHistoryContainer || !chatHistorySelect || !chatHistoryContent) return;

        // 显示加载状态
        chatHistoryLoading.style.display = 'block';
        chatHistoryError.style.display = 'none';
        chatHistoryContainer.style.display = 'none';

        try {
            const response = await fetch('/api/account/chat-history/files');
            const data = await response.json();

            if (data.success && data.files) {
                // 清空并填充下拉选择框
                chatHistorySelect.innerHTML = '<option value="">请选择聊天记录文件</option>';

                if (data.files.length === 0) {
                    chatHistorySelect.innerHTML = '<option value="">暂无聊天记录</option>';
                    chatHistoryLoading.style.display = 'none';
                    chatHistoryContainer.style.display = 'block';
                    chatHistoryContent.innerHTML = '<p class="empty-message">暂无聊天记录</p>';
                } else {
                    data.files.forEach(file => {
                        const option = document.createElement('option');
                        option.value = file.filename;
                        option.textContent = `${file.filename} (${file.message_count}条消息, ${file.modified_time})`;
                        chatHistorySelect.appendChild(option);
                    });

                    chatHistoryLoading.style.display = 'none';
                    chatHistoryContainer.style.display = 'block';
                }
            } else {
                throw new Error(data.message || '获取聊天记录文件列表失败');
            }
        } catch (error) {
            console.error('加载聊天记录文件列表失败:', error);
            chatHistoryLoading.style.display = 'none';
            chatHistoryError.textContent = error.message || '加载聊天记录文件列表失败，请稍后重试';
            chatHistoryError.style.display = 'block';
        }
    }

    // 加载指定聊天记录文件的内容
    async function loadChatHistoryContent(filename) {
        const chatHistoryContent = document.getElementById('chatHistoryContent');
        if (!chatHistoryContent) return;

        chatHistoryContent.innerHTML = '<div class="loading-message">正在加载聊天记录...</div>';

        try {
            const response = await fetch(`/api/account/chat-history/content?filename=${encodeURIComponent(filename)}`);
            const data = await response.json();

            if (data.success && data.content) {
                // 格式化并显示聊天记录
                const formattedContent = formatChatHistory(data.content);
                chatHistoryContent.innerHTML = formattedContent;
            } else {
                throw new Error(data.message || '加载聊天记录内容失败');
            }
        } catch (error) {
            console.error('加载聊天记录内容失败:', error);
            chatHistoryContent.innerHTML = `<div class="error-message">${escapeHtml(error.message || '加载聊天记录内容失败')}</div>`;
        }
    }

    // 格式化聊天记录内容
    function formatChatHistory(history) {
        if (!Array.isArray(history) || history.length === 0) {
            return '<p class="empty-message">该文件暂无聊天记录</p>';
        }

        const messagesHtml = history.map((msg, index) => {
            const role = msg.role || 'unknown';
            const content = msg.content || '';
            const timestamp = msg.timestamp || '';

            // 格式化时间
            let timeDisplay = '';
            if (timestamp) {
                try {
                    const date = new Date(timestamp);
                    timeDisplay = date.toLocaleString('zh-CN', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                    });
                } catch (e) {
                    timeDisplay = timestamp;
                }
            }

            // 根据角色设置样式
            let roleClass = 'message-role-unknown';
            let roleLabel = '未知';
            if (role === 'user') {
                roleClass = 'message-role-user';
                roleLabel = '用户';
            } else if (role === 'assistant') {
                roleClass = 'message-role-assistant';
                roleLabel = '助手';
            } else if (role === 'system') {
                roleClass = 'message-role-system';
                roleLabel = '系统';
            } else if (role === 'tool') {
                roleClass = 'message-role-tool';
                roleLabel = '工具';
            }

            // 处理内容（转义HTML，保留换行）
            const escapedContent = escapeHtml(content).replace(/\n/g, '<br>');

            // 构建消息HTML
            let messageHtml = `
                <div class="chat-message-item ${roleClass}">
                    <div class="message-header">
                        <span class="message-role">${escapeHtml(roleLabel)}</span>
                        ${timeDisplay ? `<span class="message-time">${escapeHtml(timeDisplay)}</span>` : ''}
                    </div>
                    <div class="message-content">${escapedContent}</div>
            `;

            // 如果有工具调用信息，显示
            if (msg.tool_calls && Array.isArray(msg.tool_calls)) {
                messageHtml += `
                    <div class="message-tool-calls">
                        <strong>工具调用:</strong>
                        <pre class="tool-calls-json">${escapeHtml(JSON.stringify(msg.tool_calls, null, 2))}</pre>
                    </div>
                `;
            }

            // 如果有指令调用信息，显示
            if (msg.command_info) {
                messageHtml += `
                    <div class="message-command-info">
                        <strong>指令信息:</strong>
                        <pre class="command-info-json">${escapeHtml(JSON.stringify(msg.command_info, null, 2))}</pre>
                    </div>
                `;
            }

            // 如果有图片文件名，显示
            if (msg.image_filename) {
                messageHtml += `
                    <div class="message-image">
                        <strong>图片:</strong> ${escapeHtml(msg.image_filename)}
                    </div>
                `;
            }

            messageHtml += '</div>';
            return messageHtml;
        }).join('');

        return `<div class="chat-history-messages">${messagesHtml}</div>`;
    }

    // 绑定聊天记录选择框变化事件
    const chatHistorySelect = document.getElementById('chatHistorySelect');
    if (chatHistorySelect) {
        chatHistorySelect.addEventListener('change', (e) => {
            const filename = e.target.value;
            if (filename) {
                loadChatHistoryContent(filename);
            } else {
                const chatHistoryContent = document.getElementById('chatHistoryContent');
                if (chatHistoryContent) {
                    chatHistoryContent.innerHTML = '';
                }
            }
        });
    }

    // 绑定刷新按钮事件
    const refreshChatHistoryBtn = document.getElementById('refreshChatHistoryBtn');
    if (refreshChatHistoryBtn) {
        refreshChatHistoryBtn.addEventListener('click', () => {
            loadChatHistoryFiles();
            const chatHistorySelect = document.getElementById('chatHistorySelect');
            const chatHistoryContent = document.getElementById('chatHistoryContent');
            if (chatHistorySelect) chatHistorySelect.value = '';
            if (chatHistoryContent) chatHistoryContent.innerHTML = '';
        });
    }

    // 暴露给导航模块使用
    window.loadChatHistoryFiles = loadChatHistoryFiles;
});

