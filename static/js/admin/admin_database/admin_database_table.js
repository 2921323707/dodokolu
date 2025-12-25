// 表格管理功能
(function (dbManager) {
    'use strict';

    // 加载表列表
    dbManager.loadTables = async function () {
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
    };

    // 选择表
    dbManager.selectTable = async function (tableName) {
        if (!tableName) {
            this.currentTable = null;
            this.renderTable([]);
            return;
        }

        this.currentTable = tableName;
        this.currentPage = 1;
        await this.loadTableSchema();
        await this.loadTableData();
    };

    // 加载表结构
    dbManager.loadTableSchema = async function () {
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
    };

    // 加载表数据
    dbManager.loadTableData = async function () {
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
    };

    // 渲染表格
    dbManager.renderTable = function (rows, columnNames) {
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
    };

    // 渲染分页
    dbManager.renderPagination = function (total, page, totalPages) {
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
    };

    // 跳转页面
    dbManager.goToPage = function (page) {
        if (page < 1 || page > this.totalPages) return;
        this.currentPage = page;
        this.loadTableData();
    };

    // 删除行
    dbManager.deleteRow = async function (rowId) {
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
    };
})(window.dbManager || {});

