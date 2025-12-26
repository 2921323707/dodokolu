// 视频详情模态框功能

/**
 * 显示视频详情模态框
 * @param {Object} video - 视频对象 {url, name, source, filename}
 */
function showVideoDetailModal(video) {
    // 创建模态框容器
    const modal = document.createElement('div');
    modal.className = 'video-detail-modal';
    modal.id = 'videoDetailModal';

    // 创建模态框内容
    const modalContent = document.createElement('div');
    modalContent.className = 'video-detail-modal-content';

    // 创建关闭按钮
    const closeBtn = document.createElement('button');
    closeBtn.className = 'video-detail-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.setAttribute('aria-label', '关闭');

    // 创建视频容器
    const videoContainer = document.createElement('div');
    videoContainer.className = 'video-detail-container';

    // 创建视频元素
    const videoElement = document.createElement('video');
    videoElement.src = video.url;
    videoElement.controls = true;
    videoElement.playsInline = true;
    videoElement.preload = 'auto'; // 预加载完整视频
    videoElement.className = 'video-detail-player';
    
    // 确保视频可以加载完整内容
    videoElement.load(); // 强制加载视频

    // 创建视频信息
    const videoInfo = document.createElement('div');
    videoInfo.className = 'video-detail-info';

    const videoName = document.createElement('h2');
    videoName.className = 'video-detail-name';
    videoName.textContent = video.name || video.filename;

    const videoSource = document.createElement('p');
    videoSource.className = 'video-detail-source';
    videoSource.textContent = `来源: ${video.source}`;

    // 组装元素
    videoContainer.appendChild(videoElement);
    videoInfo.appendChild(videoName);
    videoInfo.appendChild(videoSource);
    modalContent.appendChild(closeBtn);
    modalContent.appendChild(videoContainer);
    modalContent.appendChild(videoInfo);
    modal.appendChild(modalContent);

    // 添加到页面
    document.body.appendChild(modal);

    // 显示模态框（添加动画）
    requestAnimationFrame(() => {
        modal.classList.add('active');
        
        // 等待视频可以播放时再自动播放
        videoElement.addEventListener('canplaythrough', function onCanPlay() {
            videoElement.removeEventListener('canplaythrough', onCanPlay);
            // 自动播放视频
            videoElement.play().catch(err => {
                console.log('自动播放失败:', err);
            });
        }, { once: true });
        
        // 如果已经可以播放，直接播放
        if (videoElement.readyState >= 3) { // HAVE_FUTURE_DATA
            videoElement.play().catch(err => {
                console.log('自动播放失败:', err);
            });
        }
    });

    // 关闭按钮事件
    closeBtn.addEventListener('click', function () {
        closeVideoDetailModal(modal);
    });

    // 点击背景关闭
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            closeVideoDetailModal(modal);
        }
    });

    // ESC 键关闭
    const escHandler = function (e) {
        if (e.key === 'Escape') {
            closeVideoDetailModal(modal);
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);

    // 阻止body滚动
    document.body.style.overflow = 'hidden';
}

/**
 * 关闭视频详情模态框
 * @param {HTMLElement} modal - 模态框元素
 */
function closeVideoDetailModal(modal) {
    if (!modal) {
        modal = document.getElementById('videoDetailModal');
    }
    if (!modal) return;

    // 停止视频播放
    const videoElement = modal.querySelector('.video-detail-player');
    if (videoElement) {
        videoElement.pause();
        videoElement.src = ''; // 清空src释放资源
    }

    // 移除active类，触发关闭动画
    modal.classList.remove('active');

    // 等待动画完成后移除元素
    setTimeout(() => {
        if (modal.parentNode) {
            modal.parentNode.removeChild(modal);
        }
        // 恢复body滚动
        document.body.style.overflow = '';
    }, 300);
}

