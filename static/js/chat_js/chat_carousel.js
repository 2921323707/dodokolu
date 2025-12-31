// Banner 轮播图功能
(function () {
    'use strict';

    // 轮播图配置
    const CAROUSEL_CONFIG = {
        interval: 3000, // 3秒切换一次
        transitionDuration: 500 // 过渡动画时间（毫秒）
    };

    // 初始化轮播图
    function initCarousel() {
        const bannerElement = document.querySelector('.banner');
        if (!bannerElement) {
            return;
        }

        // 获取所有图片路径（从后端获取或直接使用已知路径）
        const imagePaths = getImagePaths();

        if (imagePaths.length === 0) {
            // 如果没有图片，保持原有样式
            return;
        }

        // 创建轮播图HTML结构
        const carouselHTML = createCarouselHTML(imagePaths);
        bannerElement.innerHTML = carouselHTML;

        // 初始化轮播逻辑
        const carouselContainer = bannerElement.querySelector('.banner-carousel');
        if (carouselContainer && imagePaths.length > 1) {
            startCarousel(carouselContainer, imagePaths.length);
        } else if (carouselContainer && imagePaths.length === 1) {
            // 只有一张图片时，直接显示（不显示指示点，不自动切换）
            const slide = carouselContainer.querySelector('.banner-carousel-slide');
            if (slide) {
                slide.classList.add('active');
            }
            // 移除指示点容器（如果存在）
            const dotsContainer = carouselContainer.querySelector('.banner-carousel-dots');
            if (dotsContainer) {
                dotsContainer.remove();
            }
        }
    }

    // 获取图片路径列表
    function getImagePaths() {
        const bannerElement = document.querySelector('.banner');
        if (!bannerElement) {
            return [];
        }

        // 从data属性获取图片路径
        if (bannerElement.dataset.images) {
            try {
                const images = JSON.parse(bannerElement.dataset.images);
                // 过滤掉空值
                return images.filter(img => img && img.trim() !== '');
            } catch (e) {
                console.error('Failed to parse images data:', e);
            }
        }

        // 如果没有data属性，返回空数组
        return [];
    }

    // 创建轮播图HTML结构
    function createCarouselHTML(imagePaths) {
        const slidesHTML = imagePaths.map((path, index) => {
            const activeClass = index === 0 ? 'active' : '';
            return `
                <div class="banner-carousel-slide ${activeClass}">
                    <img src="${path}" alt="Banner ${index + 1}" loading="lazy">
                </div>
            `;
        }).join('');

        const dotsHTML = imagePaths.length > 1 ? imagePaths.map((_, index) => {
            const activeClass = index === 0 ? 'active' : '';
            return `<button class="banner-carousel-dot ${activeClass}" data-index="${index}" aria-label="切换到第${index + 1}张"></button>`;
        }).join('') : '';

        return `
            <div class="banner-carousel">
                <div class="banner-carousel-slides">
                    ${slidesHTML}
                </div>
                ${dotsHTML ? `<div class="banner-carousel-dots">${dotsHTML}</div>` : ''}
            </div>
        `;
    }

    // 启动轮播
    function startCarousel(carouselContainer, totalSlides) {
        let currentIndex = 0;
        let carouselTimer = null;

        const slides = carouselContainer.querySelectorAll('.banner-carousel-slide');
        const dots = carouselContainer.querySelectorAll('.banner-carousel-dot');

        // 切换到指定索引的幻灯片
        function goToSlide(index) {
            // 移除所有活动状态
            slides.forEach(slide => slide.classList.remove('active'));
            dots.forEach(dot => dot.classList.remove('active'));

            // 添加活动状态
            if (slides[index]) {
                slides[index].classList.add('active');
            }
            if (dots[index]) {
                dots[index].classList.add('active');
            }

            currentIndex = index;
        }

        // 下一张
        function nextSlide() {
            const nextIndex = (currentIndex + 1) % totalSlides;
            goToSlide(nextIndex);
        }

        // 自动轮播
        function startAutoPlay() {
            if (carouselTimer) {
                clearInterval(carouselTimer);
            }
            carouselTimer = setInterval(nextSlide, CAROUSEL_CONFIG.interval);
        }

        // 停止自动轮播
        function stopAutoPlay() {
            if (carouselTimer) {
                clearInterval(carouselTimer);
                carouselTimer = null;
            }
        }

        // 点击指示点切换
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                goToSlide(index);
                stopAutoPlay();
                startAutoPlay(); // 重新开始自动播放
            });
        });

        // 鼠标悬停时暂停轮播
        carouselContainer.addEventListener('mouseenter', stopAutoPlay);
        carouselContainer.addEventListener('mouseleave', startAutoPlay);

        // 开始自动播放
        startAutoPlay();

        // 页面可见性变化时暂停/继续
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopAutoPlay();
            } else {
                startAutoPlay();
            }
        });
    }

    // DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCarousel);
    } else {
        initCarousel();
    }
})();
