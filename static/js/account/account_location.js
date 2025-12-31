// 位置信息功能
document.addEventListener('DOMContentLoaded', function () {
    // 获取用户地理位置
    function getCurrentLocation() {
        return new Promise((resolve) => {
            // 先从sessionStorage获取已保存的位置
            const savedLocation = sessionStorage.getItem('userLocation');
            if (savedLocation) {
                try {
                    const location = JSON.parse(savedLocation);
                    resolve({ success: true, location: location });
                    return;
                } catch (e) {
                    console.error('解析保存的位置信息失败:', e);
                }
            }

            // 检查浏览器是否支持地理位置API
            if (!navigator.geolocation) {
                console.warn('浏览器不支持地理位置API');
                resolve({ success: false, error: 'not_supported', message: '您的浏览器不支持地理位置功能' });
                return;
            }

            // 请求用户位置
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const location = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: Date.now()
                    };
                    // 保存到sessionStorage
                    sessionStorage.setItem('userLocation', JSON.stringify(location));
                    resolve({ success: true, location: location });
                },
                (error) => {
                    console.warn('获取地理位置失败:', error.message);
                    let errorType = 'unknown';
                    let errorMessage = '无法获取位置信息';

                    switch (error.code) {
                        case 1: // PERMISSION_DENIED
                            errorType = 'permission_denied';
                            errorMessage = '位置权限被拒绝';
                            break;
                        case 2: // POSITION_UNAVAILABLE
                            errorType = 'unavailable';
                            errorMessage = '位置信息不可用';
                            break;
                        case 3: // TIMEOUT
                            errorType = 'timeout';
                            errorMessage = '获取位置超时';
                            break;
                    }

                    resolve({ success: false, error: errorType, message: errorMessage });
                },
                {
                    enableHighAccuracy: false,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        });
    }

    // 加载位置信息
    async function loadLocationInfo() {
        try {
            const result = await getCurrentLocation();
            if (result.success && result.location && result.location.latitude && result.location.longitude) {
                // 调用后端API获取格式化地址
                const response = await fetch('/api/account/location', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        latitude: result.location.latitude,
                        longitude: result.location.longitude
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.data) {
                        return { success: true, data: data.data };
                    }
                }
                return { success: false, error: 'api_error', message: '获取地址信息失败' };
            } else {
                // 返回错误信息
                return {
                    success: false,
                    error: result.error || 'unknown',
                    message: result.message || '无法获取位置信息'
                };
            }
        } catch (error) {
            console.error('获取位置信息失败:', error);
            return { success: false, error: 'exception', message: '获取位置信息时发生错误' };
        }
    }

    // 渲染位置信息
    function renderLocationInfo(locationData) {
        const locationCard = document.getElementById('locationCard');
        const locationInfo = document.getElementById('locationInfo');

        if (!locationCard || !locationInfo) return;

        // 始终显示位置信息卡片
        locationCard.style.display = 'block';

        if (locationData && locationData.success && locationData.data && locationData.data.location) {
            // 成功获取位置信息
            locationInfo.innerHTML = `
                <div class="info-item">
                    <p class="info-value">${escapeHtml(locationData.data.location)}</p>
                    <p class="info-label">位置</p>
                </div>
            `;
        } else {
            // 显示权限提示
            const errorType = locationData?.error || 'unknown';
            const isPermissionDenied = errorType === 'permission_denied';

            let permissionGuide = '';
            if (isPermissionDenied) {
                permissionGuide = `
                    <div class="permission-guide">
                        <p class="guide-title">📍 如何开启位置权限：</p>
                        <div class="guide-steps">
                            <p><strong>Chrome/Edge 浏览器：</strong></p>
                            <ol>
                                <li>点击地址栏左侧的锁图标 🔒</li>
                                <li>找到"位置"选项，改为"允许"</li>
                                <li>刷新页面后再次点击"刷新"按钮</li>
                            </ol>
                            <p><strong>Firefox 浏览器：</strong></p>
                            <ol>
                                <li>点击地址栏左侧的图标</li>
                                <li>找到"权限" → "访问您的位置"</li>
                                <li>选择"允许"，刷新页面</li>
                            </ol>
                            <p><strong>Safari 浏览器：</strong></p>
                            <ol>
                                <li>Safari → 偏好设置 → 网站</li>
                                <li>选择"位置服务"</li>
                                <li>找到本网站，设置为"允许"</li>
                            </ol>
                        </div>
                    </div>
                `;
            }

            locationInfo.innerHTML = `
                <div class="info-item permission-prompt">
                    <p class="info-value">
                        <span class="placeholder">${escapeHtml(locationData?.message || '位置信息不可用')}</span>
                    </p>
                    <p class="info-label">位置</p>
                    ${permissionGuide}
                </div>
            `;
        }
    }

    // 刷新位置信息
    async function refreshLocationInfo() {
        const refreshBtn = document.getElementById('refreshLocationBtn');
        const locationInfo = document.getElementById('locationInfo');
        const locationCard = document.getElementById('locationCard');

        // 禁用按钮，显示加载状态
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.textContent = '获取中...';
        }

        // 显示加载提示
        if (locationInfo) {
            locationInfo.innerHTML = '<div class="loading-message">正在获取位置信息...</div>';
            locationCard.style.display = 'block';
        }

        try {
            // 清除之前保存的位置信息，强制重新获取
            sessionStorage.removeItem('userLocation');

            // 重新获取位置信息
            const locationData = await loadLocationInfo();
            renderLocationInfo(locationData);
        } catch (error) {
            console.error('刷新位置信息失败:', error);
            if (locationInfo) {
                locationInfo.innerHTML = '<div class="error-message">获取位置信息失败，请检查浏览器是否允许地理位置权限</div>';
            }
        } finally {
            // 恢复按钮状态
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.textContent = '刷新';
            }
        }
    }

    // 绑定刷新位置按钮事件
    const refreshLocationBtn = document.getElementById('refreshLocationBtn');
    if (refreshLocationBtn) {
        refreshLocationBtn.addEventListener('click', refreshLocationInfo);
    }

    // 暴露给账户信息模块使用
    window.loadLocationInfo = loadLocationInfo;
    window.renderLocationInfo = renderLocationInfo;
});

