// 数据库管理初始化
(function () {
    'use strict';

    window.dbManager = {
        currentTable: null,
        currentPage: 1,
        perPage: 20,
        columns: [],
        totalPages: 1,
        editingRow: null,

        // 初始化
        init: function () {
            this.loadTables();
            this.bindEvents();
        },

        // 绑定事件
        bindEvents: function () {
            const tableSelect = document.getElementById('tableSelect');
            if (tableSelect) {
                tableSelect.addEventListener('change', (e) => {
                    this.selectTable(e.target.value);
                });
            }

            const addBtn = document.getElementById('addRowBtn');
            if (addBtn) {
                addBtn.addEventListener('click', () => this.showAddModal());
            }

            const modalClose = document.getElementById('modalClose');
            if (modalClose) {
                modalClose.addEventListener('click', () => this.closeModal());
            }

            const saveBtn = document.getElementById('saveRowBtn');
            if (saveBtn) {
                saveBtn.addEventListener('click', () => this.saveRow());
            }

            // 点击模态框外部关闭
            const modal = document.getElementById('rowModal');
            if (modal) {
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        this.closeModal();
                    }
                });
            }
        }
    };
})();

