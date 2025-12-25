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
    
    // 获取图片数据和可见性状态
    const result = await fetchCategoryImages(category);
    const images = result.images;
    const isVisible = result.isVisible;
    
    // 检查类别是否被ban
    const section = document.querySelector(`.category-section[data-category="${category}"]`);
    const isBanned = section && section.dataset.banned === 'true';
    
    // 渲染图片
    if (images.length > 0) {
        await renderGallery(images, galleryGrid);
        updateGalleryCount(category, `${images.length} 张图片`);
    } else {
        showEmptyState(galleryGrid);
        updateGalleryCount(category, '0 张图片');
    }
    
    // 如果类别被ban，添加模糊效果并确保overlay显示
    if (isBanned || !isVisible) {
        galleryGrid.classList.add('banned-blur');
        // 确保有banned-overlay（如果函数存在）
        if (section && typeof ensureBannedOverlay === 'function') {
            ensureBannedOverlay(section, category);
        }
    } else {
        galleryGrid.classList.remove('banned-blur');
        // 移除banned-overlay（如果函数存在）
        if (section && typeof removeBannedOverlay === 'function') {
            removeBannedOverlay(section);
        }
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

