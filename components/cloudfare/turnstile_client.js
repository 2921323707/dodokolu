// Cloudflare Turnstile 前端客户端脚本
// 需要在页面中引入: <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>

/**
 * 渲染 Turnstile 验证组件
 * @param {string} containerId - 容器元素的 ID
 * @param {string} siteKey - Cloudflare Turnstile 站点密钥
 * @param {function} callback - 验证成功后的回调函数，参数为 token
 * @returns {string} - widgetId，用于重置验证
 */
function renderTurnstile(containerId, siteKey, callback) {
    if (typeof turnstile === 'undefined') {
        console.error('Cloudflare Turnstile 脚本未加载');
        return null;
    }
    
    return turnstile.render(`#${containerId}`, {
        sitekey: siteKey,
        callback: callback,
        'error-callback': function(error) {
            console.error('Turnstile 验证错误:', error);
        },
        'expired-callback': function() {
            console.warn('Turnstile token 已过期');
        }
    });
}

/**
 * 重置 Turnstile 验证
 * @param {string} widgetId - widget ID
 */
function resetTurnstile(widgetId) {
    if (typeof turnstile !== 'undefined' && widgetId) {
        turnstile.reset(widgetId);
    }
}

/**
 * 移除 Turnstile 验证组件
 * @param {string} widgetId - widget ID
 */
function removeTurnstile(widgetId) {
    if (typeof turnstile !== 'undefined' && widgetId) {
        turnstile.remove(widgetId);
    }
}

