// 每日学习APP打卡状态显示 - 圆形进度环

// 打卡状态相关变量
let checkStatus = {
    total: 0,
    completed: 0,
    allCompleted: false
};

// 初始化打卡状态检查
function initCheckStatus() {
    loadCheckStatus();
    // 每30秒刷新一次打卡状态
    setInterval(loadCheckStatus, 30000);
}

// 加载打卡状态
async function loadCheckStatus() {
    const placeholderContent = document.querySelector('.todo-section .placeholder-content');
    if (!placeholderContent) return;

    try {
        const response = await fetch('/check/list');
        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                renderCircularProgress(placeholderContent, 0, false);
                return;
            }
            throw new Error(data.error || '加载失败');
        }

        if (data.success) {
            const items = data.data || [];
            updateCheckStatus(items);
            const progress = checkStatus.total > 0 ? Math.round((checkStatus.completed / checkStatus.total) * 100) : 0;
            renderCircularProgress(placeholderContent, progress, checkStatus.allCompleted);
        } else {
            throw new Error(data.error || '加载失败');
        }
    } catch (error) {
        console.error('加载打卡状态失败:', error);
        renderCircularProgress(placeholderContent, 0, false);
    }
}

// 更新打卡状态数据
function updateCheckStatus(items) {
    checkStatus.total = items.length;
    checkStatus.completed = items.filter(item => item.status === 'completed').length;
    checkStatus.allCompleted = checkStatus.total > 0 && checkStatus.completed === checkStatus.total;
}

// 渲染圆形进度环
function renderCircularProgress(container, progress, allCompleted) {
    // 计算圆形进度环的 stroke-dasharray 和 stroke-dashoffset
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (progress / 100) * circumference;
    
    // 根据完成状态选择颜色（不使用绿色）
    const strokeColor = allCompleted ? '#ff9800' : '#2196f3';
    
    container.innerHTML = `
        <div class="circular-progress-container">
            <svg class="circular-progress" viewBox="0 0 140 140">
                <circle
                    class="circular-progress-bg"
                    cx="70"
                    cy="70"
                    r="${radius}"
                    fill="none"
                    stroke="#e0e0e0"
                    stroke-width="8"
                />
                <circle
                    class="circular-progress-fill"
                    cx="70"
                    cy="70"
                    r="${radius}"
                    fill="none"
                    stroke="${strokeColor}"
                    stroke-width="8"
                    stroke-linecap="round"
                    stroke-dasharray="${circumference}"
                    stroke-dashoffset="${offset}"
                    transform="rotate(-90 70 70)"
                />
            </svg>
            <div class="circular-progress-text">
                <span class="circular-progress-percent">${progress}%</span>
            </div>
        </div>
    `;
}

