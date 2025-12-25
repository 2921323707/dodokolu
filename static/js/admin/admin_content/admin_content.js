// 内容管理（相册管理）
document.addEventListener('DOMContentLoaded', function () {
    const contentManager = {
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
            const categoryVisibilityLabel = document.querySelector('.desktop-checkbox .visibility-label');
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
                categoryVisibilityToggle.addEventListener('change', function() {
                    syncCheckboxes(this, categoryVisibilityDesktop);
                    updateLabel(this.checked);
                });
            }
            
            // 桌面端checkbox事件
            if (categoryVisibilityDesktop) {
                categoryVisibilityDesktop.addEventListener('change', function() {
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
        },

        // 加载类别列表
        loadCategories: async function () {
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
        },

        // 渲染类别标签
        renderCategoryTabs: function () {
            const container = document.getElementById('categoryTabs');
            if (!container) return;

            container.innerHTML = this.categories.map(cat => `
                <button class="category-tab ${cat.category_key === this.currentCategory ? 'active' : ''}"
                        onclick="contentManager.selectCategory('${this.escapeHtml(cat.category_key)}')">
                    ${this.escapeHtml(cat.display_name)}
                </button>
            `).join('');
        },

        // 选择类别
        selectCategory: async function (categoryKey) {
            this.currentCategory = categoryKey;
            this.renderCategoryTabs();
            await this.loadCategoryConfig();
            await this.loadCategoryImages();
        },

        // 加载类别配置
        loadCategoryConfig: function () {
            const category = this.categories.find(c => c.category_key === this.currentCategory);
            if (!category) return;

            const displayNameInput = document.getElementById('categoryDisplayName');
            const visibilityToggle = document.getElementById('categoryVisibility');
            const visibilityDesktop = document.getElementById('categoryVisibilityDesktop');

            if (displayNameInput) {
                displayNameInput.value = category.display_name;
            }
            const isVisible = category.is_visible;
            if (visibilityToggle) {
                visibilityToggle.checked = isVisible;
            }
            if (visibilityDesktop) {
                visibilityDesktop.checked = isVisible;
            }
            
            // 更新标签
            const categoryVisibilityLabel = document.querySelector('.desktop-checkbox .visibility-label');
            const categoryVisibilityLabelMobile = document.getElementById('categoryVisibilityLabelMobile');
            if (categoryVisibilityLabel) {
                categoryVisibilityLabel.textContent = isVisible ? '显示' : '隐藏';
            }
            if (categoryVisibilityLabelMobile) {
                categoryVisibilityLabelMobile.textContent = isVisible ? '显示' : '隐藏';
            }
        },

        // 保存类别配置
        saveCategoryConfig: async function () {
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
        },

        // 加载类别图片
        loadCategoryImages: async function () {
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
        },

        // 渲染图片列表
        renderImages: function () {
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
        },

        // 编辑图片
        editImage: function (index) {
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
        },

        // 保存图片配置
        saveImageConfig: async function () {
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
        },

        // 重命名图片
        renameImage: async function () {
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
        },

        // 管理权限
        managePermissions: async function (imagePath) {
            if (!this.currentCategory) return;

            const modal = document.getElementById('permissionModal');
            const formContainer = document.getElementById('permissionForm');
            const listContainer = document.getElementById('permissionList');

            // 加载现有权限
            try {
                const response = await fetch(`/admin/api/content/permissions?category_key=${this.currentCategory}&image_path=${encodeURIComponent(imagePath)}`);
                const data = await response.json();

                if (data.success) {
                    // 渲染权限列表
                    if (listContainer) {
                        if (data.permissions.length === 0) {
                            listContainer.innerHTML = '<div class="empty-state"><p>暂无权限设置</p></div>';
                        } else {
                            listContainer.innerHTML = `
                                <div class="permission-list">
                                    ${data.permissions.map(perm => `
                                        <div class="permission-item">
                                            <span>${this.escapeHtml(perm.username)}</span>
                                            <button class="btn btn-sm btn-danger" onclick="contentManager.deletePermission(${perm.id})">删除</button>
                                        </div>
                                    `).join('')}
                                </div>
                            `;
                        }
                    }

                    // 设置表单
                    if (formContainer) {
                        formContainer.innerHTML = `
                            <input type="hidden" id="permissionImagePath" value="${this.escapeHtml(imagePath)}">
                            <div class="form-group">
                                <label>选择用户</label>
                                <select id="permissionUserId">
                                    <option value="">请选择用户</option>
                                    ${this.users.map(user => `
                                        <option value="${user.id}">${this.escapeHtml(user.username)} (${this.escapeHtml(user.email)})</option>
                                    `).join('')}
                                </select>
                            </div>
                            <div class="form-actions">
                                <button class="btn btn-primary" onclick="contentManager.addPermission()">添加权限</button>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('加载权限失败:', error);
            }

            if (modal) {
                modal.classList.add('active');
            }
        },

        // 添加权限
        addPermission: async function () {
            if (!this.currentCategory) return;

            const userIdSelect = document.getElementById('permissionUserId');
            const imagePathInput = document.getElementById('permissionImagePath');

            if (!userIdSelect || !imagePathInput) return;

            const userId = userIdSelect.value;
            const imagePath = imagePathInput.value;

            if (!userId) {
                this.showMessage('请选择用户', 'error');
                return;
            }

            try {
                const response = await fetch('/admin/api/content/permissions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: parseInt(userId),
                        category_key: this.currentCategory,
                        image_path: imagePath || null
                    })
                });

                const data = await response.json();

                if (data.success) {
                    this.showMessage('添加成功', 'success');
                    await this.managePermissions(imagePath);
                } else {
                    this.showMessage('添加失败: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('添加权限失败:', error);
                this.showMessage('添加权限失败，请重试', 'error');
            }
        },

        // 删除权限
        deletePermission: async function (permissionId) {
            if (!confirm('确定要删除这个权限吗？')) {
                return;
            }

            try {
                const response = await fetch(`/admin/api/content/permissions/${permissionId}`, {
                    method: 'DELETE'
                });

                const data = await response.json();

                if (data.success) {
                    this.showMessage('删除成功', 'success');
                    const imagePathInput = document.getElementById('permissionImagePath');
                    if (imagePathInput) {
                        await this.managePermissions(imagePathInput.value);
                    }
                } else {
                    this.showMessage('删除失败: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('删除权限失败:', error);
                this.showMessage('删除权限失败，请重试', 'error');
            }
        },

        // 加载用户列表
        loadUsers: async function () {
            try {
                const response = await fetch('/admin/api/content/users');
                const data = await response.json();

                if (data.success) {
                    this.users = data.users;
                }
            } catch (error) {
                console.error('加载用户列表失败:', error);
            }
        },

        // 关闭模态框
        closeModal: function (modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('active');
            }
        },

        // 显示消息
        showMessage: function (message, type) {
            const messageEl = document.getElementById('contentMessage');
            if (messageEl) {
                messageEl.textContent = message;
                messageEl.className = `message ${type} active`;
                setTimeout(() => this.hideMessage(), 5000);
            }
        },

        // 隐藏消息
        hideMessage: function () {
            const messageEl = document.getElementById('contentMessage');
            if (messageEl) {
                messageEl.classList.remove('active');
            }
        },

        // HTML转义
        escapeHtml: function (text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    // 初始化
    contentManager.init();
    window.contentManager = contentManager;
});
