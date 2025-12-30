// 聊天区域API调用和主要功能

// 发送消息
async function sendMessage() {
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

    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const message = chatInput.value.trim();
    const hasImage = currentImageFile !== null;

    // 如果没有消息也没有图片，则不发送
    if ((!message && !hasImage) || isStreaming) return;

    // 检测指令模式：如果消息以 /image 或 /video 开头，触发指令流程
    // 但如果消息包含 [已成功生成] 标记，说明这是自动触发的AI响应消息，应该跳过指令处理
    if ((message.startsWith('/image ') || message.startsWith('/video ')) && !message.includes('[已成功生成]')) {
        // 拦截消息发送，触发指令流程
        const commandType = message.startsWith('/image ') ? 'image' : 'video';
        window.selectedCommandType = commandType;
        // 直接处理指令，无需密钥验证
        if (typeof processCommand === 'function') {
            processCommand(commandType);
        }
        // 清空输入框
        chatInput.value = '';
        chatInput.style.height = 'auto';
        return;
    }

    // 检查消息是否包含[已成功生成]标记，如果有则不显示消息框
    const isSuccessMessage = message.includes('[已成功生成]');

    // 保存图片文件引用（在重置前保存，必须在 removeImage() 之前）
    const imageFileToUpload = hasImage ? currentImageFile : null;

    // 添加用户消息到界面（如果有图片，显示图片预览）
    // 注意：如果消息包含[已成功生成]标记，不显示消息框
    if (!isSuccessMessage) {
        let userMessageContent = message;
        if (hasImage && currentImageUrl) {
            userMessageContent = message || '[图片]';
            // 保存图片URL用于显示预览
            const imageUrlForPreview = currentImageUrl;
            addMessage('user', userMessageContent, {
                imagePreview: true,
                imageUrl: imageUrlForPreview
            });
        } else {
            addMessage('user', userMessageContent);
        }
    }

    // 立即重置对话框（清空输入框和图片预览）
    chatInput.value = '';
    chatInput.style.height = 'auto';
    removeImage();

    // 如果有图片，先上传图片并识别
    let imageDescription = null;
    let imageFilename = null;
    if (hasImage && imageFileToUpload) {
        try {
            // 上传图片
            const formData = new FormData();
            formData.append('image', imageFileToUpload);

            const uploadResponse = await fetch('/api/chat/upload-image', {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                const errorData = await uploadResponse.json().catch(() => ({}));
                const errorMessage = errorData.error || '图片上传失败';
                // 如果是未登录错误，调用登录提示函数
                if (errorMessage.includes('登录了吗') || errorMessage.includes('Token') || uploadResponse.status === 401) {
                    promptLoginRequired();
                    return;
                }
                throw new Error(errorMessage);
            }

            const uploadData = await uploadResponse.json();
            if (!uploadData.success) {
                const errorMessage = uploadData.error || '图片上传失败';
                // 如果是未登录错误，调用登录提示函数
                if (errorMessage.includes('登录了吗') || errorMessage.includes('Token')) {
                    promptLoginRequired();
                    return;
                }
                throw new Error(errorMessage);
            }
            imageDescription = uploadData.description;
            imageFilename = uploadData.filename;
        } catch (error) {
            console.error('图片上传/识别错误:', error);
            // 如果是未登录错误，已经在上面的处理中跳转了，这里不需要再处理
            if (error.message && (error.message.includes('登录了吗') || error.message.includes('Token'))) {
                return;
            }
            addMessage('assistant', '抱歉，图片处理失败。请稍后重试。');
            isStreaming = false;
            sendBtn.disabled = false;
            return;
        }
    }

    sendBtn.disabled = true;
    isStreaming = true;

    try {
        // 如果有图片，先显示识别提示
        let assistantMessageId;
        let isImageResponse = false;
        if (hasImage && imageDescription) {
            isImageResponse = true;
            // 立即显示提示信息
            assistantMessageId = addMessage('assistant', '[检测到图片，给我点时间，让我看看]', { loading: false });
            // 等待一小段时间让用户看到提示
            await new Promise(resolve => setTimeout(resolve, 800));

            // 更新为等待动画
            const messageDiv = document.getElementById(assistantMessageId);
            if (messageDiv) {
                const messageContent = messageDiv.querySelector('.message-content');
                const messageText = messageDiv.querySelector('.message-text');
                if (messageContent && messageText) {
                    messageText.textContent = '';
                    const loadingWrap = document.createElement('div');
                    loadingWrap.className = 'message-loading';
                    loadingWrap.innerHTML = `
                        <span class="loader-dot"></span>
                        <span class="loader-dot"></span>
                        <span class="loader-dot"></span>
                    `;
                    messageContent.appendChild(loadingWrap);
                    messageDiv.dataset.loading = 'true';
                }
            }
        } else {
            assistantMessageId = addMessage('assistant', '', { loading: true });
        }

        // 检查是否需要包含位置信息（如果消息与天气相关）
        const locationContext = isWeatherRelated(message) ? getLocationContext() : null;

        // 构建最终消息（包含图片描述）
        let finalMessage = message;
        if (imageDescription) {
            finalMessage = message
                ? `${message}\n\n[图片内容：${imageDescription}]`
                : `[图片内容：${imageDescription}]`;
        }

        // 发送请求到后端
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: finalMessage,
                session_id: sessionId,
                mode: currentMode,
                location: userLocation ? {
                    latitude: userLocation.latitude,
                    longitude: userLocation.longitude
                } : null,
                image_filename: imageFilename  // 发送图片文件名
            })
        });

        if (!response.ok) {
            // 如果是未登录错误，调用登录提示函数
            if (response.status === 401) {
                promptLoginRequired();
                isStreaming = false;
                sendBtn.disabled = false;
                return;
            }
            throw new Error('请求失败');
        }

        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let firstContentReceived = false;

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

                        // 处理表情包事件
                        if (data.type === 'emoji' && data.emoji_url) {
                            console.log('🎭 [前端] 收到表情包事件:', data);
                            // 创建表情包消息
                            addMessage('assistant', '', {
                                imageUrl: data.emoji_url,
                                imagePreview: true
                            });
                            continue;
                        }

                        // 处理收藏图片事件
                        if (data.type === 'favorite_image' && data.image_url) {
                            console.log('🖼️ [前端] 收到收藏图片事件:', data);
                            // 创建收藏图片消息
                            addMessage('assistant', '', {
                                imageUrl: data.image_url,
                                imagePreview: true
                            });
                            // 如果有描述，也显示出来
                            if (data.description) {
                                addMessage('assistant', data.description);
                            }
                            continue;
                        }

                        // 处理视频消息事件
                        if (data.type === 'video' && data.video_url) {
                            console.log('🎬 [前端] 收到视频消息事件:', data);
                            // 创建视频消息
                            addMessage('assistant', '', {
                                videoUrl: data.video_url,
                                videoPreview: true
                            });
                            // 如果有描述，也显示出来
                            if (data.description) {
                                addMessage('assistant', data.description);
                            }
                            continue;
                        }

                        if (data.content) {
                            // 如果是图片响应且首次收到内容，显示"响应成功!"然后消失
                            if (isImageResponse && !firstContentReceived) {
                                firstContentReceived = true;
                                const messageDiv = document.getElementById(assistantMessageId);
                                if (messageDiv) {
                                    const messageContent = messageDiv.querySelector('.message-content');
                                    const loadingWrap = messageDiv.querySelector('.message-loading');
                                    const messageText = messageDiv.querySelector('.message-text');

                                    if (messageContent && loadingWrap && messageText) {
                                        // 移除加载动画
                                        loadingWrap.remove();
                                        // 显示"响应成功!"
                                        messageText.textContent = '响应成功!';
                                        messageText.style.display = '';
                                        messageText.classList.add('response-success');

                                        // 等待显示一段时间后缓慢消失
                                        await new Promise(resolve => setTimeout(resolve, 1000));

                                        // 添加淡出动画
                                        messageText.style.transition = 'opacity 0.5s ease-out';
                                        messageText.style.opacity = '0';

                                        await new Promise(resolve => setTimeout(resolve, 500));

                                        // 清空内容，准备流式输出
                                        messageText.textContent = '';
                                        messageText.style.opacity = '1';
                                        messageText.style.transition = '';
                                        messageText.classList.remove('response-success');
                                        delete messageDiv.dataset.loading;
                                    }
                                }
                                // 第一次内容也要输出（从头开始）
                                appendToMessage(assistantMessageId, data.content);
                            } else {
                                // 追加内容（流式输出）
                                appendToMessage(assistantMessageId, data.content);
                            }
                        }
                        if (data.done) {
                            isStreaming = false;
                            sendBtn.disabled = false;
                            
                            // 检查是否是离线消息，如果是则自动播放系统音频
                            const messageDiv = document.getElementById(assistantMessageId);
                            if (messageDiv) {
                                const messageText = messageDiv.querySelector('.message-text');
                                if (messageText && messageText.textContent.trim() === '人家也是需要睡觉的~') {
                                    // 标记为离线消息
                                    messageDiv.dataset.offline = 'true';
                                    // 更新播放按钮，使其直接播放系统音频
                                    const playButton = messageDiv.querySelector('.message-play-btn');
                                    if (playButton) {
                                        playButton.dataset.offline = 'true';
                                        playButton.onclick = (e) => {
                                            e.stopPropagation();
                                            playOfflineAudio(playButton);
                                        };
                                    }
                                    // 自动播放系统音频
                                    playOfflineAudio(null, true);
                                }
                            }
                        }
                    } catch (e) {
                        console.error('解析数据错误:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('发送消息错误:', error);
        // 如果是未登录错误，已经在上面的处理中跳转了，这里不需要再处理
        if (error.message && (error.message.includes('登录了吗') || error.message.includes('Token'))) {
            return;
        }
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

            // 移除消息元素和备注框，保留装饰图片
            const messages = chatMessages.querySelectorAll('.message');
            messages.forEach(msg => msg.remove());
            const notes = chatMessages.querySelectorAll('.message-note');
            notes.forEach(note => note.remove());

            data.history.forEach(msg => {
                // 跳过 system 和 tool 角色的消息（已在后端过滤，这里双重保险）
                if (msg.role === 'system' || msg.role === 'tool') {
                    return;
                }

                // 检查是否有图片URL（用户上传的图片或指令生成的图片）
                if (msg.image_url) {
                    const messageId = addMessage(msg.role, msg.content || '', {
                        imageUrl: msg.image_url,
                        imagePreview: true
                    });
                    // 如果有音频URL，设置到按钮
                    if (msg.audio_url && messageId) {
                        setTimeout(() => {
                            const messageDiv = document.getElementById(messageId);
                            if (messageDiv) {
                                const playButton = messageDiv.querySelector('.message-play-btn');
                                if (playButton) {
                                    playButton.dataset.audioUrl = msg.audio_url;
                                }
                            }
                        }, 100);
                    }
                }
                // 检查是否有视频URL（指令生成的视频）
                else if (msg.video_url) {
                    const messageId = addMessage(msg.role, msg.content || '', {
                        videoUrl: msg.video_url,
                        videoPreview: true
                    });
                    // 如果有音频URL，设置到按钮
                    if (msg.audio_url && messageId) {
                        setTimeout(() => {
                            const messageDiv = document.getElementById(messageId);
                            if (messageDiv) {
                                const playButton = messageDiv.querySelector('.message-play-btn');
                                if (playButton) {
                                    playButton.dataset.audioUrl = msg.audio_url;
                                }
                            }
                        }, 100);
                    }
                }
                // 普通文本消息
                else {
                    const messageId = addMessage(msg.role, msg.content || '');
                    // 如果有音频URL，设置到按钮
                    if (msg.audio_url && messageId) {
                        setTimeout(() => {
                            const messageDiv = document.getElementById(messageId);
                            if (messageDiv) {
                                const playButton = messageDiv.querySelector('.message-play-btn');
                                if (playButton) {
                                    playButton.dataset.audioUrl = msg.audio_url;
                                }
                            }
                        }, 100);
                    }
                }
            });
        }
    } catch (error) {
        console.error('加载历史记录错误:', error);
    }
}

// 清空历史
async function clearHistory() {
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
    alert('登录了吗，就想榨干我的Token(￣へ￣)');
    window.location.href = '/login';
}

// 切换模式（已移除，现在只有normal模式）
async function toggleMode() {
    // 模式切换功能已移除，现在只支持normal模式
    console.log('当前模式: normal（模式切换功能已移除）');
}

