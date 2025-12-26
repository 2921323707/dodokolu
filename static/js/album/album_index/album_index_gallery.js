// 图片展示功能

/**
 * 渲染图片画廊
 * @param {Array} images - 图片数组
 * @param {HTMLElement} container - 容器元素（可选，如果不提供则使用默认容器）
 */
async function renderGallery(images, container = null) {
    const galleryGrid = container || document.getElementById('galleryGrid');
    
    if (!galleryGrid) {
        return;
    }
    
    // 获取用户信息
    let userInfo = null;
    try {
        const response = await fetch('/api/auth-status');
        const data = await response.json();
        if (data.success) {
            userInfo = {
                logged_in: data.logged_in || false,
                user: data.user || null
            };
        }
    } catch (error) {
        console.error('获取用户信息失败:', error);
    }
    
    // 清空现有内容
    galleryGrid.innerHTML = '';
    
    // 创建图片项
    images.forEach((image, index) => {
        const galleryItem = createGalleryItem(image, index, userInfo);
        galleryGrid.appendChild(galleryItem);
    });
}

/**
 * 创建单个图片项
 * @param {Object} image - 图片对象 {url, name, path, type}
 * @param {number} index - 索引
 * @param {Object} userInfo - 用户信息 {logged_in, role}
 * @returns {HTMLElement} 图片项元素
 */
function createGalleryItem(image, index, userInfo = null) {
    const item = document.createElement('div');
    item.className = 'gallery-item';
    item.dataset.index = index;
    // 默认尺寸，图片加载后会更新
    item.dataset.size = 'small';
    
    // 判断是否需要二次模糊（根据后端返回的needs_blur标记）
    const needsBlur = image.needs_blur === true;
    
    if (needsBlur) {
        item.classList.add('gallery-item-blurred');
        item.dataset.needsAdmin = 'true';
    }
    
    // 创建图片元素
    const img = document.createElement('img');
    img.src = image.url;
    img.alt = image.name || '图片';
    img.loading = 'lazy'; // 懒加载
    
    // 图片加载错误处理
    img.onerror = function() {
        this.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="240" height="320"%3E%3Crect width="240" height="320" fill="%23f0f0f0"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999" font-size="14"%3E图片加载失败%3C/text%3E%3C/svg%3E';
    };
    
    // 图片加载完成后，根据实际尺寸设置网格大小
    img.onload = function() {
        const width = this.naturalWidth;
        const height = this.naturalHeight;
        const aspectRatio = width / height;
        const area = width * height;
        
        // 根据宽高比和尺寸决定网格跨度
        let size = 'small';
        
        // 横向图片（宽大于高）
        if (aspectRatio > 1.4) {
            if (area > 800000) {
                // 大横向图片
                size = 'wide';
            } else {
                size = 'small';
            }
        }
        // 竖向图片（高大于宽）
        else if (aspectRatio < 0.75) {
            if (area > 800000) {
                // 大竖向图片
                size = 'tall';
            } else if (area > 400000) {
                // 中等竖向图片
                size = 'medium';
            } else {
                size = 'small';
            }
        }
        // 接近正方形或略长的图片
        else {
            if (area > 1200000) {
                // 大图
                size = 'large';
            } else if (area > 500000) {
                // 中等图片
                size = 'medium';
            } else {
                size = 'small';
            }
        }
        
        item.dataset.size = size;
        
        // 触发重新布局（如果需要）
        // 使用 requestAnimationFrame 确保 DOM 更新后再调整
        requestAnimationFrame(() => {
            // 可以在这里添加额外的布局优化逻辑
        });
    };
    
    // 创建遮罩层（显示图片名称）
    const overlay = document.createElement('div');
    overlay.className = 'gallery-item-overlay';
    const nameSpan = document.createElement('span');
    nameSpan.className = 'gallery-item-name';
    nameSpan.textContent = image.name || '未命名';
    overlay.appendChild(nameSpan);
    
    // 组装元素
    item.appendChild(img);
    item.appendChild(overlay);
    
    // 点击事件（可以扩展为查看大图等功能）
    item.addEventListener('click', () => {
        handleImageClick(image, index);
    });
    
    return item;
}

/**
 * 处理图片点击事件
 * @param {Object} image - 图片对象
 * @param {number} index - 索引
 */
function handleImageClick(image, index) {
    // 跳转到图片展开页面
    const params = new URLSearchParams({
        image: image.url,  // URLSearchParams 会自动编码
        name: image.name || '未命名图片',
        category: getCurrentCategory() || '',
        index: index.toString(),
        type: image.type || ''  // 添加图片类型参数
    });
    
    window.location.href = `/album/pic_expand?${params.toString()}`;
}

/**
 * 获取当前分类
 * @returns {string} 当前分类名称
 */
function getCurrentCategory() {
    // 从 URL 参数获取分类
    const urlParams = new URLSearchParams(window.location.search);
    const category = urlParams.get('category');
    if (category) {
        return category;
    }
    
    // 从活动标签获取分类
    const activeTab = document.querySelector('.category-tab.active');
    if (activeTab) {
        return activeTab.dataset.category || '';
    }
    
    // 从当前显示的画廊获取分类
    const activeGrid = document.querySelector('.gallery-grid:not([style*="display: none"])');
    if (activeGrid) {
        return activeGrid.dataset.grid || '';
    }
    
    return '';
}

