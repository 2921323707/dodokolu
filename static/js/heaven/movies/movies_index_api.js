// 视频列表 API 功能

/**
 * 获取视频列表
 */
async function fetchVideos() {
    try {
        const response = await fetch('/heaven/api/videos');
        const data = await response.json();

        if (data.success) {
            return data.data || [];
        } else {
            console.error('获取视频列表失败:', data.message);
            return [];
        }
    } catch (error) {
        console.error('获取视频列表出错:', error);
        return [];
    }
}

