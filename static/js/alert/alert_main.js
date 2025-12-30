// 提醒页面主入口

// API 端点
const API_BASE = '/alert/api';

// 全局变量存储节日信息
let currentHoliday = null;
// 全局变量存储所有番剧数据
let allAnimesData = null;

// 初始化
document.addEventListener('DOMContentLoaded', function () {
    loadHolidays();
    loadComics();
    // 启动时间更新（每秒更新一次）
    updateHolidayTime();
    setInterval(updateHolidayTime, 1000);
    // 初始化画集展示框点击事件
    initGallerySection();
});

// 获取当前时间字符串（时:分:秒）
function getCurrentTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
}

// 更新节日显示的时间
function updateHolidayTime() {
    const holidayList = document.getElementById('holidayList');
    if (!holidayList || !currentHoliday) return;

    const timeLine = holidayList.querySelector('.holiday-date-line');
    if (timeLine) {
        timeLine.textContent = getCurrentTime();
    }
}

// 初始化画集展示框点击事件
function initGallerySection() {
    const gallerySection = document.querySelector('.gallery-section');
    if (gallerySection) {
        // 添加鼠标悬停样式
        gallerySection.style.cursor = 'pointer';

        // 添加点击事件
        gallerySection.addEventListener('click', function () {
            window.location.href = '/album/';
        });
    }
}

