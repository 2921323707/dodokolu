// 相册API调用

const API_BASE_URL = '/album/api/images';

/**
 * 获取指定分类的图片列表
 * @param {string} category - 分类名称 (anime, wallpaper, photo, scene)
 * @returns {Promise<Array>} 图片列表
 */
async function fetchCategoryImages(category) {
    try {
        const response = await fetch(`${API_BASE_URL}/${category}`);
        const data = await response.json();
        
        if (data.success) {
            return data.data || [];
        } else {
            console.error('获取图片失败:', data.message);
            return [];
        }
    } catch (error) {
        console.error('API请求失败:', error);
        return [];
    }
}

