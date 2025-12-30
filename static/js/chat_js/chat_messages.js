// 消息显示和管理功能

// 添加消息到界面
function addMessage(role, content = '', options = {}) {
    const { loading = false, imageUrl = null, imagePreview = false, videoUrl = null, videoPreview = false } = options;
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

        const imageAvatar = role === 'user'
            ? createUserAvatarElement()
            : createAIAvatarElement();

        const imageMessageContent = document.createElement('div');
        imageMessageContent.className = 'message-content message-image-content';

        const imagePreviewDiv = document.createElement('div');
        imagePreviewDiv.className = 'message-image-preview-full';
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = '图片';
        // 为图片添加点击事件，打开模态框
        img.addEventListener('click', (e) => {
            e.stopPropagation();
            openImageModal(imageUrl);
        });
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

            const textAvatar = role === 'user'
                ? createUserAvatarElement()
                : createAIAvatarElement();

            const textMessageContent = document.createElement('div');
            textMessageContent.className = 'message-content';

            const messageText = document.createElement('div');
            messageText.className = 'message-text';
            messageText.textContent = textContent;

            textMessageContent.appendChild(messageText);

            // 为 assistant 文本消息添加播放和复制按钮（在 message-content 外部）
            if (role === 'assistant' && textContent && textContent.trim()) {
                // 检查是否是离线消息
                const isOfflineMessage = textContent.trim() === '人家也是需要睡觉的~';
                if (isOfflineMessage) {
                    textMessageDiv.dataset.offline = 'true';
                }

                const buttonContainer = document.createElement('div');
                buttonContainer.className = 'message-action-buttons';

                // 播放按钮
                const playButton = document.createElement('button');
                playButton.className = 'message-action-btn message-play-btn';
                playButton.innerHTML = '<img src="/static/imgs/icon/小喇叭.png" alt="播放">';
                playButton.title = '播放语音';
                playButton.dataset.messageId = textMessageId;
                playButton.dataset.text = textContent;
                if (isOfflineMessage) {
                    playButton.dataset.offline = 'true';
                    playButton.onclick = (e) => {
                        e.stopPropagation();
                        playOfflineAudio(playButton);
                    };
                } else {
                    playButton.onclick = (e) => {
                        e.stopPropagation();
                        playTTS(textContent, playButton, textMessageId);
                    };
                }

                // 复制按钮
                const copyButton = document.createElement('button');
                copyButton.className = 'message-action-btn message-copy-btn';
                copyButton.innerHTML = '<img src="/static/imgs/icon/复制.png" alt="复制">';
                copyButton.title = '复制文本';
                copyButton.dataset.messageId = textMessageId;
                copyButton.dataset.text = textContent;
                copyButton.onclick = (e) => {
                    e.stopPropagation();
                    copyText(textContent, copyButton);
                };

                buttonContainer.appendChild(playButton);
                buttonContainer.appendChild(copyButton);
                textMessageDiv.appendChild(buttonContainer);
            }

            textMessageDiv.appendChild(textAvatar);
            textMessageDiv.appendChild(textMessageContent);
            chatMessages.appendChild(textMessageDiv);
        }

        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // 返回文本消息的 ID（如果有），否则返回图片消息的 ID
        return textMessageId || imageMessageId;
    }

    // 如果有视频预览，创建视频消息（支持AI发送）
    if (videoPreview && videoUrl) {
        // 从内容中移除 [视频] 标记
        const textContent = content.replace(/\n?\[视频\]/g, '').trim();

        // 创建视频消息（只显示视频）
        const videoMessageDiv = document.createElement('div');
        videoMessageDiv.className = `message ${role} message-video-only`;
        const videoMessageId = 'msg_' + Date.now() + '_' + Math.random();
        videoMessageDiv.id = videoMessageId;

        const videoAvatar = role === 'user'
            ? createUserAvatarElement()
            : createAIAvatarElement();

        const videoMessageContent = document.createElement('div');
        videoMessageContent.className = 'message-content message-video-content';

        const videoPreviewDiv = document.createElement('div');
        videoPreviewDiv.className = 'message-video-preview-full';
        const video = document.createElement('video');
        video.src = videoUrl;
        video.controls = true;
        video.style.maxWidth = '100%';
        video.style.maxHeight = '400px';
        video.style.borderRadius = '8px';
        video.style.cursor = 'pointer';
        // 为视频添加点击事件，打开模态框
        video.addEventListener('click', (e) => {
            e.stopPropagation();
            openVideoModal(videoUrl);
        });
        videoPreviewDiv.appendChild(video);
        videoMessageContent.appendChild(videoPreviewDiv);

        videoMessageDiv.appendChild(videoAvatar);
        videoMessageDiv.appendChild(videoMessageContent);
        chatMessages.appendChild(videoMessageDiv);

        // 如果有文本内容，创建文本消息（只显示文本）
        let textMessageId = null;
        if (textContent) {
            const textMessageDiv = document.createElement('div');
            textMessageDiv.className = `message ${role}`;
            textMessageId = 'msg_' + Date.now() + '_' + Math.random();
            textMessageDiv.id = textMessageId;

            const textAvatar = role === 'user'
                ? createUserAvatarElement()
                : createAIAvatarElement();

            const textMessageContent = document.createElement('div');
            textMessageContent.className = 'message-content';

            const messageText = document.createElement('div');
            messageText.className = 'message-text';
            messageText.textContent = textContent;

            textMessageContent.appendChild(messageText);

            // 为 assistant 文本消息添加播放和复制按钮（在 message-content 外部）
            if (role === 'assistant' && textContent && textContent.trim()) {
                // 检查是否是离线消息
                const isOfflineMessage = textContent.trim() === '人家也是需要睡觉的~';
                if (isOfflineMessage) {
                    textMessageDiv.dataset.offline = 'true';
                }

                const buttonContainer = document.createElement('div');
                buttonContainer.className = 'message-action-buttons';

                // 播放按钮
                const playButton = document.createElement('button');
                playButton.className = 'message-action-btn message-play-btn';
                playButton.innerHTML = '<img src="/static/imgs/icon/小喇叭.png" alt="播放">';
                playButton.title = '播放语音';
                playButton.dataset.messageId = textMessageId;
                playButton.dataset.text = textContent;
                if (isOfflineMessage) {
                    playButton.dataset.offline = 'true';
                    playButton.onclick = (e) => {
                        e.stopPropagation();
                        playOfflineAudio(playButton);
                    };
                } else {
                    playButton.onclick = (e) => {
                        e.stopPropagation();
                        playTTS(textContent, playButton, textMessageId);
                    };
                }

                // 复制按钮
                const copyButton = document.createElement('button');
                copyButton.className = 'message-action-btn message-copy-btn';
                copyButton.innerHTML = '<img src="/static/imgs/icon/复制.png" alt="复制">';
                copyButton.title = '复制文本';
                copyButton.dataset.messageId = textMessageId;
                copyButton.dataset.text = textContent;
                copyButton.onclick = (e) => {
                    e.stopPropagation();
                    copyText(textContent, copyButton);
                };

                buttonContainer.appendChild(playButton);
                buttonContainer.appendChild(copyButton);
                textMessageDiv.appendChild(buttonContainer);
            }

            textMessageDiv.appendChild(textAvatar);
            textMessageDiv.appendChild(textMessageContent);
            chatMessages.appendChild(textMessageDiv);
        }

        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // 返回文本消息的 ID（如果有），否则返回视频消息的 ID
        return textMessageId || videoMessageId;
    }

    // 正常消息处理（没有图片或视频预览）
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    const messageId = 'msg_' + Date.now() + '_' + Math.random();
    messageDiv.id = messageId;

    const avatar = role === 'user'
        ? createUserAvatarElement()
        : createAIAvatarElement();

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

    // 为 assistant 消息添加播放和复制按钮（在 message-content 外部）
    if (role === 'assistant' && content && content.trim()) {
        // 检查是否是离线消息
        const isOfflineMessage = content.trim() === '人家也是需要睡觉的~';
        if (isOfflineMessage) {
            messageDiv.dataset.offline = 'true';
        }

        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'message-action-buttons';

        // 播放按钮
        const playButton = document.createElement('button');
        playButton.className = 'message-action-btn message-play-btn';
        playButton.innerHTML = '<img src="/static/imgs/icon/小喇叭.png" alt="播放">';
        playButton.title = '播放语音';
        playButton.dataset.messageId = messageId;
        playButton.dataset.text = content;
        if (isOfflineMessage) {
            playButton.dataset.offline = 'true';
            playButton.onclick = (e) => {
                e.stopPropagation();
                playOfflineAudio(playButton);
            };
        } else {
            playButton.onclick = (e) => {
                e.stopPropagation();
                playTTS(content, playButton, messageId);
            };
        }

        // 复制按钮
        const copyButton = document.createElement('button');
        copyButton.className = 'message-action-btn message-copy-btn';
        copyButton.innerHTML = '<img src="/static/imgs/icon/复制.png" alt="复制">';
        copyButton.title = '复制文本';
        copyButton.dataset.messageId = messageId;
        copyButton.dataset.text = content;
        copyButton.onclick = (e) => {
            e.stopPropagation();
            copyText(content, copyButton);
        };

        buttonContainer.appendChild(playButton);
        buttonContainer.appendChild(copyButton);
        messageDiv.appendChild(buttonContainer);
    }

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

        // 如果是 assistant 消息且还没有按钮容器，添加一个
        if (messageDiv.classList.contains('assistant')) {
            const messageContent = messageDiv.querySelector('.message-content');
            const existingButtonContainer = messageDiv.querySelector('.message-action-buttons');
            const messageId = messageDiv.id;

            if (!existingButtonContainer && messageText.textContent.trim() && messageContent) {
                // 检查是否是离线消息
                const isOfflineMessage = messageText.textContent.trim() === '人家也是需要睡觉的~';
                if (isOfflineMessage) {
                    messageDiv.dataset.offline = 'true';
                }

                const buttonContainer = document.createElement('div');
                buttonContainer.className = 'message-action-buttons';

                // 播放按钮
                const playButton = document.createElement('button');
                playButton.className = 'message-action-btn message-play-btn';
                playButton.innerHTML = '<img src="/static/imgs/icon/小喇叭.png" alt="播放">';
                playButton.title = '播放语音';
                playButton.dataset.messageId = messageId;
                playButton.dataset.text = messageText.textContent;
                if (isOfflineMessage) {
                    playButton.dataset.offline = 'true';
                    playButton.onclick = (e) => {
                        e.stopPropagation();
                        playOfflineAudio(playButton);
                    };
                } else {
                    playButton.onclick = (e) => {
                        e.stopPropagation();
                        playTTS(messageText.textContent, playButton, messageId);
                    };
                }

                // 复制按钮
                const copyButton = document.createElement('button');
                copyButton.className = 'message-action-btn message-copy-btn';
                copyButton.innerHTML = '<img src="/static/imgs/icon/复制.png" alt="复制">';
                copyButton.title = '复制文本';
                copyButton.dataset.messageId = messageId;
                copyButton.dataset.text = messageText.textContent;
                copyButton.onclick = (e) => {
                    e.stopPropagation();
                    copyText(messageText.textContent, copyButton);
                };

                buttonContainer.appendChild(playButton);
                buttonContainer.appendChild(copyButton);
                messageDiv.appendChild(buttonContainer);
            } else if (existingButtonContainer) {
                // 更新现有按钮的数据，使用最新内容
                const playButton = existingButtonContainer.querySelector('.message-play-btn');
                const copyButton = existingButtonContainer.querySelector('.message-copy-btn');
                if (playButton) {
                    // 检查是否是离线消息
                    const isOfflineMessage = messageText.textContent.trim() === '人家也是需要睡觉的~';
                    if (isOfflineMessage) {
                        messageDiv.dataset.offline = 'true';
                        playButton.dataset.offline = 'true';
                        playButton.onclick = (e) => {
                            e.stopPropagation();
                            playOfflineAudio(playButton);
                        };
                    } else {
                        playButton.dataset.offline = 'false';
                        playButton.onclick = (e) => {
                            e.stopPropagation();
                            playTTS(messageText.textContent, playButton, messageId);
                        };
                    }
                    playButton.dataset.messageId = messageId;
                    playButton.dataset.text = messageText.textContent;
                }
                if (copyButton) {
                    copyButton.dataset.messageId = messageId;
                    copyButton.dataset.text = messageText.textContent;
                    copyButton.onclick = (e) => {
                        e.stopPropagation();
                        copyText(messageText.textContent, copyButton);
                    };
                }
            }
        }

        // 滚动到底部
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// 重置消息区域为初始状态
function resetMessages() {
    const chatMessages = document.getElementById('chatMessages');

    // 移除所有消息元素和备注框，保留装饰图片
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());

    // 移除所有备注框（通过类名查找）
    const notes = chatMessages.querySelectorAll('.message-note');
    notes.forEach(note => note.remove());

    // 先创建备注框（先渲染备注框）
    const messageId = 'msg_' + Date.now() + '_' + Math.random();
    const skillsNote = createSkillsNote('assistant', messageId);
    if (skillsNote) {
        chatMessages.appendChild(skillsNote);
    }

    // 延迟0.88秒后添加初始消息（后渲染消息）
    setTimeout(() => {
        const initialMessage = document.createElement('div');
        initialMessage.className = 'message assistant';
        initialMessage.id = messageId;
        const avatar = createAIAvatarElement();
        initialMessage.appendChild(avatar);
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = '期待你的输入ing...';
        messageContent.appendChild(messageText);
        initialMessage.appendChild(messageContent);
        chatMessages.appendChild(initialMessage);

        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 880);
}

/**
 * 创建备注框元素（不插入DOM，用于先创建备注框的场景）
 * @param {string} role - 消息角色 ('assistant' | 'user')
 * @param {Object} options - 配置选项
 * @param {string} options.title - 备注框标题
 * @param {Array|string} options.content - 备注框内容（数组或字符串）
 * @param {string} options.messageId - 关联的消息ID（可选）
 * @returns {HTMLElement} 返回创建的备注框元素
 */
function createMessageNote(role = 'assistant', options = {}) {
    const { title = '', content = [], messageId = null } = options;

    // 创建备注框
    const noteDiv = document.createElement('div');
    noteDiv.className = 'message-note';
    if (role === 'assistant') {
        noteDiv.classList.add('note-assistant');
    } else if (role === 'user') {
        noteDiv.classList.add('note-user');
    }

    // 关联消息ID（如果有）
    if (messageId) {
        noteDiv.setAttribute('data-message-id', messageId);
    }

    // 如果有标题，添加标题
    if (title) {
        const titleDiv = document.createElement('div');
        titleDiv.className = 'message-note-title';
        titleDiv.textContent = title;
        noteDiv.appendChild(titleDiv);
    }

    // 添加内容
    if (typeof content === 'string') {
        // 如果是字符串，直接显示
        noteDiv.appendChild(document.createTextNode(content));
    } else if (Array.isArray(content) && content.length > 0) {
        // 如果是数组，创建列表
        const list = document.createElement('ul');
        list.className = 'message-note-list';
        content.forEach(item => {
            const listItem = document.createElement('li');
            listItem.textContent = item;
            list.appendChild(listItem);
        });
        noteDiv.appendChild(list);
    }

    return noteDiv;
}

/**
 * 在指定消息上方添加备注框（独立元素，不在消息内容内部）
 * 可复用，用于显示技能、思考过程等
 * @param {HTMLElement|string} messageElement - 消息元素或消息ID
 * @param {Object} options - 配置选项
 * @param {string} options.title - 备注框标题
 * @param {Array|string} options.content - 备注框内容（数组或字符串）
 * @param {string} options.type - 备注框类型（'skills' | 'thinking' | 'custom'）
 * @returns {HTMLElement|null} 返回创建的备注框元素，失败时返回null
 */
function addMessageNote(messageElement, options = {}) {
    const { title = '', content = [], type = 'custom' } = options;

    // 如果传入的是ID字符串，获取元素
    let messageDiv;
    if (typeof messageElement === 'string') {
        messageDiv = document.getElementById(messageElement);
    } else {
        messageDiv = messageElement;
    }

    if (!messageDiv) {
        console.warn('无法找到消息元素，无法添加备注框');
        return null;
    }

    // 检查是否已存在备注框，如果存在则移除（通过消息ID查找，因为备注框在消息外部）
    const messageId = messageDiv.id;
    if (messageId) {
        const existingNote = document.querySelector(`.message-note[data-message-id="${messageId}"]`);
        if (existingNote) {
            existingNote.remove();
        }
    }

    // 获取消息的角色类型，用于设置备注框样式
    const role = messageDiv.classList.contains('assistant') ? 'assistant' : 'user';

    // 使用 createMessageNote 创建备注框
    const noteDiv = createMessageNote(role, {
        title: title,
        content: content,
        messageId: messageId
    });

    // 将备注框添加到消息元素的上方（作为独立元素，不在消息内部）
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages && messageDiv.parentNode === chatMessages) {
        // 在消息元素之前插入备注框
        chatMessages.insertBefore(noteDiv, messageDiv);
    } else if (messageDiv.parentNode) {
        // 如果消息不在chatMessages中，在消息之前插入
        messageDiv.parentNode.insertBefore(noteDiv, messageDiv);
    } else {
        console.warn('无法找到消息的父元素，无法添加备注框');
        return null;
    }

    // 滚动到底部
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    return noteDiv;
}

/**
 * 创建技能提示备注框（先创建备注框，用于在消息之前渲染）
 * @param {string} role - 消息角色 ('assistant' | 'user')
 * @param {string} messageId - 关联的消息ID
 * @returns {HTMLElement} 返回创建的备注框元素
 */
function createSkillsNote(role = 'assistant', messageId = null) {
    const skills = [
        '获取天气信息：告诉我城市名称或位置，我可以为你查询天气',
        '联网搜索：搜索最新信息，帮你获取实时资讯',
        '发送表情包：我会根据对话内容自动发送相关表情包,你懂概率的',
        '收藏图片：问我最喜欢的图片，我会分享收藏的图片给你,站主收藏款请勿外传',
        '图像生成：根据你的描述，我可以为你生成图片,40s左右',
        '视频生成：根据你的描述，我可以为你生成视频,100s左右',
        '(人家可以看懂你发送的图片哦)'
    ];

    return createMessageNote(role, {
        title: '这是我的技能ovo',
        content: skills,
        messageId: messageId
    });
}

/**
 * 显示技能提示框（封装函数，方便调用 - 用于已有消息的场景）
 * @param {HTMLElement|string} messageElement - 消息元素或消息ID
 */
function showSkillsNote(messageElement) {
    const skills = [
        '获取天气信息：告诉我城市名称或位置，我可以为你查询天气',
        '联网搜索：搜索最新信息，帮你获取实时资讯',
        '发送表情包：我会根据对话内容自动发送相关表情包,你懂概率的',
        '收藏图片：问我最喜欢的图片，我会分享收藏的图片给你,站主收藏款请勿外传',
        '图像生成：根据你的描述，我可以为你生成图片,40s左右',
        '视频生成：根据你的描述，我可以为你生成视频,100s左右',
        '(人家可以看懂你发送的图片哦)'

    ];

    addMessageNote(messageElement, {
        title: '这是我的技能ovo',
        content: skills,
        type: 'skills'
    });
}

// 全局 ESC 键事件处理器（避免重复添加监听器）
let imageModalEscHandler = null;
let videoModalEscHandler = null;
let aiInfoModalEscHandler = null;
let userInfoModalEscHandler = null;

/**
 * 打开图片模态框
 * @param {string} imageUrl - 图片URL
 */
function openImageModal(imageUrl) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');

    if (modal && modalImage) {
        modalImage.src = imageUrl;
        modal.classList.add('active');
        // 防止背景滚动
        document.body.style.overflow = 'hidden';

        // 如果还没有添加 ESC 键监听器，则添加
        if (!imageModalEscHandler) {
            imageModalEscHandler = (e) => {
                if (e.key === 'Escape') {
                    const modal = document.getElementById('imageModal');
                    if (modal && modal.classList.contains('active')) {
                        closeImageModal();
                    }
                }
            };
            document.addEventListener('keydown', imageModalEscHandler);
        }
    }
}

/**
 * 关闭图片模态框
 * @param {Event} event - 事件对象（可选，用于判断点击位置）
 */
function closeImageModal(event) {
    // 如果传入了事件对象，检查点击位置
    if (event && event.target) {
        // 如果点击的是图片内容区域（但不是关闭按钮），则不关闭
        const isCloseButton = event.target.classList.contains('image-modal-close');
        const isBackground = event.target.id === 'imageModal';
        const isContentArea = event.target.closest('.image-modal-content');

        // 只有当点击的是关闭按钮或背景时才关闭
        if (!isCloseButton && !isBackground) {
            return;
        }
    }

    const modal = document.getElementById('imageModal');
    if (modal && modal.classList.contains('active')) {
        modal.classList.remove('active');
        // 恢复背景滚动
        document.body.style.overflow = '';
    }
}

/**
 * 打开视频模态框
 * @param {string} videoUrl - 视频URL
 */
function openVideoModal(videoUrl) {
    const modal = document.getElementById('videoModal');
    const modalVideo = document.getElementById('modalVideo');

    if (modal && modalVideo) {
        modalVideo.src = videoUrl;
        modal.classList.add('active');
        // 防止背景滚动
        document.body.style.overflow = 'hidden';

        // 如果还没有添加 ESC 键监听器，则添加
        if (!videoModalEscHandler) {
            videoModalEscHandler = (e) => {
                if (e.key === 'Escape') {
                    const modal = document.getElementById('videoModal');
                    if (modal && modal.classList.contains('active')) {
                        closeVideoModal();
                    }
                }
            };
            document.addEventListener('keydown', videoModalEscHandler);
        }
    }
}

/**
 * 关闭视频模态框
 * @param {Event} event - 事件对象（可选，用于判断点击位置）
 */
function closeVideoModal(event) {
    // 如果传入了事件对象，检查点击位置
    if (event && event.target) {
        // 如果点击的是视频内容区域（但不是关闭按钮），则不关闭
        const isCloseButton = event.target.classList.contains('video-modal-close');
        const isBackground = event.target.id === 'videoModal';
        const isContentArea = event.target.closest('.video-modal-content');

        // 只有当点击的是关闭按钮或背景时才关闭
        if (!isCloseButton && !isBackground) {
            return;
        }
    }

    const modal = document.getElementById('videoModal');
    if (modal && modal.classList.contains('active')) {
        modal.classList.remove('active');
        // 停止视频播放
        const modalVideo = document.getElementById('modalVideo');
        if (modalVideo) {
            modalVideo.pause();
            modalVideo.src = '';
        }
        // 恢复背景滚动
        document.body.style.overflow = '';
    }
}

/**
 * 获取智能体的在线状态
 * @param {string} mode - 智能体模式，默认为 'normal'
 * @returns {Promise<boolean>} 返回是否在线
 */
async function getAgentStatus(mode = 'normal') {
    try {
        const response = await fetch(`/api/chat/agent/status?mode=${mode}`);
        if (!response.ok) {
            console.error('获取智能体状态失败:', response.status);
            return true; // 默认返回在线状态
        }
        const data = await response.json();
        return data.is_online === true;
    } catch (error) {
        console.error('获取智能体状态出错:', error);
        return true; // 默认返回在线状态
    }
}

/**
 * 更新标题栏中的dodokolu智能体在线状态显示
 * @param {string} mode - 智能体模式，默认为 'dodokolu'
 */
async function updateHeaderAgentStatus(mode = 'dodokolu') {
    const statusElement = document.getElementById('agentStatus');
    if (!statusElement) {
        return;
    }

    // 设置为检查中状态
    statusElement.classList.remove('online', 'offline');
    statusElement.classList.add('checking');
    const statusText = statusElement.querySelector('.status-text');
    if (statusText) {
        statusText.textContent = '检查中...';
    }

    try {
        const isOnline = await getAgentStatus(mode);
        statusElement.classList.remove('checking');
        statusElement.classList.add(isOnline ? 'online' : 'offline');
        if (statusText) {
            statusText.textContent = isOnline ? '在线' : '离线';
        }
    } catch (error) {
        console.error('更新标题栏在线状态失败:', error);
        statusElement.classList.remove('checking');
        statusElement.classList.add('offline');
        if (statusText) {
            statusText.textContent = '离线';
        }
    }
}

/**
 * 更新AI信息模态框中的在线状态显示
 * @param {string} mode - 智能体模式，默认为 'normal'
 */
async function updateAgentStatusDisplay(mode = 'normal') {
    // 查找状态元素：优先查找已有的状态元素，否则通过标签查找
    let statusElement = document.querySelector('#aiInfoModal .stat-value.online, #aiInfoModal .stat-value.offline');

    if (!statusElement) {
        // 如果找不到已有的状态元素，通过标签查找
        const statItems = document.querySelectorAll('#aiInfoModal .ai-info-stat-item');
        for (let item of statItems) {
            const label = item.querySelector('.stat-label');
            if (label && label.textContent.trim() === '状态') {
                statusElement = item.querySelector('.stat-value');
                break;
            }
        }
    }

    if (!statusElement) {
        console.warn('无法找到状态显示元素');
        return;
    }

    try {
        const isOnline = await getAgentStatus(mode);
        statusElement.textContent = isOnline ? '在线' : '离线';
        statusElement.classList.remove('online', 'offline');
        statusElement.classList.add(isOnline ? 'online' : 'offline');
    } catch (error) {
        console.error('更新在线状态显示失败:', error);
    }
}

/**
 * 打开AI信息模态框
 * @param {string} avatarPath - AI头像路径
 */
function openAIInfoModal(avatarPath) {
    const modal = document.getElementById('aiInfoModal');
    const modalAvatar = document.getElementById('aiInfoAvatar');

    if (modal && modalAvatar) {
        // 设置头像
        modalAvatar.src = avatarPath;
        modal.classList.add('active');
        // 防止背景滚动
        document.body.style.overflow = 'hidden';

        // 更新在线状态显示
        // 获取当前模式（从全局变量获取，默认为 'normal'）
        const mode = typeof currentMode !== 'undefined' ? currentMode : 'normal';
        updateAgentStatusDisplay(mode);

        // 如果还没有添加 ESC 键监听器，则添加
        if (!aiInfoModalEscHandler) {
            aiInfoModalEscHandler = (e) => {
                if (e.key === 'Escape') {
                    const modal = document.getElementById('aiInfoModal');
                    if (modal && modal.classList.contains('active')) {
                        closeAIInfoModal();
                    }
                }
            };
            document.addEventListener('keydown', aiInfoModalEscHandler);
        }
    }
}

/**
 * 关闭AI信息模态框
 * @param {Event} event - 事件对象（可选，用于判断点击位置）
 */
function closeAIInfoModal(event) {
    // 如果传入了事件对象，检查点击位置
    if (event && event.target) {
        // 如果点击的是内容区域（但不是关闭按钮），则不关闭
        const isCloseButton = event.target.classList.contains('ai-info-modal-close');
        const isBackground = event.target.id === 'aiInfoModal';
        const isContentArea = event.target.closest('.ai-info-modal-content');

        // 只有当点击的是关闭按钮或背景时才关闭
        if (!isCloseButton && !isBackground) {
            return;
        }
    }

    const modal = document.getElementById('aiInfoModal');
    if (modal && modal.classList.contains('active')) {
        modal.classList.remove('active');
        // 恢复背景滚动
        document.body.style.overflow = '';
    }
}

/**
 * 打开用户信息模态框
 */
async function openUserInfoModal() {
    const modal = document.getElementById('userInfoModal');
    if (!modal) {
        console.warn('用户信息模态框元素未找到');
        return;
    }

    // 显示模态框
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // 获取用户信息和头像
    try {
        const response = await fetch('/api/account/profile');
        if (response.status === 401) {
            // 未登录
            document.getElementById('userInfoName').textContent = '未登录';
            document.getElementById('userInfoEmail').textContent = '请先登录';
            document.getElementById('userInfoId').textContent = '-';
            document.getElementById('userInfoCreatedAt').textContent = '-';
            // 隐藏头像，显示占位符
            document.getElementById('userInfoAvatar').style.display = 'none';
            document.getElementById('userInfoAvatarPlaceholder').style.display = 'flex';
        } else if (response.ok) {
            const data = await response.json();
            if (data.success && data.data) {
                const profile = data.data;
                document.getElementById('userInfoName').textContent = profile.username || '用户';
                document.getElementById('userInfoEmail').textContent = profile.email || '未设置';
                document.getElementById('userInfoId').textContent = profile.id || '-';
                // 格式化注册时间
                if (profile.created_at) {
                    const date = new Date(profile.created_at);
                    document.getElementById('userInfoCreatedAt').textContent = date.toLocaleDateString('zh-CN');
                } else {
                    document.getElementById('userInfoCreatedAt').textContent = '-';
                }
            } else {
                document.getElementById('userInfoName').textContent = '获取失败';
                document.getElementById('userInfoEmail').textContent = data.message || '未知错误';
                document.getElementById('userInfoId').textContent = '-';
                document.getElementById('userInfoCreatedAt').textContent = '-';
            }
        } else {
            document.getElementById('userInfoName').textContent = '获取失败';
            document.getElementById('userInfoEmail').textContent = '网络错误';
            document.getElementById('userInfoId').textContent = '-';
            document.getElementById('userInfoCreatedAt').textContent = '-';
        }

        // 获取用户头像
        try {
            const avatarResponse = await fetch('/api/user/avatar');
            if (avatarResponse.ok) {
                const avatarData = await avatarResponse.json();
                if (avatarData.success && avatarData.has_avatar && avatarData.avatar_url) {
                    const avatarImg = document.getElementById('userInfoAvatar');
                    const avatarPlaceholder = document.getElementById('userInfoAvatarPlaceholder');
                    avatarImg.src = avatarData.avatar_url;
                    avatarImg.style.display = 'block';
                    avatarPlaceholder.style.display = 'none';
                } else {
                    // 没有头像，显示占位符
                    document.getElementById('userInfoAvatar').style.display = 'none';
                    document.getElementById('userInfoAvatarPlaceholder').style.display = 'flex';
                }
            }
        } catch (avatarError) {
            console.error('获取头像失败:', avatarError);
            // 显示占位符
            document.getElementById('userInfoAvatar').style.display = 'none';
            document.getElementById('userInfoAvatarPlaceholder').style.display = 'flex';
        }
    } catch (error) {
        console.error('获取用户信息失败:', error);
        document.getElementById('userInfoName').textContent = '获取失败';
        document.getElementById('userInfoEmail').textContent = '网络错误';
        document.getElementById('userInfoId').textContent = '-';
        document.getElementById('userInfoCreatedAt').textContent = '-';
    }

    // 如果还没有添加 ESC 键监听器，则添加
    if (!userInfoModalEscHandler) {
        userInfoModalEscHandler = (e) => {
            if (e.key === 'Escape') {
                const modal = document.getElementById('userInfoModal');
                if (modal && modal.classList.contains('active')) {
                    closeUserInfoModal();
                }
            }
        };
        document.addEventListener('keydown', userInfoModalEscHandler);
    }
}

/**
 * 关闭用户信息模态框
 * @param {Event} event - 事件对象（可选，用于判断点击位置）
 */
function closeUserInfoModal(event) {
    // 如果传入了事件对象，检查点击位置
    if (event && event.target) {
        // 如果点击的是内容区域（但不是关闭按钮），则不关闭
        const isCloseButton = event.target.classList.contains('ai-info-modal-close');
        const isBackground = event.target.id === 'userInfoModal';
        const isContentArea = event.target.closest('.ai-info-modal-content');

        // 只有当点击的是关闭按钮或背景时才关闭
        if (!isCloseButton && !isBackground) {
            return;
        }
    }

    const modal = document.getElementById('userInfoModal');
    if (modal && modal.classList.contains('active')) {
        modal.classList.remove('active');
        // 恢复背景滚动
        document.body.style.overflow = '';
    }
}

/**
 * 处理头像上传
 * @param {Event} event - 文件选择事件
 */
async function handleAvatarUpload(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    // 验证文件类型
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
        alert('仅支持 PNG 或 JPG 格式的图片');
        event.target.value = ''; // 清空选择
        return;
    }

    // 验证文件大小（限制为5MB）
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
        alert('图片大小不能超过 5MB');
        event.target.value = ''; // 清空选择
        return;
    }

    // 创建 FormData
    const formData = new FormData();
    formData.append('avatar', file);

    try {
        const response = await fetch('/api/user/upload-avatar', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 更新头像显示
            const avatarImg = document.getElementById('userInfoAvatar');
            const avatarPlaceholder = document.getElementById('userInfoAvatarPlaceholder');
            avatarImg.src = data.avatar_url + '?t=' + Date.now(); // 添加时间戳防止缓存
            avatarImg.style.display = 'block';
            avatarPlaceholder.style.display = 'none';

            // 更新聊天界面中的用户头像
            updateUserAvatarInChat(data.avatar_url);

            alert('头像上传成功！');
        } else {
            alert(data.message || '头像上传失败');
        }
    } catch (error) {
        console.error('上传头像失败:', error);
        alert('头像上传失败，请稍后重试');
    }

    // 清空文件选择，允许重复选择同一文件
    event.target.value = '';
}

/**
 * 更新聊天界面中的用户头像
 * @param {string} avatarUrl - 头像URL
 */
function updateUserAvatarInChat(avatarUrl) {
    // 更新全局变量
    userAvatarUrl = avatarUrl;

    // 更新所有用户消息中的头像
    const userAvatars = document.querySelectorAll('.message.user .message-avatar');
    userAvatars.forEach(avatarDiv => {
        const existingImg = avatarDiv.querySelector('img');
        if (existingImg) {
            // 如果已经有图片，更新URL
            existingImg.src = avatarUrl + '?t=' + Date.now();
        } else if (avatarDiv.textContent === '我') {
            // 如果是文本，替换为图片
            avatarDiv.textContent = '';
            const img = document.createElement('img');
            img.src = avatarUrl + '?t=' + Date.now();
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
                openUserInfoModal();
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
        }
    });
}

// TTS 播放相关变量
let currentAudio = null;
let currentTTSButton = null;

// TTS 音频缓存（存储已生成的音频URL）
const ttsAudioCache = new Map();

// 音频生成模态框相关变量
let audioGeneratingClickHandler = null;

/**
 * 显示音频生成模态框并阻止所有点击事件
 */
function showAudioGeneratingModal() {
    const modal = document.getElementById('audioGeneratingModal');
    if (!modal) {
        console.warn('音频生成模态框元素未找到');
        return;
    }

    // 显示模态框
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // 确保图片加载（如果图片加载失败，至少显示文字）
    const img = modal.querySelector('.audio-generating-image');
    if (img) {
        img.onerror = function () {
            console.warn('音频生成表情包图片加载失败，但模态框仍会显示');
            // 图片加载失败时，至少确保文字可见
            this.style.display = 'none';
        };
        // 如果图片还没有加载，强制重新加载
        if (!img.complete || img.naturalHeight === 0) {
            const src = img.src;
            img.src = '';
            img.src = src;
        }
    }

    // 阻止所有点击事件
    audioGeneratingClickHandler = (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        return false;
    };

    // 在捕获阶段阻止所有点击事件
    document.addEventListener('click', audioGeneratingClickHandler, true);
    document.addEventListener('mousedown', audioGeneratingClickHandler, true);
    document.addEventListener('touchstart', audioGeneratingClickHandler, true);
}

/**
 * 隐藏音频生成模态框并恢复点击事件
 */
function hideAudioGeneratingModal() {
    const modal = document.getElementById('audioGeneratingModal');
    if (modal) {
        modal.classList.remove('active');
    }
    document.body.style.overflow = '';

    // 恢复点击事件
    if (audioGeneratingClickHandler) {
        document.removeEventListener('click', audioGeneratingClickHandler, true);
        document.removeEventListener('mousedown', audioGeneratingClickHandler, true);
        document.removeEventListener('touchstart', audioGeneratingClickHandler, true);
        audioGeneratingClickHandler = null;
    }
}

/**
 * 检查音频文件是否存在
 * @param {string} audioUrl - 音频文件URL
 * @returns {Promise<boolean>} 文件是否存在
 */
async function checkAudioExists(audioUrl) {
    try {
        const response = await fetch(audioUrl, { method: 'HEAD' });
        return response.ok;
    } catch (error) {
        return false;
    }
}

/**
 * 播放离线系统音频
 * @param {HTMLElement} button - 触发按钮元素（可选）
 * @param {boolean} autoPlay - 是否自动播放（默认false）
 */
function playOfflineAudio(button = null, autoPlay = false) {
    // 如果正在播放，先停止
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }

    // 如果提供了按钮，处理按钮状态
    if (button) {
        // 如果点击的是同一个按钮，重置状态
        if (currentTTSButton === button && button.classList.contains('playing')) {
            currentTTSButton = null;
            button.classList.remove('playing');
            return;
        }

        // 重置之前按钮的状态
        if (currentTTSButton && currentTTSButton !== button) {
            currentTTSButton.classList.remove('playing');
        }

        currentTTSButton = button;
        button.classList.add('playing');
    }

    // 播放系统音频
    const systemAudioUrl = '/static/audio/system_audio/request_close.mp3';
    const audio = new Audio(systemAudioUrl);
    currentAudio = audio;

    audio.onended = () => {
        if (button) {
            button.classList.remove('playing');
            currentTTSButton = null;
        }
        currentAudio = null;
    };

    audio.onerror = () => {
        console.error('系统音频播放失败');
        if (button) {
            button.classList.remove('playing');
            currentTTSButton = null;
        }
        currentAudio = null;
    };

    audio.play().catch(error => {
        console.error('播放系统音频失败:', error);
        if (button) {
            button.classList.remove('playing');
            currentTTSButton = null;
        }
        currentAudio = null;
    });
}

/**
 * 播放 TTS 语音
 * @param {string} text - 要转换为语音的文本
 * @param {HTMLElement} button - 触发按钮元素
 * @param {string} messageId - 消息ID（可选，用于缓存）
 */
async function playTTS(text, button, messageId = null) {
    // 检查是否是离线消息，如果是则直接播放系统音频
    if (button && button.dataset.offline === 'true') {
        playOfflineAudio(button);
        return;
    }

    // 如果按钮被禁用，不允许点击
    if (button.classList.contains('disabled')) {
        return;
    }

    // 如果正在播放，先停止
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }

    // 如果点击的是同一个按钮，重置状态
    if (currentTTSButton === button && button.classList.contains('playing')) {
        currentTTSButton = null;
        button.classList.remove('playing');
        return;
    }

    // 重置之前按钮的状态
    if (currentTTSButton && currentTTSButton !== button) {
        currentTTSButton.classList.remove('playing');
    }

    // 禁用按钮，防止重复点击（不显示加载动画）
    button.classList.add('disabled');
    currentTTSButton = button;

    // 先显示音频生成模态框（在检查缓存之前，确保用户能看到加载状态）
    showAudioGeneratingModal();

    try {
        // 检查缓存：如果按钮已有存储的音频URL，先检查文件是否存在
        const cachedAudioUrl = button.dataset.audioUrl;
        if (cachedAudioUrl) {
            // 检查文件是否存在
            const exists = await checkAudioExists(cachedAudioUrl);
            if (exists) {
                // 文件存在，直接播放，隐藏模态框
                hideAudioGeneratingModal();

                button.classList.remove('disabled');
                button.classList.add('playing');

                const audio = new Audio(cachedAudioUrl);
                currentAudio = audio;

                audio.onended = () => {
                    button.classList.remove('playing');
                    currentTTSButton = null;
                    currentAudio = null;
                };

                audio.onerror = () => {
                    button.classList.remove('playing');
                    currentTTSButton = null;
                    currentAudio = null;
                    // 缓存失效，清除
                    delete button.dataset.audioUrl;
                    alert('音频播放失败，请重试');
                };

                await audio.play();
                return;
            } else {
                // 文件不存在，清除缓存，继续生成（模态框保持显示）
                delete button.dataset.audioUrl;
            }
        }

        // 模态框已经在上面显示了，这里不需要再次显示

        // 调用后端 API 生成语音（传递 message_id 用于缓存）
        const requestBody = { text: text };
        if (messageId) {
            requestBody.message_id = messageId;
        }

        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        // 隐藏音频生成模态框并恢复点击
        hideAudioGeneratingModal();

        if (!response.ok || !data.success) {
            throw new Error(data.error || '语音生成失败');
        }

        // 将音频URL存储到按钮和缓存中
        button.dataset.audioUrl = data.audio_url;
        if (messageId) {
            ttsAudioCache.set(messageId, data.audio_url);
        }

        // 移除禁用状态，添加播放状态
        button.classList.remove('disabled');
        button.classList.add('playing');

        // 创建音频元素并播放
        const audio = new Audio(data.audio_url);
        currentAudio = audio;

        audio.onended = () => {
            button.classList.remove('playing');
            currentTTSButton = null;
            currentAudio = null;
        };

        audio.onerror = () => {
            button.classList.remove('playing');
            currentTTSButton = null;
            currentAudio = null;
            // 清除缓存
            delete button.dataset.audioUrl;
            if (messageId) {
                ttsAudioCache.delete(messageId);
            }
            alert('音频播放失败');
        };

        await audio.play();

    } catch (error) {
        console.error('TTS 播放错误:', error);
        // 确保在错误时也隐藏模态框
        hideAudioGeneratingModal();
        button.classList.remove('playing', 'disabled');
        currentTTSButton = null;
        alert('语音生成失败: ' + error.message);
    }
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @param {HTMLElement} button - 触发按钮元素
 */
async function copyText(text, button) {
    try {
        // 检查是否支持现代 Clipboard API（需要 HTTPS 或 localhost）
        if (navigator.clipboard && navigator.clipboard.writeText) {
            // 使用现代 Clipboard API
            await navigator.clipboard.writeText(text);
        } else {
            // 回退到传统方法（适用于非 HTTPS 环境）
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            try {
                const successful = document.execCommand('copy');
                if (!successful) {
                    throw new Error('execCommand 复制失败');
                }
            } finally {
                document.body.removeChild(textArea);
            }
        }

        // 播放复制成功音频
        const audio = new Audio('/static/audio/system_audio/copy.mp3');
        audio.play().catch(err => {
            console.warn('播放复制音频失败:', err);
        });

        // 显示复制成功提示
        const originalTitle = button.title;
        button.title = '复制成功！';

        // 恢复原始标题
        setTimeout(() => {
            button.title = originalTitle;
        }, 2000);
    } catch (error) {
        console.error('复制失败:', error);
        alert('复制失败，请稍后重试');
    }
}

