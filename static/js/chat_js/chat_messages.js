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
            ? (() => {
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = '我';
                return avatar;
            })()
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
                ? (() => {
                    const avatar = document.createElement('div');
                    avatar.className = 'message-avatar';
                    avatar.textContent = '我';
                    return avatar;
                })()
                : createAIAvatarElement();

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
            ? (() => {
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = '我';
                return avatar;
            })()
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
                ? (() => {
                    const avatar = document.createElement('div');
                    avatar.className = 'message-avatar';
                    avatar.textContent = '我';
                    return avatar;
                })()
                : createAIAvatarElement();

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

        // 返回文本消息的 ID（如果有），否则返回视频消息的 ID
        return textMessageId || videoMessageId;
    }

    // 正常消息处理（没有图片或视频预览）
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    const messageId = 'msg_' + Date.now() + '_' + Math.random();
    messageDiv.id = messageId;

    const avatar = role === 'user'
        ? (() => {
            const av = document.createElement('div');
            av.className = 'message-avatar';
            av.textContent = '我';
            return av;
        })()
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

