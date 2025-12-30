// 初始化代码

// 更新装饰图片位置，使其固定在聊天消息容器的可视区域中央
let decoUpdateTimer = null;
function updateDecoPosition() {
    // 防抖处理，避免频繁更新
    if (decoUpdateTimer) {
        clearTimeout(decoUpdateTimer);
    }
    decoUpdateTimer = setTimeout(() => {
        const chatMessages = document.getElementById('chatMessages');
        const decoImg = document.querySelector('.chat-messages-deco');

        if (!chatMessages || !decoImg) return;

        // 获取容器的位置和尺寸
        const rect = chatMessages.getBoundingClientRect();

        // 计算容器的可视区域中心点
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        // 更新图片位置
        decoImg.style.left = centerX + 'px';
        decoImg.style.top = centerY + 'px';
    }, 10); // 10ms 防抖延迟
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    // 替换初始头像为图片
    const initialAvatar = document.getElementById('initialAvatar');
    if (initialAvatar) {
        const avatarImg = document.createElement('img');
        avatarImg.src = getAvatarImagePath();
        avatarImg.alt = 'AI';
        avatarImg.style.width = '100%';
        avatarImg.style.height = '100%';
        avatarImg.style.objectFit = 'cover';
        avatarImg.style.borderRadius = '50%';
        avatarImg.style.cursor = 'pointer';
        avatarImg.style.transition = 'transform 0.2s ease, opacity 0.2s ease';

        // 添加点击事件，打开AI信息模态框
        avatarImg.addEventListener('click', (e) => {
            e.stopPropagation();
            openAIInfoModal(getAvatarImagePath());
        });

        // 添加悬停效果
        avatarImg.addEventListener('mouseenter', () => {
            avatarImg.style.transform = 'scale(1.1)';
            avatarImg.style.opacity = '0.9';
        });

        avatarImg.addEventListener('mouseleave', () => {
            avatarImg.style.transform = 'scale(1)';
            avatarImg.style.opacity = '1';
        });

        initialAvatar.textContent = '';
        initialAvatar.appendChild(avatarImg);
    }

    // 初始化输入框
    initInput();

    // 初始化模式按钮状态
    const modeText = document.getElementById('modeText');
    const modeToggleBtn = document.getElementById('modeToggleBtn');
    if (modeText) {
        modeText.textContent = getModeDisplayText(currentMode);
    }
    if (modeToggleBtn && currentMode === 'normal') {
        modeToggleBtn.classList.add('active');
    }

    // 初始化地理位置（静默获取，不阻塞页面加载）
    initLocation();

    // 初始化用户头像（静默获取，不阻塞页面加载）
    if (typeof getUserAvatarUrl === 'function') {
        getUserAvatarUrl().then(avatarUrl => {
            if (avatarUrl) {
                // 更新所有已存在的用户头像
                const userAvatars = document.querySelectorAll('.message.user .message-avatar');
                userAvatars.forEach(avatarDiv => {
                    // 如果已经有文本内容，替换为图片
                    if (avatarDiv.textContent === '我' && !avatarDiv.querySelector('img')) {
                        avatarDiv.textContent = '';
                        const img = document.createElement('img');
                        img.src = avatarUrl;
                        img.alt = '我';
                        img.style.width = '100%';
                        img.style.height = '100%';
                        img.style.objectFit = 'cover';
                        img.style.borderRadius = '50%';
                        img.style.cursor = 'pointer';
                        img.style.transition = 'transform 0.2s ease, opacity 0.2s ease';
                        
                        // 添加点击事件
                        img.addEventListener('click', (e) => {
                            e.stopPropagation();
                            if (typeof openUserInfoModal === 'function') {
                                openUserInfoModal();
                            }
                        });
                        
                        // 添加悬停效果
                        img.addEventListener('mouseenter', () => {
                            img.style.transform = 'scale(1.1)';
                            img.style.opacity = '0.9';
                        });
                        
                        img.addEventListener('mouseleave', () => {
                            img.style.transform = 'scale(1)';
                            img.style.opacity = '1';
                        });
                        
                        avatarDiv.appendChild(img);
                    } else if (avatarDiv.querySelector('img')) {
                        // 如果已经有图片，更新URL
                        avatarDiv.querySelector('img').src = avatarUrl + '?t=' + Date.now();
                    }
                });
            }
        }).catch(error => {
            console.error('加载用户头像失败:', error);
        });
    }

    // 初始化智能体在线状态显示（静默获取，不阻塞页面加载）
    if (typeof updateAgentStatusDisplay === 'function') {
        const mode = typeof currentMode !== 'undefined' ? currentMode : 'normal';
        updateAgentStatusDisplay(mode);
    }

    // 初始化标题栏中的dodokolu智能体在线状态显示
    if (typeof updateHeaderAgentStatus === 'function') {
        updateHeaderAgentStatus('dodokolu');
        // 每30秒更新一次状态
        setInterval(() => {
            updateHeaderAgentStatus('dodokolu');
        }, 30000);
    }

    // 加载历史记录
    loadHistory().then(() => {
        // 检查是否有历史记录，如果没有则先创建备注框，再创建消息
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            const messages = chatMessages.querySelectorAll('.message');
            // 如果只有初始消息（期待你的输入ing...），先移除它，然后先创建备注框，再创建消息
            if (messages.length === 1) {
                const initialMessage = messages[0];
                const messageText = initialMessage.querySelector('.message-text');
                if (messageText && messageText.textContent === '期待你的输入ing...') {
                    // 移除初始消息
                    initialMessage.remove();
                    // 先创建备注框
                    const messageId = 'msg_' + Date.now() + '_' + Math.random();
                    const skillsNote = createSkillsNote('assistant', messageId);
                    if (skillsNote) {
                        chatMessages.appendChild(skillsNote);
                    }
                    // 延迟0.88秒后创建消息
                    setTimeout(() => {
                        const newInitialMessage = document.createElement('div');
                        newInitialMessage.className = 'message assistant';
                        newInitialMessage.id = messageId;
                        const avatar = createAIAvatarElement();
                        newInitialMessage.appendChild(avatar);
                        const messageContent = document.createElement('div');
                        messageContent.className = 'message-content';
                        const messageText = document.createElement('div');
                        messageText.className = 'message-text';
                        messageText.textContent = '期待你的输入ing...';
                        messageContent.appendChild(messageText);
                        newInitialMessage.appendChild(messageContent);
                        chatMessages.appendChild(newInitialMessage);
                        // 滚动到底部
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }, 880);
                }
            }
        }
    });

    // 初始化装饰图片位置
    updateDecoPosition();

    // 监听窗口大小改变和滚动事件，更新图片位置
    window.addEventListener('resize', updateDecoPosition);
    window.addEventListener('scroll', updateDecoPosition);

    // 监听聊天消息容器的滚动事件
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.addEventListener('scroll', updateDecoPosition);
    }
});

