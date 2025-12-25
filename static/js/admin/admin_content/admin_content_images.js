// 图片管理功能
(function(contentManager) {
    'use strict';

    // 加载类别图片
    contentManager.loadCategoryImages = async function () {
        if (!this.currentCategory) return;

        const container = document.getElementById('imagesContainer');
        if (container) {
            container.innerHTML = '<div class="loading">加载中...</div>';
        }

        try {
            const response = await fetch(`/admin/api/content/images/${this.currentCategory}`);
            const data = await response.json();

            if (data.success) {
                this.images = data.images;
                this.renderImages();
            } else {
                if (container) {
                    container.innerHTML = `<div class="empty-state"><p>加载失败: ${data.message}</p></div>`;
                }
            }
        } catch (error) {
            console.error('加载图片失败:', error);
            if (container) {
                container.innerHTML = '<div class="empty-state"><p>加载失败，请刷新页面重试</p></div>';
            }
        }
    };

    // 渲染图片列表
    contentManager.renderImages = function () {
        const container = document.getElementById('imagesContainer');
        if (!container) return;

        if (this.images.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>暂无图片</p></div>';
            return;
        }

        container.innerHTML = `
            <div class="images-grid">
                ${this.images.map((img, index) => `
                    <div class="image-item ${!img.is_visible ? 'hidden' : ''}" data-index="${index}">
                        <img src="${this.escapeHtml(img.url)}" alt="${this.escapeHtml(img.name)}" class="image-preview">
                        <div class="image-info">
                            <div class="image-name">${this.escapeHtml(img.display_name || img.name)}</div>
                            <div class="image-actions">
                                <button class="btn btn-sm btn-primary" onclick="contentManager.editImage(${index})">编辑</button>
                                <button class="btn btn-sm btn-secondary" onclick="contentManager.managePermissions('${this.escapeHtml(img.path)}')">权限</button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    };

    // 编辑图片
    contentManager.editImage = function (index) {
        const img = this.images[index];
        if (!img) return;

        const modal = document.getElementById('imageEditModal');
        const formContainer = document.getElementById('imageEditForm');

        if (formContainer) {
            formContainer.innerHTML = `
                <div class="form-group">
                    <label>显示名称</label>
                    <input type="text" id="imageDisplayName" value="${this.escapeHtml(img.display_name || img.name)}" placeholder="留空使用原文件名">
                </div>
                <div class="form-group">
                    <label>可见性</label>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <label class="toggle-switch">
                            <input type="checkbox" id="imageVisibility" ${img.is_visible ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                        <span id="visibilityLabel" style="color: var(--text-secondary, #64748b);">${img.is_visible ? '显示' : '隐藏'}</span>
                    </div>
                </div>
                <input type="hidden" id="imagePath" value="${this.escapeHtml(img.path)}">
            `;
        }

        if (modal) {
            modal.classList.add('active');
        }

        // 更新可见性文本（在模态框显示后绑定事件）
        setTimeout(() => {
            const visibilityToggle = document.getElementById('imageVisibility');
            const visibilityLabel = document.getElementById('visibilityLabel');
            if (visibilityToggle && visibilityLabel) {
                visibilityToggle.addEventListener('change', function() {
                    visibilityLabel.textContent = this.checked ? '显示' : '隐藏';
                });
            }
        }, 100);
    };

    // 保存图片配置
    contentManager.saveImageConfig = async function () {
        if (!this.currentCategory) return;

        const displayNameInput = document.getElementById('imageDisplayName');
        const visibilityToggle = document.getElementById('imageVisibility');
        const pathInput = document.getElementById('imagePath');

        if (!pathInput) return;

        const imagePath = pathInput.value;
        const displayName = displayNameInput?.value.trim() || null;
        const isVisible = visibilityToggle?.checked;

        try {
            const response = await fetch(`/admin/api/content/images/${this.currentCategory}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image_path: imagePath,
                    display_name: displayName,
                    is_visible: isVisible
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('保存成功', 'success');
                this.closeModal('imageEditModal');
                await this.loadCategoryImages();
            } else {
                this.showMessage('保存失败: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('保存失败:', error);
            this.showMessage('保存失败，请重试', 'error');
        }
    };

    // 重命名图片
    contentManager.renameImage = async function () {
        if (!this.currentCategory) return;

        const oldPathInput = document.getElementById('renameOldPath');
        const newNameInput = document.getElementById('renameNewName');

        if (!oldPathInput || !newNameInput) return;

        const oldPath = oldPathInput.value;
        const newName = newNameInput.value.trim();

        if (!newName) {
            this.showMessage('新文件名不能为空', 'error');
            return;
        }

        try {
            const response = await fetch(`/admin/api/content/images/${this.currentCategory}/rename`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    old_path: oldPath,
                    new_name: newName
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('重命名成功', 'success');
                this.closeModal('imageRenameModal');
                await this.loadCategoryImages();
            } else {
                this.showMessage('重命名失败: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('重命名失败:', error);
            this.showMessage('重命名失败，请重试', 'error');
        }
    };
})(window.contentManager || {});

