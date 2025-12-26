// 反馈页面图片上传功能

let selectedImageFiles = []; // 改为数组，最多3张
const MAX_IMAGES = 3;

// 初始化图片上传功能
function initImageUpload() {
    const uploadInput = document.getElementById('feedbackImageUpload');
    const previewContainer = document.getElementById('imagePreviewContainer');

    if (!uploadInput || !previewContainer) return;

    // 监听文件选择
    uploadInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        
        // 检查总数是否超过限制
        if (selectedImageFiles.length + files.length > MAX_IMAGES) {
            showMessage(`最多只能上传 ${MAX_IMAGES} 张图片`, 'error', 800);
            uploadInput.value = '';
            return;
        }

        // 验证每个文件
        const validFiles = [];
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            // 验证文件类型
            if (!file.type.match('image/(jpeg|jpg|png)')) {
                showMessage(`第 ${i + 1} 张图片格式不正确，请上传 JPG 或 PNG 格式`, 'error');
                continue;
            }

            // 验证文件大小（限制为 5MB）
            if (file.size > 5 * 1024 * 1024) {
                showMessage(`第 ${i + 1} 张图片大小不能超过 5MB`, 'error');
                continue;
            }

            validFiles.push(file);
        }

        // 添加到已选图片数组
        selectedImageFiles = selectedImageFiles.concat(validFiles);
        
        // 更新预览
        updateImagePreview();
        
        // 清空输入框，以便可以再次选择相同的文件
        uploadInput.value = '';
    });
}

// 更新图片预览
function updateImagePreview() {
    const previewContainer = document.getElementById('imagePreviewContainer');
    if (!previewContainer) return;

    // 清空现有预览
    previewContainer.innerHTML = '';

    if (selectedImageFiles.length === 0) {
        previewContainer.style.display = 'none';
        return;
    }

    previewContainer.style.display = 'flex';
    previewContainer.className = 'image-preview-container';

    // 为每张图片创建预览
    selectedImageFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const previewItem = document.createElement('div');
            previewItem.className = 'image-preview-item';
            previewItem.dataset.index = index;

            const img = document.createElement('img');
            img.src = e.target.result;
            img.alt = '预览图片';
            img.className = 'preview-img';

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'remove-image-btn';
            removeBtn.textContent = '×';
            removeBtn.onclick = function() {
                removeImage(index);
            };

            previewItem.appendChild(img);
            previewItem.appendChild(removeBtn);
            previewContainer.appendChild(previewItem);
        };
        reader.readAsDataURL(file);
    });
}

// 移除指定索引的图片
function removeImage(index) {
    selectedImageFiles.splice(index, 1);
    updateImagePreview();
}

// 获取选中的图片文件数组
function getSelectedImageFiles() {
    return selectedImageFiles;
}

// 清除所有选中的图片
function clearSelectedImages() {
    selectedImageFiles = [];
    const uploadInput = document.getElementById('feedbackImageUpload');
    const previewContainer = document.getElementById('imagePreviewContainer');
    
    if (uploadInput) uploadInput.value = '';
    if (previewContainer) {
        previewContainer.innerHTML = '';
        previewContainer.style.display = 'none';
    }
}

