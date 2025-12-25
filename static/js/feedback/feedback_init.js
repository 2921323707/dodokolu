// 反馈页面主初始化文件

document.addEventListener('DOMContentLoaded', function() {
    // 初始化元素引用
    initElements();

    // 第一步：提交反馈内容
    if (elements.feedbackContentForm) {
        elements.feedbackContentForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const contentInput = document.getElementById('feedbackContent');
            if (!contentInput) return;

            feedbackContent = contentInput.value.trim();

            // 验证反馈内容
            if (!feedbackContent) {
                showMessage('请填写反馈内容', 'error');
                return;
            }

            // 切换到第二步
            switchToStep2();
        });
    }

    // 返回第一步
    if (elements.backBtn) {
        elements.backBtn.addEventListener('click', function() {
            switchToStep1();
        });
    }

    // 第二步：提交完整反馈
    if (elements.feedbackContactForm) {
        elements.feedbackContactForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const contactInput = document.getElementById('feedbackContact');
            const feedbackContact = contactInput ? contactInput.value.trim() : '';

            // 禁用提交按钮并显示加载状态
            setSubmitButtonState(true);
            hideMessage();

            const result = await submitFeedback(feedbackContent, feedbackContact);

            // 如果失败且不需要登录，恢复提交按钮
            if (!result.success && !result.requireLogin) {
                setSubmitButtonState(false);
            }
        });
    }
});

