// 地理位置工具模块

// 用户位置信息
let userLocation = null;

/**
 * 获取用户地理位置
 * @returns {Promise<{latitude: number, longitude: number} | null>}
 */
function getUserLocation() {
    return new Promise((resolve, reject) => {
        // 先从sessionStorage获取已保存的位置
        const savedLocation = sessionStorage.getItem('userLocation');
        if (savedLocation) {
            try {
                userLocation = JSON.parse(savedLocation);
                resolve(userLocation);
                return;
            } catch (e) {
                console.error('解析保存的位置信息失败:', e);
            }
        }

        // 检查浏览器是否支持地理位置API
        if (!navigator.geolocation) {
            console.warn('浏览器不支持地理位置API');
            resolve(null);
            return;
        }

        // 检查是否在安全上下文中（HTTPS 或 localhost）
        // 注意：即使不在安全上下文中，某些浏览器也可能支持，但会显示警告
        if (typeof window.isSecureContext !== 'undefined' && !window.isSecureContext) {
            console.warn('当前不在安全上下文中，地理位置功能可能受限');
            // 不直接返回，让浏览器自己决定是否允许
        }

        // 请求用户位置
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: Date.now()
                };
                // 保存到sessionStorage
                sessionStorage.setItem('userLocation', JSON.stringify(userLocation));
                resolve(userLocation);
            },
            (error) => {
                // 处理不同类型的错误
                // error.code: 1=PERMISSION_DENIED, 2=POSITION_UNAVAILABLE, 3=TIMEOUT
                let errorMessage = '获取地理位置失败';
                switch (error.code) {
                    case 1: // PERMISSION_DENIED
                        errorMessage = '用户拒绝了地理位置权限请求';
                        break;
                    case 2: // POSITION_UNAVAILABLE
                        errorMessage = '无法获取地理位置信息';
                        break;
                    case 3: // TIMEOUT
                        errorMessage = '获取地理位置超时';
                        break;
                    default:
                        errorMessage = `获取地理位置失败: ${error.message || '未知错误'}`;
                        break;
                }
                console.warn(errorMessage);
                // 不拒绝，而是返回null，允许继续使用
                resolve(null);
            },
            {
                enableHighAccuracy: false, // 不需要高精度，节省电量
                timeout: 10000, // 10秒超时
                maximumAge: 300000 // 5分钟内缓存有效
            }
        );
    });
}

/**
 * 初始化地理位置（在页面加载时调用）
 */
async function initLocation() {
    try {
        await getUserLocation();
        if (userLocation) {
            console.log('用户位置已获取:', userLocation);
        } else {
            console.log('未获取到用户位置（用户可能拒绝了权限）');
        }
    } catch (error) {
        console.error('初始化地理位置失败:', error);
    }
}

/**
 * 检查消息是否与天气相关
 * @param {string} message 
 * @returns {boolean}
 */
function isWeatherRelated(message) {
    const weatherKeywords = ['天气', '温度', '气温', '下雨', '晴天', '阴天', 'weather', 'temperature', 'rain', 'sunny'];
    const lowerMessage = message.toLowerCase();
    return weatherKeywords.some(keyword =>
        lowerMessage.includes(keyword.toLowerCase())
    );
}

/**
 * 获取位置信息字符串（用于传递给后端）
 * @returns {string | null}
 */
function getLocationContext() {
    if (userLocation) {
        return `用户当前位置：纬度 ${userLocation.latitude.toFixed(4)}, 经度 ${userLocation.longitude.toFixed(4)}`;
    }
    return null;
}

