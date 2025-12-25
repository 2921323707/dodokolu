// 导航栏相关功能

// 移动端菜单切换
function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
}

// 根据登录状态更新导航栏（登录 -> 账户）
function updateAuthLink() {
    const authLink = document.getElementById('authNavLink');
    if (!authLink) return;

    fetch('/api/auth-status')
        .then(res => res.json())
        .then(data => {
            if (data.logged_in) {
                // 缓存用户信息供其他页面使用
                if (data.user) {
                    localStorage.setItem('userInfo', JSON.stringify(data.user));
                }
                authLink.textContent = '账户';
                authLink.setAttribute('href', '/account');
            } else {
                localStorage.removeItem('userInfo');
                authLink.textContent = '登录';
                authLink.setAttribute('href', '/login');
            }
        })
        .catch(() => {
            // 请求失败时不改动UI
        });
}

// Logo 点击跳转到聊天界面
function initLogoClick() {
    const logo = document.querySelector('.logo span');
    if (logo) {
        logo.addEventListener('click', () => {
            window.location.href = '/';
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateAuthLink();
    initLogoClick();
});

