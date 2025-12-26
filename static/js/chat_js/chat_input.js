// 输入框相关功能

// 全局变量：当前选中的图片
let currentImageFile = null;
let currentImageUrl = null;

// 处理键盘事件
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 初始化输入框（自动调整高度）
function initInput() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });
    }

    // 初始化图片上传功能
    const imageUpload = document.getElementById('imageUpload');
    if (imageUpload) {
        imageUpload.addEventListener('change', handleImageSelect);
    }
}

// 处理图片选择
function handleImageSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // 检查文件类型
    if (!file.type.startsWith('image/')) {
        alert('请选择图片文件');
        return;
    }

    // 一次只能上传一张图片，替换之前的图片
    currentImageFile = file;

    // 显示预览
    const reader = new FileReader();
    reader.onload = function (e) {
        currentImageUrl = e.target.result;
        const preview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');
        if (preview && previewImg) {
            previewImg.src = currentImageUrl;
            preview.style.display = 'block';
        }
    };
    reader.readAsDataURL(file);
}

// 移除图片
function removeImage() {
    currentImageFile = null;
    currentImageUrl = null;
    const preview = document.getElementById('imagePreview');
    const imageUpload = document.getElementById('imageUpload');
    if (preview) {
        preview.style.display = 'none';
    }
    if (imageUpload) {
        imageUpload.value = '';
    }
}

