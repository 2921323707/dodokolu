document.addEventListener('DOMContentLoaded', function () {
    const adminStatus = document.getElementById('adminStatus');

    // 检查管理员状态
    fetch('/api/auth-status')
        .then(res => res.json())
        .then(data => {
            if (!data.logged_in) {
                // 未登录，跳转到登录页
                window.location.href = '/login';
                return;
            }

            if (data.user && data.user.role !== 2) {
                // 不是管理员，跳转到账户页
                alert('您不是管理员，无权限访问此页面');
                window.location.href = '/account';
                return;
            }

            // 是管理员，显示页面
            adminStatus.textContent = '管理员模式';
            adminStatus.style.background = '#10b981';
        })
        .catch(error => {
            console.error('检查管理员状态失败:', error);
            alert('验证失败，请刷新页面重试');
            window.location.href = '/account';
        });
});

