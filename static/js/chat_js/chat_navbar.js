// 导航栏相关功能

// 移动端菜单切换
function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
}

// 移动端侧边栏菜单面板切换
function toggleMobileMenuPanel() {
    const menuPanel = document.getElementById('mobileMenuPanel');
    const arrowBtn = document.getElementById('mobileMenuArrowBtn');
    if (!menuPanel) return;
    
    const isActive = menuPanel.classList.toggle('active');
    
    // 更新箭头按钮状态
    if (arrowBtn) {
        if (isActive) {
            arrowBtn.classList.add('active');
        } else {
            arrowBtn.classList.remove('active');
        }
    }
    
    // 防止背景滚动
    if (isActive) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
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

// 初始化移动端菜单
function initMobileMenu() {
    const menuPanel = document.getElementById('mobileMenuPanel');
    if (!menuPanel) return;

    // 点击菜单项后关闭菜单
    const menuItems = menuPanel.querySelectorAll('.mobile-banner-item');
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            // 延迟关闭，让跳转先执行
            setTimeout(() => {
                toggleMobileMenuPanel();
            }, 100);
        });
    });

    // ESC键关闭菜单
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && menuPanel.classList.contains('active')) {
            toggleMobileMenuPanel();
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    updateAuthLink();
    initLogoClick();
    initMobileMenu();
});

