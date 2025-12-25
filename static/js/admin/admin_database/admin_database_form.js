// 表单和编辑功能
(function(dbManager) {
    'use strict';

    // 显示添加模态框
    dbManager.showAddModal = function () {
        if (!this.currentTable) {
            this.showMessage('请先选择一个表', 'error');
            return;
        }

        this.editingRow = null;
        const modal = document.getElementById('rowModal');
        const modalTitle = document.getElementById('modalTitle');
        const formContainer = document.getElementById('formContainer');

        if (modalTitle) {
            modalTitle.textContent = '添加新行';
        }

        // 生成表单
        if (formContainer) {
            const pkColumn = this.columns.find(c => c.pk);
            const editableColumns = this.columns.filter(c => !c.pk);

            formContainer.innerHTML = editableColumns.map(col => `
                <div class="form-group">
                    <label>${this.escapeHtml(col.name)} ${col.notnull ? '<span style="color: red;">*</span>' : ''}</label>
                    <input type="text" name="${this.escapeHtml(col.name)}" 
                           ${col.notnull ? 'required' : ''} 
                           placeholder="${col.type}">
                </div>
            `).join('');
        }

        if (modal) {
            modal.classList.add('active');
        }

        this.hideMessage();
    };

    // 编辑行
    dbManager.editRow = async function (rowId) {
        if (!this.currentTable) return;

        // 加载行数据
        try {
            const response = await fetch(
                `/admin/api/database/table/${this.currentTable}/data?page=1&per_page=1000`
            );
            const data = await response.json();

            if (data.success) {
                const pkColumn = this.columns.find(c => c.pk)?.name || 'id';
                const row = data.data.find(r => r[pkColumn] == rowId);

                if (row) {
                    this.showEditModal(row);
                } else {
                    this.showMessage('未找到该行数据', 'error');
                }
            }
        } catch (error) {
            console.error('加载行数据失败:', error);
            this.showMessage('加载行数据失败', 'error');
        }
    };

    // 显示编辑模态框
    dbManager.showEditModal = function (row) {
        this.editingRow = row;
        const modal = document.getElementById('rowModal');
        const modalTitle = document.getElementById('modalTitle');
        const formContainer = document.getElementById('formContainer');

        if (modalTitle) {
            modalTitle.textContent = '编辑行';
        }

        // 生成表单
        if (formContainer) {
            const pkColumn = this.columns.find(c => c.pk);
            const editableColumns = this.columns.filter(c => !c.pk);

            formContainer.innerHTML = editableColumns.map(col => {
                const value = row[col.name] !== null && row[col.name] !== undefined ? String(row[col.name]) : '';
                return `
                    <div class="form-group">
                        <label>${this.escapeHtml(col.name)} ${col.notnull ? '<span style="color: red;">*</span>' : ''}</label>
                        <input type="text" name="${this.escapeHtml(col.name)}" 
                               value="${this.escapeHtml(value)}"
                               ${col.notnull ? 'required' : ''} 
                               placeholder="${col.type}">
                    </div>
                `;
            }).join('');
        }

        if (modal) {
            modal.classList.add('active');
        }

        this.hideMessage();
    };

    // 保存行
    dbManager.saveRow = async function () {
        if (!this.currentTable) return;

        const formContainer = document.getElementById('formContainer');
        if (!formContainer) return;

        const inputs = formContainer.querySelectorAll('input, textarea');
        const data = {};

        inputs.forEach(input => {
            const value = input.value.trim();
            if (value || input.required) {
                data[input.name] = value || null;
            }
        });

        try {
            const pkColumn = this.columns.find(c => c.pk)?.name || 'id';
            const url = `/admin/api/database/table/${this.currentTable}/row`;
            const method = this.editingRow ? 'PUT' : 'POST';

            if (this.editingRow) {
                data.id = this.editingRow[pkColumn];
            }

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.showMessage(result.message || '保存成功', 'success');
                this.closeModal();
                await this.loadTableData();
            } else {
                this.showMessage('保存失败: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('保存失败:', error);
            this.showMessage('保存失败，请重试', 'error');
        }
    };
})(window.dbManager || {});

