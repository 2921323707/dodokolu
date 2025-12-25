// 初始化代码

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    // 初始化输入框
    initInput();

    // 初始化模式按钮状态
    const modeText = document.getElementById('modeText');
    const modeToggleBtn = document.getElementById('modeToggleBtn');
    if (modeText) {
        modeText.textContent = currentMode;
    }
    if (modeToggleBtn && currentMode === 'normal') {
        modeToggleBtn.classList.add('active');
    }

    // 初始化地理位置（静默获取，不阻塞页面加载）
    initLocation();

    // 加载历史记录
    loadHistory();
});

