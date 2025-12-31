// GitHub更新信息功能
document.addEventListener('DOMContentLoaded', function () {
    // 格式化时间
    function formatTime(dateString) {
        if (!dateString) return '未知';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) {
            return '刚刚';
        } else if (diffMins < 60) {
            return `${diffMins}分钟前`;
        } else if (diffHours < 24) {
            return `${diffHours}小时前`;
        } else if (diffDays < 7) {
            return `${diffDays}天前`;
        } else {
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }

    // 获取作者名称
    function getAuthorName(commit) {
        let authorName = '未知';
        if (commit.author) {
            if (commit.author.name && commit.author.name.trim() !== '') {
                authorName = commit.author.name.trim();
            } else if (commit.author.email && commit.author.email.trim() !== '') {
                const email = commit.author.email.trim();
                const emailParts = email.split('@');
                if (emailParts.length > 0 && emailParts[0]) {
                    authorName = emailParts[0];
                }
            }
        }
        return authorName;
    }

    // 加载GitHub更新信息（显示最近三次提交）
    async function loadGitHubUpdateInfo() {
        const updateLoading = document.getElementById('updateLoading');
        const updateContent = document.getElementById('updateContent');
        const updateError = document.getElementById('updateError');

        if (!updateLoading || !updateContent || !updateError) return;

        // 显示加载状态
        updateLoading.style.display = 'block';
        updateContent.style.display = 'none';
        updateError.style.display = 'none';

        try {
            // 获取最近三次提交
            const response = await fetch('/api/github/commits?owner=2921323707&repo=dodokolu&branch=main&per_page=3');
            const data = await response.json();

            if (data.success && data.data && Array.isArray(data.data) && data.data.length > 0) {
                const commits = data.data;

                // 生成提交列表HTML
                const commitsHtml = commits.map((commit, index) => {
                    // 格式化提交信息（只显示第一行）
                    const message = commit.message ? commit.message.split('\n')[0] : '无提交信息';
                    const timeText = formatTime(commit.date);
                    const authorName = getAuthorName(commit);
                    const hasLink = commit.url && commit.url.trim() !== '';

                    return `
                        <div class="update-item ${index < commits.length - 1 ? 'update-item-separator' : ''}">
                            <div class="update-message">${escapeHtml(message)}</div>
                            <div class="update-meta">
                                <span class="update-time">更新时间: ${timeText}</span>
                                <span class="update-author">作者: ${escapeHtml(authorName)}</span>
                            </div>
                            ${hasLink ? `<a href="${escapeHtml(commit.url)}" target="_blank" class="update-link">查看详情</a>` : ''}
                        </div>
                    `;
                }).join('');

                updateContent.innerHTML = commitsHtml;

                // 显示内容
                updateLoading.style.display = 'none';
                updateContent.style.display = 'block';
            } else {
                throw new Error(data.error || '获取更新信息失败');
            }
        } catch (error) {
            console.error('加载GitHub更新信息失败:', error);
            updateLoading.style.display = 'none';
            updateError.style.display = 'block';
        }
    }

    // 暴露给导航模块使用
    window.loadGitHubUpdateInfo = loadGitHubUpdateInfo;
});

