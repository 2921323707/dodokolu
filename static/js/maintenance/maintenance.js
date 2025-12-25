// 维护页面脚本 - 随机加载背景图片

document.addEventListener('DOMContentLoaded', function() {
    // 随机加载背景图片
    loadRandomBackground();
    
    // 初始化返回主页按钮
    initHomeButton();
});

/**
 * 随机加载背景图片（bg1.jpg, bg2.jpg, bg3.jpg）
 */
function loadRandomBackground() {
    const backgroundElement = document.getElementById('maintenanceBackground');
    if (!backgroundElement) return;

    // 生成随机数（1-3）
    const randomNum = Math.floor(Math.random() * 3) + 1;
    const imagePath = `/static/imgs/maintenance/bg${randomNum}.jpg`;

    // 创建新的图片对象预加载
    const img = new Image();
    img.onload = function() {
        // 图片加载成功后设置背景
        backgroundElement.style.backgroundImage = `url(${imagePath})`;
    };
    img.onerror = function() {
        // 如果图片加载失败，使用默认背景
        backgroundElement.style.backgroundImage = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    };
    img.src = imagePath;
}

/**
 * 初始化返回主页按钮
 */
function initHomeButton() {
    const homeButton = document.getElementById('homeButton');
    if (!homeButton) return;

    homeButton.addEventListener('click', function() {
        // 返回主页
        window.location.href = '/';
    });
}

