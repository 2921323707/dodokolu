// 相册API调用

const API_BASE_URL = '/album/api/images';

/**
 * 获取可见的类别列表
 * @returns {Promise<Array>} 类别列表，包含category_key和display_name
 */
async function fetchVisibleCategories() {
    try {
        const response = await fetch('/album/api/categories');
        const data = await response.json();
        
        if (data.success) {
            return data.data || [];
        } else {
            console.error('获取类别列表失败:', data.message);
            return [];
        }
    } catch (error) {
        console.error('API请求失败:', error);
        return [];
    }
}

/**
 * 获取指定分类的图片列表
 * @param {string} category - 分类名称 (anime, wallpaper, photo, scene)
 * @returns {Promise<{images: Array, isVisible: boolean}>} 图片列表和可见性状态
 */
async function fetchCategoryImages(category) {
    try {
        const response = await fetch(`${API_BASE_URL}/${category}`);
        const data = await response.json();
        
        if (data.success) {
            return {
                images: data.data || [],
                isVisible: data.is_visible !== false  // 默认为true
            };
        } else {
            console.error('获取图片失败:', data.message);
            return {
                images: [],
                isVisible: true
            };
        }
    } catch (error) {
        console.error('API请求失败:', error);
        return {
            images: [],
            isVisible: true
        };
    }
}

