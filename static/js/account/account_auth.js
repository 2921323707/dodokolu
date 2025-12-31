// 申请创作者和退出登录功能
document.addEventListener('DOMContentLoaded', function () {
    const applyBtn = document.getElementById('applyCreatorBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    if (applyBtn) {
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
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            fetch('/api/account/logout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        localStorage.removeItem('userInfo');
                        window.location.href = '/login';
                    } else {
                        alert(data.message || '退出登录失败');
                    }
                })
                .catch(() => {
                    alert('退出登录失败，请稍后重试');
                });
        });
    }
});

