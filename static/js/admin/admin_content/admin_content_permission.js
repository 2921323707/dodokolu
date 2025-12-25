// 权限管理功能
(function(contentManager) {
    'use strict';

    // 管理权限
    contentManager.managePermissions = async function (imagePath) {
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
    };

    // 添加权限
    contentManager.addPermission = async function () {
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
    };

    // 删除权限
    contentManager.deletePermission = async function (permissionId) {
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
    };

    // 加载用户列表
    contentManager.loadUsers = async function () {
        try {
            const response = await fetch('/admin/api/content/users');
            const data = await response.json();

            if (data.success) {
                this.users = data.users;
            }
        } catch (error) {
            console.error('加载用户列表失败:', error);
        }
    };
})(window.contentManager || {});

