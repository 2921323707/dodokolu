document.addEventListener('DOMContentLoaded', function () {
    // 转义HTML函数
    function escapeHtml(raw) {
        return String(raw)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // 获取设备信息（仅保留：操作系统、浏览器、CPU核心数、内存）
    function getDeviceInfo() {
        const deviceInfo = {};
        const userAgent = navigator.userAgent;

        // 操作系统
        let os = '未知';
        if (userAgent.indexOf('Win') !== -1) os = 'Windows';
        else if (userAgent.indexOf('Mac') !== -1) os = 'macOS';
        else if (userAgent.indexOf('Linux') !== -1) os = 'Linux';
        else if (userAgent.indexOf('Android') !== -1) os = 'Android';
        else if (userAgent.indexOf('iOS') !== -1 || userAgent.indexOf('iPhone') !== -1 || userAgent.indexOf('iPad') !== -1) os = 'iOS';
        deviceInfo.os = os;

        // 浏览器信息
        let browser = '未知';
        if (userAgent.indexOf('Chrome') !== -1 && userAgent.indexOf('Edg') === -1 && userAgent.indexOf('OPR') === -1) {
            browser = 'Chrome';
        } else if (userAgent.indexOf('Edg') !== -1) {
            browser = 'Edge';
        } else if (userAgent.indexOf('Firefox') !== -1) {
            browser = 'Firefox';
        } else if (userAgent.indexOf('Safari') !== -1 && userAgent.indexOf('Chrome') === -1) {
            browser = 'Safari';
        } else if (userAgent.indexOf('OPR') !== -1) {
            browser = 'Opera';
        }
        deviceInfo.browser = browser;

        // CPU核心数（如果可用）
        if (navigator.hardwareConcurrency) {
            deviceInfo.cpuCores = navigator.hardwareConcurrency;
        }

        // 内存信息（如果可用，Chrome 特有）
        if (navigator.deviceMemory) {
            deviceInfo.memory = `${navigator.deviceMemory} GB`;
        }

        return deviceInfo;
    }

    // 渲染设备信息
    function renderDeviceInfo() {
        const deviceInfo = getDeviceInfo();
        const deviceInfoEl = document.getElementById('deviceInfo');
        const deviceCard = document.getElementById('deviceCard');

        if (!deviceInfoEl || !deviceCard) return;

        const deviceLabelMap = {
            os: '操作系统',
            browser: '浏览器',
            cpuCores: 'CPU核心数',
            memory: '内存'
        };

        // 按顺序显示：操作系统、浏览器、CPU核心数、内存
        const orderedKeys = ['os', 'browser', 'cpuCores', 'memory'];

        deviceInfoEl.innerHTML = orderedKeys
            .filter(key => deviceInfo[key] !== undefined && deviceInfo[key] !== null)
            .map(key => {
                const value = deviceInfo[key];
                const valueHtml = (value === null || value === undefined || value === '')
                    ? '<span class="placeholder">未知</span>'
                    : escapeHtml(String(value));
                return `
                    <div class="info-item">
                        <p class="info-value">${valueHtml}</p>
                        <p class="info-label">${deviceLabelMap[key] || key}</p>
                    </div>
                `;
            })
            .join('');

        deviceCard.style.display = 'block';
    }

    // 刷新设备信息
    function refreshDeviceInfo() {
        const refreshBtn = document.getElementById('refreshDeviceBtn');
        const deviceInfo = document.getElementById('deviceInfo');
        const deviceCard = document.getElementById('deviceCard');

        // 禁用按钮，显示加载状态
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.textContent = '刷新中...';
        }

        // 显示加载提示
        if (deviceInfo) {
            deviceInfo.innerHTML = '<div class="loading-message">正在刷新设备信息...</div>';
            deviceCard.style.display = 'block';
        }

        // 模拟短暂延迟以显示加载状态
        setTimeout(() => {
            renderDeviceInfo();
            // 恢复按钮状态
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.textContent = '刷新';
            }
        }, 300);
    }

    // 初始加载设备信息
    renderDeviceInfo();

    // 绑定刷新设备信息按钮事件
    const refreshDeviceBtn = document.getElementById('refreshDeviceBtn');
    if (refreshDeviceBtn) {
        refreshDeviceBtn.addEventListener('click', refreshDeviceInfo);
    }
});

