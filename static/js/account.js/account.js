document.addEventListener('DOMContentLoaded', function () {
    const statusEl = document.getElementById('accountStatus');
    const infoEl = document.getElementById('accountInfo');
    const applyBtn = document.getElementById('applyCreatorBtn');

    const labelMap = {
        username: '用户名',
        email: '邮箱'
    };

    function escapeHtml(raw) {
        return String(raw)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function renderProfile(profile) {
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
    }

    fetch('/api/account/profile')
        .then(res => {
            if (res.status === 401) {
                statusEl.textContent = '未登录，正在跳转...';
                setTimeout(() => window.location.href = '/login', 800);
                return null;
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;
            if (data.success) {
                statusEl.textContent = '已登录';
                renderProfile(data.data || {});
            } else {
                statusEl.textContent = data.message || '获取资料失败';
            }
        })
        .catch(() => {
            statusEl.textContent = '获取资料失败';
        });

    applyBtn.addEventListener('click', () => {
        const code = prompt('请输入邀请码，站主QQ:2921323707');
        if (!code) return;
        fetch('/api/account/apply-creator', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ invite_code: code.trim() })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message || '身份验证通过，身份已更新');
                } else {
                    alert(data.message || '申请失败');
                }
            })
            .catch(() => {
                alert('申请失败，请稍后重试');
            });
    });
});
