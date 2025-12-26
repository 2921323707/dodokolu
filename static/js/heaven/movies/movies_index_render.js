// 视频列表渲染功能

/**
 * 渲染视频列表
 * @param {Array} videos - 视频数组
 */
function renderVideos(videos) {
    const videosGrid = document.getElementById('videosGrid');
    const loading = document.getElementById('loading');
    const emptyState = document.getElementById('emptyState');

    if (!videosGrid) {
        return;
    }

    // 隐藏加载状态
    if (loading) {
        loading.classList.remove('active');
    }

    // 清空现有内容
    videosGrid.innerHTML = '';

    if (videos.length === 0) {
        // 显示空状态
        if (emptyState) {
            emptyState.style.display = 'block';
        }
        return;
    }

    // 隐藏空状态
    if (emptyState) {
        emptyState.style.display = 'none';
    }

    // 创建视频项
    videos.forEach(video => {
        const videoItem = createVideoItem(video);
        videosGrid.appendChild(videoItem);
    });
}

