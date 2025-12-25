// 相册页面初始化

// 分类列表（按显示顺序）
const CATEGORIES = ['anime', 'wallpaper', 'photo', 'scene'];

// 需要登录的分类（未登录时显示模糊覆盖层）
const LOGIN_REQUIRED_CATEGORIES = ['anime', 'photo'];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 初始化登录状态标记
    try {
        const response = await fetch('/api/auth-status');
        const data = await response.json();
        document.body.dataset.wasLoggedIn = (data.logged_in === true).toString();
    } catch (error) {
        document.body.dataset.wasLoggedIn = 'false';
    }
    
    // 检查登录状态并应用模糊效果
    checkLoginStatusAndApplyBlur();
    // 加载所有分类的图片
    loadAllCategories();
    
    // 监听 localStorage 变化（当用户在其他标签页登录时）
    window.addEventListener('storage', (e) => {
        if (e.key === 'userInfo') {
            checkLoginStatusAndApplyBlur();
        }
    });
    
    // 定期检查登录状态（用于处理同标签页登录的情况）
    setInterval(checkLoginStatusAndApplyBlur, 5000);
});

/**
 * 检查登录状态并应用模糊效果
 */
async function checkLoginStatusAndApplyBlur() {
    try {
        const response = await fetch('/api/auth-status');
        const data = await response.json();
        
        const isLoggedIn = data.logged_in === true;
        const wasLoggedIn = document.body.dataset.wasLoggedIn === 'true';
        
        // 如果登录状态发生变化，重新加载图片
        if (isLoggedIn !== wasLoggedIn) {
            document.body.dataset.wasLoggedIn = isLoggedIn;
            // 重新加载所有分类的图片
            loadAllCategories();
        }
        
        // 为每个需要登录的分类应用或移除模糊效果
        LOGIN_REQUIRED_CATEGORIES.forEach(category => {
            const section = document.querySelector(`.category-section[data-category="${category}"]`);
            if (section) {
                const galleryWrapper = section.querySelector('.gallery-wrapper');
                if (galleryWrapper) {
                    if (isLoggedIn) {
                        galleryWrapper.classList.add('logged-in');
                    } else {
                        galleryWrapper.classList.remove('logged-in');
                    }
                }
            }
        });
    } catch (error) {
        console.error('检查登录状态失败:', error);
        // 如果检查失败，默认显示模糊效果（要求登录）
        LOGIN_REQUIRED_CATEGORIES.forEach(category => {
            const section = document.querySelector(`.category-section[data-category="${category}"]`);
            if (section) {
                const galleryWrapper = section.querySelector('.gallery-wrapper');
                if (galleryWrapper) {
                    galleryWrapper.classList.remove('logged-in');
                }
            }
        });
    }
}

/**
 * 加载所有分类的图片
 */
async function loadAllCategories() {
    // 并行加载所有分类
    const promises = CATEGORIES.map(category => loadCategoryImages(category));
    await Promise.all(promises);
}

