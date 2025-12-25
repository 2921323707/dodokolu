// 反馈页面步骤切换逻辑

// 切换到第一步
function switchToStep1() {
    if (elements.step1 && elements.step2) {
        elements.step1.classList.add('active');
        elements.step2.classList.remove('active');
    }
    hideMessage();
}

// 切换到第二步
function switchToStep2() {
    if (elements.step1 && elements.step2) {
        elements.step1.classList.remove('active');
        elements.step2.classList.add('active');
    }
    hideMessage();
    
    // 聚焦到联系方式输入框
    setTimeout(() => {
        const contactInput = document.getElementById('feedbackContact');
        if (contactInput) {
            contactInput.focus();
        }
    }, 100);
}

