// 数据库管理
document.addEventListener('DOMContentLoaded', function () {
    const dbManager = {
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
        },

        // 加载表列表
        loadTables: async function () {
            try {
                const response = await fetch('/admin/api/database/tables');
                const data = await response.json();

                if (data.success) {
                    const tableSelect = document.getElementById('tableSelect');
                    if (tableSelect) {
                        tableSelect.innerHTML = '<option value="">选择表...</option>' +
                            data.tables.map(table => `<option value="${this.escapeHtml(table)}">${this.escapeHtml(table)}</option>`).join('');
                    }
                } else {
                    this.showMessage('加载表列表失败: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('加载表列表失败:', error);
                this.showMessage('加载表列表失败，请刷新页面重试', 'error');
            }
        },

        // 选择表
        selectTable: async function (tableName) {
            if (!tableName) {
                this.currentTable = null;
                this.renderTable([]);
                return;
            }

            this.currentTable = tableName;
            this.currentPage = 1;
            await this.loadTableSchema();
            await this.loadTableData();
        },

        // 加载表结构
        loadTableSchema: async function () {
            if (!this.currentTable) return;

            try {
                const response = await fetch(`/admin/api/database/table/${this.currentTable}/schema`);
                const data = await response.json();

                if (data.success) {
                    this.columns = data.columns;
                } else {
                    this.showMessage('加载表结构失败: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('加载表结构失败:', error);
                this.showMessage('加载表结构失败', 'error');
            }
        },

        // 加载表数据
        loadTableData: async function () {
            if (!this.currentTable) return;

            const container = document.getElementById('tableContainer');
            if (container) {
                container.innerHTML = '<div class="loading">加载中...</div>';
            }

            try {
                const response = await fetch(
                    `/admin/api/database/table/${this.currentTable}/data?page=${this.currentPage}&per_page=${this.perPage}`
                );
                const data = await response.json();

                if (data.success) {
                    this.totalPages = data.total_pages;
                    this.renderTable(data.data, data.columns);
                    this.renderPagination(data.total, data.page, data.total_pages);
                } else {
                    if (container) {
                        container.innerHTML = `<div class="empty-state"><p>加载失败: ${data.message}</p></div>`;
                    }
                }
            } catch (error) {
                console.error('加载数据失败:', error);
                if (container) {
                    container.innerHTML = '<div class="empty-state"><p>加载失败，请刷新页面重试</p></div>';
                }
            }
        },

        // 渲染表格
        renderTable: function (rows, columnNames) {
            const container = document.getElementById('tableContainer');
            if (!container) return;

            if (!this.currentTable) {
                container.innerHTML = '<div class="empty-state"><p>请选择一个表</p></div>';
                return;
            }

            if (rows.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>暂无数据</p></div>';
                return;
            }

            const cols = columnNames || this.columns.map(c => c.name);
            const pkColumn = this.columns.find(c => c.pk)?.name || 'id';

            let html = '<div class="data-table-wrapper"><table class="data-table"><thead><tr>';
            cols.forEach(col => {
                html += `<th>${this.escapeHtml(col)}</th>`;
            });
            html += '<th>操作</th></tr></thead><tbody>';

            rows.forEach(row => {
                const rowId = row[pkColumn];
                html += `<tr data-id="${rowId}">`;
                cols.forEach(col => {
                    const value = row[col] !== null && row[col] !== undefined ? String(row[col]) : '';
                    html += `<td>${this.escapeHtml(value)}</td>`;
                });
                html += `<td class="table-actions">
                    <button class="btn btn-primary" onclick="dbManager.editRow(${rowId})">编辑</button>
                    <button class="btn btn-danger" onclick="dbManager.deleteRow(${rowId})">删除</button>
                </td></tr>`;
            });

            html += '</tbody></table></div>';
            container.innerHTML = html;
        },

        // 渲染分页
        renderPagination: function (total, page, totalPages) {
            const container = document.getElementById('paginationContainer');
            if (!container) return;

            container.innerHTML = `
                <div class="pagination">
                    <button onclick="dbManager.goToPage(1)" ${page === 1 ? 'disabled' : ''}>首页</button>
                    <button onclick="dbManager.goToPage(${page - 1})" ${page === 1 ? 'disabled' : ''}>上一页</button>
                    <span class="page-info">第 ${page} / ${totalPages} 页，共 ${total} 条</span>
                    <button onclick="dbManager.goToPage(${page + 1})" ${page === totalPages ? 'disabled' : ''}>下一页</button>
                    <button onclick="dbManager.goToPage(${totalPages})" ${page === totalPages ? 'disabled' : ''}>末页</button>
                </div>
            `;
        },

        // 跳转页面
        goToPage: function (page) {
            if (page < 1 || page > this.totalPages) return;
            this.currentPage = page;
            this.loadTableData();
        },

        // 显示添加模态框
        showAddModal: function () {
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
        },

        // 编辑行
        editRow: async function (rowId) {
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
        },

        // 显示编辑模态框
        showEditModal: function (row) {
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
        },

        // 保存行
        saveRow: async function () {
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
        },

        // 删除行
        deleteRow: async function (rowId) {
            if (!this.currentTable) return;

            if (!confirm('确定要删除这条记录吗？此操作不可撤销。')) {
                return;
            }

            try {
                const pkColumn = this.columns.find(c => c.pk)?.name || 'id';
                const response = await fetch(`/admin/api/database/table/${this.currentTable}/row`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ id: rowId })
                });

                const result = await response.json();

                if (result.success) {
                    this.showMessage('删除成功', 'success');
                    await this.loadTableData();
                } else {
                    this.showMessage('删除失败: ' + result.message, 'error');
                }
            } catch (error) {
                console.error('删除失败:', error);
                this.showMessage('删除失败，请重试', 'error');
            }
        },

        // 关闭模态框
        closeModal: function () {
            const modal = document.getElementById('rowModal');
            if (modal) {
                modal.classList.remove('active');
            }
            this.editingRow = null;
        },

        // 显示消息
        showMessage: function (message, type) {
            const messageEl = document.getElementById('dbMessage');
            if (messageEl) {
                messageEl.textContent = message;
                messageEl.className = `message ${type} active`;
                setTimeout(() => this.hideMessage(), 5000);
            }
        },

        // 隐藏消息
        hideMessage: function () {
            const messageEl = document.getElementById('dbMessage');
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
    dbManager.init();
    window.dbManager = dbManager;
});
