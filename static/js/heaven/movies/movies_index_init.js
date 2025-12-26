// 视频页面初始化功能

/**
 * 初始化页面
 */
async function initPage() {
    const loading = document.getElementById('loading');

    // 显示加载状态
    if (loading) {
        loading.classList.add('active');
    }

    // 获取视频列表
    const videos = await fetchVideos();

    // 渲染视频列表
    renderVideos(videos);
}

/**
 * 返回上一页
 */
function goBack() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.href = '/';
    }
}

// 键盘快捷键
document.addEventListener('keydown', function (e) {
    // ESC 键返回
    if (e.key === 'Escape') {
        goBack();
    }
});

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    initPage();
});

