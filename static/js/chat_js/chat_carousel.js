// 轮播图功能

let carouselInterval = null;
let currentSlide = 0;

/**
 * 初始化轮播图
 */
function initCarousel() {
    const carousel = document.getElementById('bannerCarousel');
    if (!carousel) return;

    const slides = carousel.querySelectorAll('.carousel-slide');
    const indicators = carousel.querySelectorAll('.indicator');

    if (slides.length === 0) return;

    // 点击指示器切换幻灯片
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            goToSlide(index);
        });
    });

    // 启动自动轮播（每3秒切换一次）
    startCarousel();

    // 鼠标悬停时暂停轮播
    carousel.addEventListener('mouseenter', stopCarousel);
    carousel.addEventListener('mouseleave', startCarousel);
}

/**
 * 切换到指定幻灯片
 */
function goToSlide(index) {
    const carousel = document.getElementById('bannerCarousel');
    if (!carousel) return;

    const slides = carousel.querySelectorAll('.carousel-slide');
    const indicators = carousel.querySelectorAll('.indicator');

    if (index < 0 || index >= slides.length) return;

    // 移除所有活动状态
    slides.forEach(slide => slide.classList.remove('active'));
    indicators.forEach(indicator => indicator.classList.remove('active'));

    // 添加活动状态
    slides[index].classList.add('active');
    indicators[index].classList.add('active');

    currentSlide = index;
}

/**
 * 切换到下一张幻灯片
 */
function nextSlide() {
    const carousel = document.getElementById('bannerCarousel');
    if (!carousel) return;

    const slides = carousel.querySelectorAll('.carousel-slide');
    const nextIndex = (currentSlide + 1) % slides.length;
    goToSlide(nextIndex);
}

/**
 * 启动自动轮播
 */
function startCarousel() {
    stopCarousel(); // 先清除之前的定时器
    carouselInterval = setInterval(nextSlide, 3000);
}

/**
 * 停止自动轮播
 */
function stopCarousel() {
    if (carouselInterval) {
        clearInterval(carouselInterval);
        carouselInterval = null;
    }
}

// 页面加载完成后初始化轮播图
document.addEventListener('DOMContentLoaded', function () {
    initCarousel();
});

