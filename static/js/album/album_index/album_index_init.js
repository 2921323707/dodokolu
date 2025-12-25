// 相册页面初始化

// 动态加载的类别列表
let CATEGORIES = [];
// 类别配置映射 {category_key: {display_name, ...}}
let CATEGORY_CONFIG = {};

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

    // 先加载所有类别列表（包括被ban的）
    await loadVisibleCategories();

    // 检查登录状态并应用模糊效果
    checkLoginStatusAndApplyBlur();
    // 加载所有可见分类的图片
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

        // 为每个需要登录的可见分类应用或移除模糊效果（不包括被ban的类别）
        LOGIN_REQUIRED_CATEGORIES.forEach(category => {
            // 只处理可见的类别
            if (!CATEGORIES.includes(category)) {
                return;
            }
            const section = document.querySelector(`.category-section[data-category="${category}"]`);
            // 如果类别被ban，跳过登录相关的逻辑
            if (section && section.dataset.banned === 'true') {
                return;
            }
            if (section && section.style.display !== 'none') {
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
        // 如果检查失败，默认显示模糊效果（要求登录，但不包括被ban的类别）
        LOGIN_REQUIRED_CATEGORIES.forEach(category => {
            // 只处理可见的类别
            if (!CATEGORIES.includes(category)) {
                return;
            }
            const section = document.querySelector(`.category-section[data-category="${category}"]`);
            // 如果类别被ban，跳过登录相关的逻辑
            if (section && section.dataset.banned === 'true') {
                return;
            }
            if (section && section.style.display !== 'none') {
                const galleryWrapper = section.querySelector('.gallery-wrapper');
                if (galleryWrapper) {
                    galleryWrapper.classList.remove('logged-in');
                }
            }
        });
    }
}

/**
 * 加载可见的类别列表并更新页面
 */
async function loadVisibleCategories() {
    try {
        const categories = await fetchVisibleCategories();

        // 构建类别配置映射（包括所有类别，可见和不可见的）
        CATEGORY_CONFIG = {};
        categories.forEach(cat => {
            CATEGORY_CONFIG[cat.category_key] = cat;
        });

        // 更新CATEGORIES数组（只包含可见的类别）
        CATEGORIES = categories.filter(cat => cat.is_visible).map(cat => cat.category_key);

        // 更新页面上的类别区域（包括被ban的类别）
        updateCategorySections(categories);
    } catch (error) {
        console.error('加载类别列表失败:', error);
        // 如果加载失败，使用默认类别列表（向后兼容）
        CATEGORIES = ['anime', 'wallpaper', 'photo', 'scene'];
    }
}

/**
 * 更新页面上的类别区域（显示/隐藏，更新标题，标记被ban的类别）
 */
function updateCategorySections(allCategories) {
    // 构建所有类别的映射
    const allCategoriesMap = new Map();
    allCategories.forEach(cat => {
        allCategoriesMap.set(cat.category_key, cat);
    });

    // 遍历所有类别区域
    document.querySelectorAll('.category-section').forEach(section => {
        const categoryKey = section.dataset.category;

        if (categoryKey && allCategoriesMap.has(categoryKey)) {
            const config = allCategoriesMap.get(categoryKey);

            // 显示类别区域（包括被ban的）
            section.style.display = '';

            // 更新类别标题
            if (config) {
                const titleElement = section.querySelector('.category-title');
                if (titleElement) {
                    titleElement.textContent = config.display_name;
                }
            }

            // 标记被ban的类别
            if (!config.is_visible) {
                section.dataset.banned = 'true';
                // 确保有banned-overlay
                ensureBannedOverlay(section, categoryKey);
            } else {
                section.removeAttribute('data-banned');
                // 移除banned-overlay（如果存在）
                removeBannedOverlay(section);
            }
        } else {
            // 如果类别不在数据库中，隐藏它
            section.style.display = 'none';
        }
    });
}

/**
 * 确保被ban的类别有overlay提示
 */
function ensureBannedOverlay(section, categoryKey) {
    let galleryWrapper = section.querySelector('.gallery-wrapper');
    if (!galleryWrapper) return;

    // 检查是否已有banned-overlay
    let bannedOverlay = galleryWrapper.querySelector('.banned-overlay');
    if (!bannedOverlay) {
        // 创建banned-overlay
        bannedOverlay = document.createElement('div');
        bannedOverlay.className = 'banned-overlay';
        bannedOverlay.setAttribute('data-overlay', categoryKey);
        bannedOverlay.innerHTML = `
            <div class="banned-prompt">
                <h3 class="banned-prompt-title">请联系管理员</h3>
                <p class="banned-prompt-text">此处少儿不宜</p>
            </div>
        `;
        galleryWrapper.appendChild(bannedOverlay);
    }
}

/**
 * 移除banned-overlay
 */
function removeBannedOverlay(section) {
    const galleryWrapper = section.querySelector('.gallery-wrapper');
    if (galleryWrapper) {
        const bannedOverlay = galleryWrapper.querySelector('.banned-overlay');
        if (bannedOverlay) {
            bannedOverlay.remove();
        }
    }
}

/**
 * 加载所有分类的图片（包括被ban的类别，用于显示模糊效果）
 */
async function loadAllCategories() {
    // 获取所有类别（包括被ban的）
    const allCategoryKeys = Object.keys(CATEGORY_CONFIG);

    // 并行加载所有分类（包括被ban的）
    const promises = allCategoryKeys.map(category => loadCategoryImages(category));
    await Promise.all(promises);
}

