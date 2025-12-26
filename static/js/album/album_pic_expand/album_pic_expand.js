// 获取 URL 参数
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        image: params.get('image'),
        name: params.get('name') || '未命名图片',
        category: params.get('category') || '',
        index: params.get('index') || '',
        type: params.get('type') || ''  // 添加图片类型参数
    };
}

// 初始化页面
function initPage() {
    const params = getUrlParams();
    const imageElement = document.getElementById('expanded-image');
    const loadingSpinner = document.getElementById('loading-spinner');
    const imageName = document.getElementById('image-name');

    if (!params.image) {
        console.error('缺少图片参数');
        imageElement.alt = '图片加载失败';
        imageElement.classList.add('error');
        return;
    }

    // 设置图片名称
    imageName.textContent = params.name;

    // 如果是 abnormal 类型，显示前往视频页面的 GIF 按钮
    if (params.type === 'abnormal') {
        initMoviesGifButton();
    }

    // 显示加载动画
    loadingSpinner.classList.add('active');

    // 加载图片
    imageElement.src = params.image;

    // 图片加载完成
    imageElement.onload = function () {
        loadingSpinner.classList.remove('active');
        imageElement.style.opacity = '1';
    };

    // 图片加载失败
    imageElement.onerror = function () {
        loadingSpinner.classList.remove('active');
        imageElement.alt = '图片加载失败';
        imageElement.classList.add('error');
        console.error('图片加载失败:', params.image);
    };

    // 双击放大/缩小
    let isZoomed = false;
    imageElement.addEventListener('dblclick', function () {
        if (isZoomed) {
            imageElement.classList.remove('zoomed');
            isZoomed = false;
        } else {
            imageElement.classList.add('zoomed');
            isZoomed = true;
        }
    });

    // 鼠标滚轮缩放
    imageElement.addEventListener('wheel', function (e) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        const currentScale = isZoomed ? 2 : 1;
        const newScale = Math.max(1, Math.min(3, currentScale + delta));

        if (newScale > 1) {
            imageElement.style.transform = `scale(${newScale})`;
            imageElement.classList.add('zoomed');
            isZoomed = true;
        } else {
            imageElement.style.transform = 'scale(1)';
            imageElement.classList.remove('zoomed');
            isZoomed = false;
        }
    });
}

// 初始化视频 GIF 按钮
function initMoviesGifButton() {
    const container = document.querySelector('.pic-expand-container');
    if (!container) return;

    // 创建 GIF 容器
    const gifContainer = document.createElement('div');
    gifContainer.className = 'movies-gif-container';

    // 创建 GIF 图片
    const gifImage = document.createElement('img');
    gifImage.src = '/static/imgs/gif/album_herf/herf_click.gif';
    gifImage.alt = '点击前往';
    gifImage.className = 'movies-gif-image';

    // 创建提示文字
    const hintText = document.createElement('div');
    hintText.className = 'movies-gif-hint';
    hintText.textContent = '忍不住了？';
    hintText.style.display = 'none'; // 初始隐藏

    // 点击状态管理
    let isFirstClick = true;

    // 点击事件处理
    gifContainer.addEventListener('click', function (e) {
        e.stopPropagation();

        if (isFirstClick) {
            // 第一次点击：显示提示文字
            isFirstClick = false;
            hintText.style.display = 'block';
            hintText.style.animation = 'fadeInUp 0.3s ease-out';
        } else {
            // 第二次点击：跳转到视频页面
            window.location.href = '/heaven/movies';
        }
    });

    // 组装元素（提示文字在上方，GIF 在下方）
    gifContainer.appendChild(hintText);
    gifContainer.appendChild(gifImage);
    container.appendChild(gifContainer);
}

// 返回上一页
function goBack() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        // 如果没有历史记录，跳转到相册首页
        const category = new URLSearchParams(window.location.search).get('category');
        if (category) {
            window.location.href = `/album?category=${encodeURIComponent(category)}`;
        } else {
            window.location.href = '/album';
        }
    }
}

// 键盘快捷键
document.addEventListener('keydown', function (e) {
    // ESC 键返回
    if (e.key === 'Escape') {
        goBack();
    }
    // 左右箭头键（后续可以用于切换图片）
    // if (e.key === 'ArrowLeft') {
    //     // 上一张图片
    // }
    // if (e.key === 'ArrowRight') {
    //     // 下一张图片
    // }
});

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    initPage();
});

