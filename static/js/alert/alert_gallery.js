// 画集展示框图片轮播功能

// API端点
const ALBUM_API_BASE = '/album/api/images';

// 存储所有可用的图片
let allWallpaperImages = [];
let imageRotationInterval = null;
let currentBackgroundLayer = 1; // 当前显示的背景层（1或2）
let currentImageUrl = null; // 当前显示的图片URL

/**
 * 从wallpaper分类中获取所有图片
 */
async function fetchWallpaperImages() {
    try {
        const response = await fetch(`${ALBUM_API_BASE}/wallpaper`);
        const data = await response.json();
        
        if (data.success && data.data) {
            // 获取所有有URL的图片
            const images = data.data.filter(img => img.url);
            return images;
        }
        return [];
    } catch (error) {
        console.error('获取图片失败:', error);
        return [];
    }
}

/**
 * 从图片列表中随机选择一张（确保与上一张不同）
 */
function selectRandomImage(images, excludeUrl = null) {
    if (images.length === 0) return null;
    
    // 如果只有一张图片，直接返回
    if (images.length === 1) {
        return images[0];
    }
    
    // 过滤掉与上一张相同的图片
    let availableImages = images;
    if (excludeUrl) {
        availableImages = images.filter(img => img.url !== excludeUrl);
    }
    
    // 如果过滤后没有可用图片（理论上不应该发生），使用所有图片
    if (availableImages.length === 0) {
        availableImages = images;
    }
    
    // 随机选择
    const randomIndex = Math.floor(Math.random() * availableImages.length);
    return availableImages[randomIndex];
}

/**
 * 创建背景层元素
 */
function createBackgroundLayer(layerNumber) {
    const placeholder = document.getElementById('galleryPlaceholder');
    if (!placeholder) return null;
    
    let layer = placeholder.querySelector(`.bg-layer-${layerNumber}`);
    if (!layer) {
        layer = document.createElement('div');
        layer.className = `gallery-bg-layer bg-layer-${layerNumber}`;
        placeholder.insertBefore(layer, placeholder.firstChild);
    }
    return layer;
}

/**
 * 设置背景图片（使用淡入淡出效果）
 */
function setBackgroundImage(imageUrl) {
    const placeholder = document.getElementById('galleryPlaceholder');
    if (!placeholder) return;
    
    // 切换到另一个背景层
    const nextLayer = currentBackgroundLayer === 1 ? 2 : 1;
    const currentLayer = createBackgroundLayer(currentBackgroundLayer);
    const newLayer = createBackgroundLayer(nextLayer);
    
    if (!currentLayer || !newLayer) return;
    
    // 设置新层的背景图片
    newLayer.style.backgroundImage = `url(${imageUrl})`;
    newLayer.style.opacity = '0';
    
    // 触发重排，确保新图片加载
    newLayer.offsetHeight;
    
    // 淡入新层，淡出旧层
    setTimeout(() => {
        newLayer.style.opacity = '1';
        currentLayer.style.opacity = '0';
    }, 50);
    
    // 更新当前层和当前图片URL
    currentBackgroundLayer = nextLayer;
    currentImageUrl = imageUrl;
}

/**
 * 初始化图片轮播
 */
async function initGalleryImageRotation() {
    const placeholder = document.getElementById('galleryPlaceholder');
    if (!placeholder) return;
    
    // 获取所有wallpaper图片
    allWallpaperImages = await fetchWallpaperImages();
    if (allWallpaperImages.length === 0) {
        console.warn('未找到wallpaper类型的图片');
        return;
    }
    
    // 立即显示第一张随机图片
    const firstImage = selectRandomImage(allWallpaperImages, null);
    if (firstImage) {
        setBackgroundImage(firstImage.url);
    }
    
    // 启动轮播
    startImageRotation();
}

/**
 * 启动图片轮播（每3秒切换一次，随机选择）
 */
function startImageRotation() {
    // 清除之前的定时器
    if (imageRotationInterval) {
        clearInterval(imageRotationInterval);
    }
    
    const placeholder = document.getElementById('galleryPlaceholder');
    if (!placeholder || allWallpaperImages.length === 0) return;
    
    // 每3秒随机切换一张图片（确保与上一张不同）
    imageRotationInterval = setInterval(() => {
        const randomImage = selectRandomImage(allWallpaperImages, currentImageUrl);
        if (randomImage) {
            setBackgroundImage(randomImage.url);
        }
    }, 3000);
}

/**
 * 停止图片轮播
 */
function stopImageRotation() {
    if (imageRotationInterval) {
        clearInterval(imageRotationInterval);
        imageRotationInterval = null;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 延迟初始化，确保其他资源加载完成
    setTimeout(() => {
        initGalleryImageRotation();
    }, 500);
});

// 页面卸载时清理定时器
window.addEventListener('beforeunload', function() {
    stopImageRotation();
});

