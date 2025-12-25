// 工具函数
(function(contentManager) {
    'use strict';

    // 关闭模态框
    contentManager.closeModal = function (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    };

    // 显示消息
    contentManager.showMessage = function (message, type) {
        const messageEl = document.getElementById('contentMessage');
        if (messageEl) {
            messageEl.textContent = message;
            messageEl.className = `message ${type} active`;
            setTimeout(() => this.hideMessage(), 5000);
        }
    };

    // 隐藏消息
    contentManager.hideMessage = function () {
        const messageEl = document.getElementById('contentMessage');
        if (messageEl) {
            messageEl.classList.remove('active');
        }
    };

    // HTML转义
    contentManager.escapeHtml = function (text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };
})(window.contentManager || {});

