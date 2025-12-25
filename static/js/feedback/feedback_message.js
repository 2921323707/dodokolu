// 反馈页面消息提示功能

// 显示消息提示（仅用于错误消息）
function showMessage(message, type) {
    if (type === 'error' && elements.feedbackMessage) {
        elements.feedbackMessage.textContent = message;
        elements.feedbackMessage.className = `feedback-message ${type}`;
        elements.feedbackMessage.style.display = 'block';
    }
}

// 隐藏消息提示
function hideMessage() {
    if (elements.feedbackMessage) {
        elements.feedbackMessage.style.display = 'none';
    }
}

