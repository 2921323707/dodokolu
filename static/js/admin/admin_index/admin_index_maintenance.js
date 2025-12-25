// 维护配置组件
document.addEventListener('DOMContentLoaded', function () {
    const maintenanceConfig = {
        pages: [],
        loading: false,

        // 初始化
        init: function () {
            this.loadConfig();
            this.bindEvents();
        },

        // 加载配置
        loadConfig: async function () {
            try {
                const response = await fetch('/admin/api/maintenance/config');
                const data = await response.json();
                
                if (data.success) {
                    this.pages = data.pages || [];
                    this.renderPages();
                } else {
                    this.showMessage('加载配置失败: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('加载配置失败:', error);
                this.showMessage('加载配置失败，请刷新页面重试', 'error');
            }
        },

        // 渲染页面列表
        renderPages: function () {
            const listContainer = document.getElementById('maintenancePagesList');
            if (!listContainer) return;

            if (this.pages.length === 0) {
                listContainer.innerHTML = '<div class="empty-state">暂无维护页面</div>';
                return;
            }

            listContainer.innerHTML = this.pages.map((page, index) => `
                <div class="maintenance-page-item">
                    <span>${this.escapeHtml(page)}</span>
                    <button onclick="maintenanceConfig.removePage(${index})">删除</button>
                </div>
            `).join('');
        },

        // 添加页面
        addPage: function () {
            const input = document.getElementById('maintenancePageInput');
            if (!input) return;

            const page = input.value.trim();
            if (!page) {
                this.showMessage('请输入页面路径', 'error');
                return;
            }

            // 检查是否已存在
            if (this.pages.includes(page)) {
                this.showMessage('该页面已在维护列表中', 'error');
                return;
            }

            this.pages.push(page);
            input.value = '';
            this.renderPages();
            this.hideMessage();
        },

        // 删除页面
        removePage: function (index) {
            if (confirm('确定要移除该页面的维护状态吗？')) {
                this.pages.splice(index, 1);
                this.renderPages();
                this.hideMessage();
            }
        },

        // 保存配置
        saveConfig: async function () {
            if (this.loading) return;

            this.loading = true;
            const saveBtn = document.getElementById('maintenanceSaveBtn');
            if (saveBtn) {
                saveBtn.disabled = true;
                saveBtn.textContent = '保存中...';
            }

            try {
                const response = await fetch('/admin/api/maintenance/config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        pages: this.pages
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    this.showMessage('配置已保存！需要重启应用才能生效。', 'success');
                } else {
                    this.showMessage('保存失败: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('保存配置失败:', error);
                this.showMessage('保存失败，请重试', 'error');
            } finally {
                this.loading = false;
                if (saveBtn) {
                    saveBtn.disabled = false;
                    saveBtn.textContent = '保存配置';
                }
            }
        },

        // 绑定事件
        bindEvents: function () {
            // 添加按钮
            const addBtn = document.getElementById('maintenanceAddBtn');
            if (addBtn) {
                addBtn.addEventListener('click', () => this.addPage());
            }

            // 输入框回车
            const input = document.getElementById('maintenancePageInput');
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.addPage();
                    }
                });
            }

            // 保存按钮
            const saveBtn = document.getElementById('maintenanceSaveBtn');
            if (saveBtn) {
                saveBtn.addEventListener('click', () => this.saveConfig());
            }
        },

        // 显示消息
        showMessage: function (message, type) {
            const messageEl = document.getElementById('maintenanceMessage');
            if (messageEl) {
                messageEl.textContent = message;
                messageEl.className = `maintenance-message ${type}`;
            }
        },

        // 隐藏消息
        hideMessage: function () {
            const messageEl = document.getElementById('maintenanceMessage');
            if (messageEl) {
                messageEl.className = 'maintenance-message';
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
    if (document.getElementById('maintenanceConfig')) {
        maintenanceConfig.init();
        window.maintenanceConfig = maintenanceConfig;
    }
});
