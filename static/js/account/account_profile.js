// 账户信息和资料功能
document.addEventListener('DOMContentLoaded', function () {
    const statusEl = document.getElementById('accountStatus');
    const infoEl = document.getElementById('accountInfo');

    if (!statusEl || !infoEl) return;

    const labelMap = {
        username: '用户名',
        email: '邮箱'
    };

    function renderProfile(profile, locationData = null) {
        // 只展示用户名和邮箱
        const orderedKeys = ['username', 'email'];
        infoEl.innerHTML = orderedKeys
            .filter(key => profile[key] !== undefined)
            .map(key => {
                const value = profile[key];
                const valueHtml = (value === null || value === undefined || value === '')
                    ? '<span class="placeholder">暂无</span>'
                    : escapeHtml(value);
                return `
                    <div class="info-item">
                        <p class="info-value">${valueHtml}</p>
                        <p class="info-label">${labelMap[key] || ''}</p>
                    </div>
                `;
            })
            .join('');
        infoEl.style.display = 'grid';

        // 渲染位置信息
        if (window.renderLocationInfo && locationData) {
            window.renderLocationInfo(locationData);
        }
    }

    // 加载用户资料和位置信息
    async function loadAccountInfo() {
        try {
            const profileRes = await fetch('/api/account/profile');
            if (profileRes.status === 401) {
                statusEl.textContent = '未登录，正在跳转...';
                setTimeout(() => window.location.href = '/login', 800);
                return;
            }

            const profileData = await profileRes.json();
            if (!profileData || !profileData.success) {
                statusEl.textContent = profileData?.message || '获取资料失败';
                return;
            }

            statusEl.textContent = '已登录';

            // 加载位置信息
            let locationData = null;
            if (window.loadLocationInfo) {
                locationData = await window.loadLocationInfo();
            }

            // 渲染资料（包含位置信息）
            renderProfile(profileData.data || {}, locationData);
        } catch (error) {
            console.error('加载账户信息失败:', error);
            statusEl.textContent = '获取资料失败';
        }
    }

    loadAccountInfo();
});

