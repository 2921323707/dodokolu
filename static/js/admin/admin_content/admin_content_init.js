// 内容管理（相册管理）初始化
(function () {
    'use strict';

    window.contentManager = {
        currentCategory: null,
        categories: [],
        images: [],
        users: [],

        // 初始化
        init: function () {
            this.loadCategories();
            this.loadUsers();
            this.bindEvents();
        },

        // 绑定事件
        bindEvents: function () {
            // 类别配置保存
            const saveCategoryBtn = document.getElementById('saveCategoryBtn');
            if (saveCategoryBtn) {
                saveCategoryBtn.addEventListener('click', () => this.saveCategoryConfig());
            }

            // 类别可见性切换 - 同步桌面端和移动端checkbox
            const categoryVisibilityToggle = document.getElementById('categoryVisibility');
            const categoryVisibilityDesktop = document.getElementById('categoryVisibilityDesktop');
            const categoryVisibilityLabel = document.getElementById('categoryVisibilityLabel');
            const categoryVisibilityLabelMobile = document.getElementById('categoryVisibilityLabelMobile');

            // 同步函数
            const syncCheckboxes = (source, target) => {
                if (target && source) {
                    target.checked = source.checked;
                }
            };

            // 更新标签文本的函数
            const updateLabel = (checked) => {
                if (categoryVisibilityLabel) {
                    categoryVisibilityLabel.textContent = checked ? '显示' : '隐藏';
                }
                if (categoryVisibilityLabelMobile) {
                    categoryVisibilityLabelMobile.textContent = checked ? '显示' : '隐藏';
                }
            };

            // 移动端checkbox事件
            if (categoryVisibilityToggle) {
                categoryVisibilityToggle.addEventListener('change', function () {
                    syncCheckboxes(this, categoryVisibilityDesktop);
                    updateLabel(this.checked);
                });
            }

            // 桌面端checkbox事件
            if (categoryVisibilityDesktop) {
                categoryVisibilityDesktop.addEventListener('change', function () {
                    syncCheckboxes(this, categoryVisibilityToggle);
                    updateLabel(this.checked);
                });
            }

            // 模态框关闭
            const modalCloses = document.querySelectorAll('.modal-close');
            modalCloses.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const modal = e.target.closest('.modal');
                    if (modal) {
                        modal.classList.remove('active');
                    }
                });
            });

            // 点击模态框外部关闭
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        modal.classList.remove('active');
                    }
                });
            });
        }
    };
})();

