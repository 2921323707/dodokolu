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

