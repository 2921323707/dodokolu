// 侧边栏折叠功能
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('accountSidebar');
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');

    if (!sidebar || !sidebarToggleBtn) return;

    // 从本地存储读取折叠状态
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        sidebar.classList.add('collapsed');
    }

    sidebarToggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        const collapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', collapsed);
    });
});

