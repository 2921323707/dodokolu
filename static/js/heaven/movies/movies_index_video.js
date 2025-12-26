// 视频项创建和预览功能

// 引入视频详情模态框功能（需要在movies_index_modal.js之后加载）

/**
 * 创建视频项
 * @param {Object} video - 视频对象 {url, name, source, filename}
 * @returns {HTMLElement} 视频项元素
 */
function createVideoItem(video) {
    const item = document.createElement('div');
    item.className = 'video-item';

    // 视频容器
    const videoWrapper = document.createElement('div');
    videoWrapper.className = 'video-wrapper';

    const videoElement = document.createElement('video');
    videoElement.preload = 'metadata';
    videoElement.controls = false; // 预览模式不显示控制栏
    videoElement.playsInline = true;
    videoElement.muted = true; // 预览时静音，自动播放需要静音
    videoElement.classList.add('video-preview'); // 添加预览类用于CSS控制

    // 标记是否已加载完整视频
    let isFullVideoLoaded = false;
    let previewEndTime = 8; // 8秒预览
    let timeUpdateHandler = null;

    // 加载预览视频（前8秒）
    function loadPreview() {
        if (isFullVideoLoaded) return;

        // 设置视频源
        videoElement.src = video.url;

        // 监听metadata加载完成
        videoElement.addEventListener('loadedmetadata', function onMetadataLoaded() {
            // 移除监听器
            videoElement.removeEventListener('loadedmetadata', onMetadataLoaded);

            // 设置当前时间为8秒，触发加载前8秒的数据
            if (videoElement.duration > previewEndTime) {
                videoElement.currentTime = previewEndTime;

                // 等待数据加载
                videoElement.addEventListener('seeked', function onSeeked() {
                    videoElement.removeEventListener('seeked', onSeeked);

                    // 回到开始位置
                    videoElement.currentTime = 0;

                    // 监听播放到8秒时循环（仅在预览模式下）
                    timeUpdateHandler = function onTimeUpdate() {
                        if (!isFullVideoLoaded && videoElement.currentTime >= previewEndTime) {
                            videoElement.currentTime = 0;
                        }
                    };
                    videoElement.addEventListener('timeupdate', timeUpdateHandler);

                    // 等待回到0秒后开始自动播放
                    videoElement.addEventListener('seeked', function onSeekedToStart() {
                        videoElement.removeEventListener('seeked', onSeekedToStart);
                        videoElement.play().catch(err => {
                            console.log('自动播放失败:', err);
                        });
                    }, { once: true });
                }, { once: true });
            } else {
                // 视频长度小于8秒，直接播放完整视频
                isFullVideoLoaded = true;
                videoElement.play().catch(err => {
                    console.log('自动播放失败:', err);
                });
            }
        }, { once: true });
    }

    // 打开视频详情页
    function openVideoDetail() {
        // 创建视频详情模态框
        showVideoDetailModal(video);
    }

    // 视频容器点击事件 - 打开详情页
    videoWrapper.addEventListener('click', function (e) {
        e.stopPropagation();
        openVideoDetail();
    });

    // 视频元素点击事件 - 打开详情页
    videoElement.addEventListener('click', function (e) {
        e.stopPropagation();
        openVideoDetail();
    });

    // 视频信息
    const videoInfo = document.createElement('div');
    videoInfo.className = 'video-info';

    const videoName = document.createElement('div');
    videoName.className = 'video-name';
    videoName.textContent = video.name || video.filename;

    const videoSource = document.createElement('div');
    videoSource.className = 'video-source';
    videoSource.textContent = `来源: ${video.source}`;

    // 组装元素
    videoWrapper.appendChild(videoElement);
    videoInfo.appendChild(videoName);
    videoInfo.appendChild(videoSource);
    item.appendChild(videoWrapper);
    item.appendChild(videoInfo);

    // 点击事件：切换激活状态
    item.addEventListener('click', function (e) {
        // 如果点击的是视频容器或视频本身，不处理（已在上面处理）
        if (e.target.closest('.video-wrapper')) {
            return;
        }

        // 切换激活状态
        const isActive = item.classList.contains('active');
        document.querySelectorAll('.video-item').forEach(v => {
            v.classList.remove('active');
        });

        if (!isActive) {
            item.classList.add('active');
        }
    });

    // 开始加载预览
    loadPreview();

    return item;
}

