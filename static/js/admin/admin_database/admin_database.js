// 数据库管理主文件 - 初始化
document.addEventListener('DOMContentLoaded', function () {
    // 确保所有模块已加载，然后初始化
    if (window.dbManager) {
        window.dbManager.init();
    }
});

