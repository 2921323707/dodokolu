// 导航切换功能
document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.sidebar-nav-link');
    const sections = document.querySelectorAll('.account-section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // 移除所有活动状态
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.style.display = 'none');

            // 添加当前活动状态
            link.classList.add('active');
            const sectionId = link.getAttribute('data-section');
            const targetSection = document.getElementById(`section-${sectionId}`);
            if (targetSection) {
                targetSection.style.display = 'block';

                // 如果切换到section1（模型配置页面），加载智能体列表
                if (sectionId === 'section1' && window.loadAgentsList) {
                    window.loadAgentsList();
                }
                // 如果切换到section2（聊天记录页面），加载聊天记录
                else if (sectionId === 'section2' && window.loadChatHistoryFiles) {
                    window.loadChatHistoryFiles();
                }
                // 如果切换到section3（关于页面），加载GitHub更新信息
                else if (sectionId === 'section3' && window.loadGitHubUpdateInfo) {
                    window.loadGitHubUpdateInfo();
                }
            }
        });
    });
});

