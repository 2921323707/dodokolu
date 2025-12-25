// 分类管理功能

/**
 * 加载分类图片
 * @param {string} category - 分类名称
 */
async function loadCategoryImages(category) {
    const galleryGrid = document.querySelector(`[data-grid="${category}"]`);
    
    if (!galleryGrid) {
        return;
    }
    
    // 显示加载状态
    showLoadingState(galleryGrid);
    
    // 更新计数
    updateGalleryCount(category, '加载中...');
    
    // 获取图片数据
    const images = await fetchCategoryImages(category);
    
    // 渲染图片
    if (images.length > 0) {
        await renderGallery(images, galleryGrid);
        updateGalleryCount(category, `${images.length} 张图片`);
    } else {
        showEmptyState(galleryGrid);
        updateGalleryCount(category, '0 张图片');
    }
}

/**
 * 更新图片计数
 * @param {string} category - 分类名称
 * @param {string} text - 计数文本
 */
function updateGalleryCount(category, text) {
    const countElement = document.querySelector(`[data-count="${category}"]`);
    if (countElement) {
        countElement.textContent = text;
    }
}

/**
 * 显示加载状态
 * @param {HTMLElement} container - 容器元素
 */
function showLoadingState(container) {
    container.innerHTML = '<div class="loading-spinner"></div>';
}

/**
 * 显示空状态
 * @param {HTMLElement} container - 容器元素
 */
function showEmptyState(container) {
    if (container) {
        container.innerHTML = `
            <div class="gallery-empty">
                <div class="gallery-empty-icon">📷</div>
                <div class="gallery-empty-text">暂无图片</div>
            </div>
        `;
    }
}

