// 获取 URL 参数
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        image: params.get('image'),
        name: params.get('name') || '未命名图片',
        category: params.get('category') || '',
        index: params.get('index') || ''
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

    // 显示加载动画
    loadingSpinner.classList.add('active');

    // 加载图片
    imageElement.src = params.image;
    
    // 图片加载完成
    imageElement.onload = function() {
        loadingSpinner.classList.remove('active');
        imageElement.style.opacity = '1';
    };

    // 图片加载失败
    imageElement.onerror = function() {
        loadingSpinner.classList.remove('active');
        imageElement.alt = '图片加载失败';
        imageElement.classList.add('error');
        console.error('图片加载失败:', params.image);
    };

    // 双击放大/缩小
    let isZoomed = false;
    imageElement.addEventListener('dblclick', function() {
        if (isZoomed) {
            imageElement.classList.remove('zoomed');
            isZoomed = false;
        } else {
            imageElement.classList.add('zoomed');
            isZoomed = true;
        }
    });

    // 鼠标滚轮缩放
    imageElement.addEventListener('wheel', function(e) {
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
document.addEventListener('keydown', function(e) {
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
document.addEventListener('DOMContentLoaded', function() {
    initPage();
});

