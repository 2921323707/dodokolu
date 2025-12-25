// 类别管理功能
(function (contentManager) {
    'use strict';

    // 加载类别列表
    contentManager.loadCategories = async function () {
        try {
            const response = await fetch('/admin/api/content/categories');
            const data = await response.json();

            if (data.success) {
                this.categories = data.categories;
                this.renderCategoryTabs();

                // 默认选择第一个类别
                if (this.categories.length > 0 && !this.currentCategory) {
                    this.selectCategory(this.categories[0].category_key);
                }
            } else {
                this.showMessage('加载类别失败: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('加载类别失败:', error);
            this.showMessage('加载类别失败，请刷新页面重试', 'error');
        }
    };

    // 渲染类别标签
    contentManager.renderCategoryTabs = function () {
        const container = document.getElementById('categoryTabs');
        if (!container) return;

        container.innerHTML = this.categories.map(cat => `
            <button class="category-tab ${cat.category_key === this.currentCategory ? 'active' : ''}"
                    onclick="contentManager.selectCategory('${this.escapeHtml(cat.category_key)}')">
                ${this.escapeHtml(cat.display_name)}
            </button>
        `).join('');
    };

    // 选择类别
    contentManager.selectCategory = async function (categoryKey) {
        this.currentCategory = categoryKey;
        this.renderCategoryTabs();
        await this.loadCategoryConfig();
        await this.loadCategoryImages();
    };

    // 加载类别配置
    contentManager.loadCategoryConfig = function () {
        const category = this.categories.find(c => c.category_key === this.currentCategory);
        if (!category) return;

        const displayNameInput = document.getElementById('categoryDisplayName');
        const visibilityToggle = document.getElementById('categoryVisibility');
        const visibilityDesktop = document.getElementById('categoryVisibilityDesktop');

        if (displayNameInput) {
            displayNameInput.value = category.display_name || '';
        }
        const isVisible = category.is_visible !== undefined ? category.is_visible : true;
        if (visibilityToggle) {
            visibilityToggle.checked = isVisible;
        }
        if (visibilityDesktop) {
            visibilityDesktop.checked = isVisible;
        }

        // 更新标签 - 使用ID选择器更可靠
        const categoryVisibilityLabel = document.getElementById('categoryVisibilityLabel');
        const categoryVisibilityLabelMobile = document.getElementById('categoryVisibilityLabelMobile');
        if (categoryVisibilityLabel) {
            categoryVisibilityLabel.textContent = isVisible ? '显示' : '隐藏';
        }
        if (categoryVisibilityLabelMobile) {
            categoryVisibilityLabelMobile.textContent = isVisible ? '显示' : '隐藏';
        }
    };

    // 保存类别配置
    contentManager.saveCategoryConfig = async function () {
        if (!this.currentCategory) return;

        const displayNameInput = document.getElementById('categoryDisplayName');
        // 优先读取桌面端checkbox（桌面端显示），如果没有则读取移动端checkbox
        const visibilityDesktop = document.getElementById('categoryVisibilityDesktop');
        const visibilityToggle = document.getElementById('categoryVisibility');
        const visibilityCheckbox = visibilityDesktop || visibilityToggle;

        const displayName = displayNameInput?.value.trim();
        const isVisible = visibilityCheckbox?.checked;

        if (!displayName) {
            this.showMessage('显示名称不能为空', 'error');
            return;
        }

        try {
            const response = await fetch(`/admin/api/content/categories/${this.currentCategory}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    display_name: displayName,
                    is_visible: isVisible
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('保存成功', 'success');
                await this.loadCategories();
                await this.loadCategoryConfig();
            } else {
                this.showMessage('保存失败: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('保存失败:', error);
            this.showMessage('保存失败，请重试', 'error');
        }
    };
})(window.contentManager || {});

