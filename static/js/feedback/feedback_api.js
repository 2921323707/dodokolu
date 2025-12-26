// 反馈页面API调用逻辑

// 提交反馈到后端
async function submitFeedback(content, contact) {
    try {
        const imageFiles = getSelectedImageFiles();
        
        // 使用 FormData 来支持文件上传
        const formData = new FormData();
        formData.append('content', content);
        formData.append('contact', contact || '');
        
        // 添加所有图片文件
        if (imageFiles && imageFiles.length > 0) {
            imageFiles.forEach((file, index) => {
                formData.append('images', file);
            });
        }

        const response = await fetch('/api/feedback', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // 检查是否需要登录
        if (response.status === 401 && data.require_login) {
            window.location.href = '/login';
            return { success: false, requireLogin: true };
        }

        if (data.success) {
            showSuccessAnimation();
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
            return { success: true };
        } else {
            showMessage(data.message || '提交失败，请稍后重试', 'error');
            return { success: false, message: data.message };
        }
    } catch (error) {
        console.error('提交反馈失败:', error);
        showMessage('网络错误，请检查网络连接后重试', 'error');
        return { success: false, error: error.message };
    }
}

// 设置提交按钮状态
function setSubmitButtonState(disabled) {
    if (elements.submitBtn && elements.btnText && elements.btnLoading) {
        elements.submitBtn.disabled = disabled;
        if (disabled) {
            elements.btnText.style.display = 'none';
            elements.btnLoading.style.display = 'inline-block';
        } else {
            elements.btnText.style.display = 'inline-block';
            elements.btnLoading.style.display = 'none';
        }
    }
}

