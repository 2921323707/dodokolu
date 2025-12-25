// 反馈页面成功动画

// 显示成功动画
function showSuccessAnimation() {
    const overlay = document.createElement('div');
    overlay.className = 'feedback-success-overlay';
    overlay.innerHTML = `
        <div class="feedback-success-icon">✓</div>
        <div class="feedback-success-text">感谢反馈</div>
    `;
    document.body.appendChild(overlay);
}

