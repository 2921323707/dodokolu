// 工具函数
(function(dbManager) {
    'use strict';

    // 关闭模态框
    dbManager.closeModal = function () {
        const modal = document.getElementById('rowModal');
        if (modal) {
            modal.classList.remove('active');
        }
        this.editingRow = null;
    };

    // 显示消息
    dbManager.showMessage = function (message, type) {
        const messageEl = document.getElementById('dbMessage');
        if (messageEl) {
            messageEl.textContent = message;
            messageEl.className = `message ${type} active`;
            setTimeout(() => this.hideMessage(), 5000);
        }
    };

    // 隐藏消息
    dbManager.hideMessage = function () {
        const messageEl = document.getElementById('dbMessage');
        if (messageEl) {
            messageEl.classList.remove('active');
        }
    };

    // HTML转义
    dbManager.escapeHtml = function (text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };
})(window.dbManager || {});

