// 打卡功能 JavaScript

// DOM 元素
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const uploadPlaceholder = document.getElementById('uploadPlaceholder');
const uploadSuccess = document.getElementById('uploadSuccess');
const analyzeBtn = document.getElementById('analyzeBtn');

// 当前识别的结果
let currentResult = null;

// 清单相关变量
let currentEditingItemId = null;
let checkListItems = [];

// 初始化
document.addEventListener('DOMContentLoaded', function () {
    initUploadArea();
    loadCheckList();
});

// 初始化上传区域
function initUploadArea() {
    // 点击上传
    uploadArea.addEventListener('click', function (e) {
        if (e.target === uploadArea || e.target === uploadPlaceholder || uploadPlaceholder.contains(e.target)) {
            imageInput.click();
        }
    });

    // 文件选择
    imageInput.addEventListener('change', function (e) {
        handleFileSelect(e.target.files[0]);
    });

    // 拖拽上传
    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
}

// 处理文件选择
function handleFileSelect(file) {
    if (!file) return;

    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        alert('不支持的文件格式，请上传 JPG、PNG、GIF 或 WEBP 格式的图片');
        return;
    }

    // 验证文件大小（限制 10MB）
    if (file.size > 10 * 1024 * 1024) {
        alert('文件大小不能超过 10MB');
        return;
    }

    // 显示上传成功
    uploadPlaceholder.style.display = 'none';
    uploadSuccess.style.display = 'flex';
    analyzeBtn.disabled = false;
}

// 移除图片
function removeImage() {
    imageInput.value = '';
    uploadPlaceholder.style.display = 'block';
    uploadSuccess.style.display = 'none';
    analyzeBtn.disabled = true;
    currentResult = null;
    closeModal();
}

// 分析图片
async function analyzeImage() {
    if (!imageInput.files[0]) {
        alert('请先上传图片');
        return;
    }

    // 显示加载状态
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoading = analyzeBtn.querySelector('.btn-loading');
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    analyzeBtn.disabled = true;

    try {
        // 创建 FormData
        const formData = new FormData();
        formData.append('image', imageInput.files[0]);

        // 发送请求
        const response = await fetch('/check/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || '识别失败');
        }

        if (data.success) {
            currentResult = data.data;
            // 显示模态框
            showResultModal(data.data);
            // 自动推送
            await autoPush(data.data);
            // 刷新清单（识别成功后可能更新了状态）
            loadCheckList();
        } else {
            throw new Error(data.error || '识别失败');
        }

    } catch (error) {
        alert('识别失败: ' + error.message);
        console.error('识别错误:', error);
    } finally {
        // 恢复按钮状态
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        analyzeBtn.disabled = false;
    }
}

// 显示结果模态框
function showResultModal(result) {
    const modal = document.getElementById('resultModal');
    const modalBody = document.getElementById('modalBody');

    const appName = result.app_name || 'unknown';
    const status = result.check_in_status || 'unknown';
    const date = result.check_in_date || 'unknown';
    const details = result.details || '';
    const confidence = result.confidence || 'medium';

    // 状态图标和文本
    const statusConfig = {
        'success': { icon: '✓', text: '打卡成功', class: 'modal-status-success' },
        'failed': { icon: '✗', text: '打卡失败', class: 'modal-status-failed' },
        'unknown': { icon: '?', text: '无法确定', class: 'modal-status-unknown' }
    };

    const statusInfo = statusConfig[status] || statusConfig['unknown'];
    const confidenceText = {
        'high': '高',
        'medium': '中',
        'low': '低'
    }[confidence] || '未知';

    // 构建 HTML
    const html = `
        <div class="modal-result-item">
            <div class="modal-result-label">应用名称</div>
            <div class="modal-result-value">${appName}</div>
        </div>
        <div class="modal-result-item">
            <div class="modal-result-label">打卡状态</div>
            <div class="modal-result-value ${statusInfo.class}">
                <span>${statusInfo.icon}</span>
                ${statusInfo.text}
            </div>
        </div>
        <div class="modal-result-item">
            <div class="modal-result-label">打卡日期</div>
            <div class="modal-result-value">${date}</div>
        </div>
        <div class="modal-result-item">
            <div class="modal-result-label">识别置信度</div>
            <div class="modal-result-value">${confidenceText}</div>
        </div>
        ${details ? `
        <div class="modal-result-item">
            <div class="modal-result-label">详细说明</div>
            <div class="modal-result-value" style="font-size: 0.875rem; line-height: 1.6; color: var(--text-secondary);">${details}</div>
        </div>
        ` : ''}
        <div id="pushStatus" style="display: none;"></div>
    `;

    modalBody.innerHTML = html;
    modal.classList.add('show');

    // 阻止背景滚动
    document.body.style.overflow = 'hidden';
}

// 自动推送
async function autoPush(result) {
    const appName = result.app_name || '未知应用';
    const status = result.check_in_status || 'unknown';
    const date = result.check_in_date || '未知日期';
    const details = result.details || '';

    // 自动生成标题
    const statusText = {
        'success': '打卡成功',
        'failed': '打卡失败',
        'unknown': '打卡提醒'
    }[status] || '打卡提醒';

    const title = `${appName} - ${statusText}`;

    // 自动生成内容
    let content = `应用: ${appName}\n`;
    content += `状态: ${statusText}\n`;
    content += `日期: ${date}\n`;
    if (details) {
        content += `\n${details}`;
    }

    // 显示推送状态
    const pushStatus = document.getElementById('pushStatus');
    if (pushStatus) {
        pushStatus.style.display = 'block';
        pushStatus.className = 'modal-push-status';
        pushStatus.innerHTML = '正在推送...';
    }

    try {
        const response = await fetch('/check/push', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                content: content
            })
        });

        const data = await response.json();

        if (pushStatus) {
            if (data.success) {
                pushStatus.className = 'modal-push-status modal-push-success';
                pushStatus.innerHTML = '✓ 推送成功！';
            } else {
                pushStatus.className = 'modal-push-status modal-push-error';
                pushStatus.innerHTML = '✗ 推送失败: ' + (data.error_message || '未知错误');
            }
        }

    } catch (error) {
        if (pushStatus) {
            pushStatus.className = 'modal-push-status modal-push-error';
            pushStatus.innerHTML = '✗ 推送失败: ' + error.message;
        }
        console.error('推送错误:', error);
    }
}

// 关闭模态框
function closeModal() {
    const modal = document.getElementById('resultModal');
    modal.classList.remove('show');
    document.body.style.overflow = '';
}

// 点击背景关闭模态框
function closeModalOnBackdrop(event) {
    if (event.target.classList.contains('check-modal')) {
        closeModal();
    }
}

// ========== 清单管理功能 ==========

// 加载打卡清单
async function loadCheckList() {
    const listContent = document.getElementById('checkListContent');

    try {
        const response = await fetch('/check/list');
        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                listContent.innerHTML = '<div class="list-empty">请先登录</div>';
                return;
            }
            throw new Error(data.error || '加载失败');
        }

        if (data.success) {
            checkListItems = data.data || [];
            renderCheckList();
        } else {
            throw new Error(data.error || '加载失败');
        }
    } catch (error) {
        console.error('加载清单失败:', error);
        listContent.innerHTML = '<div class="list-error">加载失败: ' + error.message + '</div>';
    }
}

// 渲染打卡清单
function renderCheckList() {
    const listContent = document.getElementById('checkListContent');

    if (checkListItems.length === 0) {
        listContent.innerHTML = '<div class="list-empty">暂无打卡项，点击右上角 + 添加</div>';
        return;
    }

    const html = checkListItems.map(item => {
        const statusConfig = {
            'completed': { icon: '✓', text: '已完成', class: 'list-item-status-completed' },
            'failed': { icon: '✗', text: '失败', class: 'list-item-status-failed' },
            'pending': { icon: '○', text: '待完成', class: 'list-item-status-pending' }
        };

        const statusInfo = statusConfig[item.status] || statusConfig['pending'];

        return `
            <div class="list-item" data-id="${item.id}">
                <div class="list-item-content">
                    <div class="list-item-status ${statusInfo.class}">
                        <span class="status-icon">${statusInfo.icon}</span>
                    </div>
                    <div class="list-item-info">
                        <div class="list-item-name">${escapeHtml(item.app_name)}</div>
                        ${item.check_in_date && item.check_in_date !== 'unknown' ?
                `<div class="list-item-date">${escapeHtml(item.check_in_date)}</div>` : ''}
                    </div>
                </div>
                <div class="list-item-actions">
                    <button class="list-item-btn" onclick="editCheckItem(${item.id})" title="编辑">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                    </button>
                    <button class="list-item-btn list-item-btn-danger" onclick="deleteCheckItem(${item.id})" title="删除">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    listContent.innerHTML = html;
}

// 显示添加清单项模态框
function showAddItemModal() {
    currentEditingItemId = null;
    const modal = document.getElementById('itemModal');
    const modalTitle = document.getElementById('itemModalTitle');
    const appNameInput = document.getElementById('itemAppName');

    modalTitle.textContent = '添加打卡项';
    appNameInput.value = '';
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';

    // 聚焦输入框
    setTimeout(() => appNameInput.focus(), 100);
}

// 编辑清单项
function editCheckItem(itemId) {
    const item = checkListItems.find(i => i.id === itemId);
    if (!item) return;

    currentEditingItemId = itemId;
    const modal = document.getElementById('itemModal');
    const modalTitle = document.getElementById('itemModalTitle');
    const appNameInput = document.getElementById('itemAppName');

    modalTitle.textContent = '编辑打卡项';
    appNameInput.value = item.app_name;
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';

    // 聚焦输入框
    setTimeout(() => appNameInput.focus(), 100);
}

// 保存清单项
async function saveCheckItem() {
    const appNameInput = document.getElementById('itemAppName');
    const appName = appNameInput.value.trim();

    if (!appName) {
        alert('应用名称不能为空');
        return;
    }

    try {
        let response;
        if (currentEditingItemId) {
            // 更新
            response = await fetch(`/check/list/${currentEditingItemId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ app_name: appName })
            });
        } else {
            // 创建
            response = await fetch('/check/list', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ app_name: appName })
            });
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || '保存失败');
        }

        if (data.success) {
            closeItemModal();
            loadCheckList();
        } else {
            throw new Error(data.error || '保存失败');
        }
    } catch (error) {
        alert('保存失败: ' + error.message);
        console.error('保存错误:', error);
    }
}

// 删除清单项
async function deleteCheckItem(itemId) {
    if (!confirm('确定要删除这个打卡项吗？')) {
        return;
    }

    try {
        const response = await fetch(`/check/list/${itemId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || '删除失败');
        }

        if (data.success) {
            loadCheckList();
        } else {
            throw new Error(data.error || '删除失败');
        }
    } catch (error) {
        alert('删除失败: ' + error.message);
        console.error('删除错误:', error);
    }
}

// 关闭清单项模态框
function closeItemModal() {
    const modal = document.getElementById('itemModal');
    modal.classList.remove('show');
    document.body.style.overflow = '';
    currentEditingItemId = null;
}

// 点击背景关闭清单项模态框
function closeItemModalOnBackdrop(event) {
    if (event.target.classList.contains('check-modal')) {
        closeItemModal();
    }
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

