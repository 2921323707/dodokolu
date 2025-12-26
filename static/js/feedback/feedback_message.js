// 反馈页面消息提示功能

// 显示消息提示（仅用于错误消息）
function showMessage(message, type, autoHideDelay = null) {
    if (type === 'error' && elements.feedbackMessage) {
        elements.feedbackMessage.textContent = message;
        elements.feedbackMessage.className = `feedback-message ${type}`;
        elements.feedbackMessage.style.display = 'block';
        
        // 如果设置了自动隐藏时间，则在指定时间后自动隐藏
        if (autoHideDelay !== null && autoHideDelay > 0) {
            setTimeout(() => {
                hideMessage();
            }, autoHideDelay);
        }
    }
}

// 隐藏消息提示
function hideMessage() {
    if (elements.feedbackMessage) {
        elements.feedbackMessage.style.display = 'none';
    }
}

