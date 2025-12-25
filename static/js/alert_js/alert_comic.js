// 番剧相关功能

// 加载番剧数据
async function loadComics() {
    const comicList = document.getElementById('comicList');
    if (!comicList) return;

    try {
        const response = await fetch(`${API_BASE}/comics`);
        const result = await response.json();

        if (result.success && result.data && result.data.animes && result.data.animes.length > 0) {
            const data = result.data;
            // 保存所有番剧数据
            allAnimesData = data;

            // 显示日期到节日区域
            const comicDate = document.getElementById('comicDate');
            if (comicDate) {
                const updateDate = new Date(data.file_update_time);
                comicDate.textContent = updateDate.toLocaleDateString('zh-CN', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            }

            // 初始化显示（只显示前3条）
            renderComicList(data.animes, false);

            // 添加点击展开功能
            setupComicSectionExpand();
        } else {
            comicList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📺</div>
                    <p>暂无番剧推荐</p>
                    <p style="margin-top: 8px; font-size: 0.9rem;">请等待每日更新</p>
                </div>
            `;

            // 清空日期显示
            const comicDate = document.getElementById('comicDate');
            if (comicDate) {
                comicDate.textContent = '';
            }
        }
    } catch (error) {
        console.error('加载番剧数据失败:', error);
        comicList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <p>加载失败，请稍后重试</p>
            </div>
        `;
    }
}

// 创建番剧卡片元素
function createComicItem(anime, index) {
    const item = document.createElement('div');
    item.className = 'comic-item';
    item.style.animationDelay = `${index * 0.1}s`;

    const link = document.createElement('a');
    link.href = anime.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.className = 'comic-link';

    // 格式化时间
    const updateTime = formatTime(anime.update_time);

    link.innerHTML = `
        <div class="comic-item-header">
            <div class="comic-name">${escapeHtml(anime.name)}</div>
            <div class="comic-time">${updateTime}</div>
        </div>
    `;

    item.appendChild(link);
    return item;
}

// 格式化时间显示
function formatTime(timeString) {
    try {
        const date = new Date(timeString);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) {
            return '刚刚';
        } else if (minutes < 60) {
            return `${minutes}分钟前`;
        } else if (hours < 24) {
            return `${hours}小时前`;
        } else if (days < 7) {
            return `${days}天前`;
        } else {
            return date.toLocaleDateString('zh-CN', {
                month: 'short',
                day: 'numeric'
            });
        }
    } catch (e) {
        return timeString;
    }
}

// HTML转义，防止XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 渲染番剧列表
function renderComicList(animes, isExpanded) {
    const comicList = document.getElementById('comicList');
    if (!comicList) return;

    // 根据展开状态决定显示的数量
    const displayAnimes = isExpanded ? animes : animes.slice(0, 3);

    // 创建包装容器
    const wrapper = document.createElement('div');
    wrapper.className = 'comic-list-wrapper-inner';
    comicList.innerHTML = '';
    comicList.appendChild(wrapper);

    // 创建列表
    displayAnimes.forEach((anime, index) => {
        const comicItem = createComicItem(anime, index);
        wrapper.appendChild(comicItem);
    });
}

// 设置番剧区域展开功能
function setupComicSectionExpand() {
    const comicSection = document.querySelector('.comic-section');
    if (!comicSection) return;

    let isExpanded = false;
    let overlay = null;

    // 创建遮罩层
    function createOverlay() {
        if (overlay) return overlay;
        overlay = document.createElement('div');
        overlay.className = 'comic-expand-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.3);
            z-index: 999;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(overlay);
        // 点击遮罩层关闭
        overlay.addEventListener('click', function() {
            closeExpand();
        });
        return overlay;
    }

    // 关闭展开
    function closeExpand() {
        isExpanded = false;
        comicSection.classList.remove('expanded');
        // 清除自定义样式
        comicSection.style.top = '';
        comicSection.style.left = '';
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => {
                if (overlay && overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                    overlay = null;
                }
            }, 300);
        }
        // 重新渲染列表
        if (allAnimesData && allAnimesData.animes) {
            renderComicList(allAnimesData.animes, false);
        }
    }

    // 点击事件（排除内部链接点击）
    comicSection.addEventListener('click', function (e) {
        // 如果点击的是链接，不触发展开
        if (e.target.closest('.comic-link')) {
            return;
        }

        if (!isExpanded) {
            // 获取屏幕中心位置
            const centerX = window.innerWidth / 2;
            const centerY = window.innerHeight / 2;
            
            isExpanded = true;
            comicSection.classList.add('expanded');
            
            // 设置展开后的位置（从屏幕中心展开）
            comicSection.style.top = `${centerY}px`;
            comicSection.style.left = `${centerX}px`;
            
            // 显示遮罩层
            const overlayEl = createOverlay();
            setTimeout(() => {
                overlayEl.style.opacity = '1';
            }, 10);
            
            // 重新渲染列表
            if (allAnimesData && allAnimesData.animes) {
                renderComicList(allAnimesData.animes, true);
            }
        }
    });

    // ESC键关闭
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isExpanded) {
            closeExpand();
        }
    });
}


