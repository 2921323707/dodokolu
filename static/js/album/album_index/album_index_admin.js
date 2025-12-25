// 相册管理功能

let isAdmin = false;

// 初始化管理功能
document.addEventListener('DOMContentLoaded', async () => {
    await checkAdminStatus();
    initAdminFeatures();
});

/**
 * 检查用户是否为管理员
 */
async function checkAdminStatus() {
    try {
        const response = await fetch('/api/auth-status');
        const data = await response.json();
        
        if (data.logged_in && data.user && data.user.role === 2) {
            isAdmin = true;
            const footer = document.getElementById('albumFooter');
            if (footer) {
                footer.style.display = 'block';
            }
        } else {
            isAdmin = false;
            const footer = document.getElementById('albumFooter');
            if (footer) {
                footer.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('检查管理员状态失败:', error);
        isAdmin = false;
    }
}

/**
 * 初始化管理功能
 */
function initAdminFeatures() {
    const manageBtn = document.getElementById('adminManageBtn');
    const modal = document.getElementById('uploadModal');
    const closeBtn = document.getElementById('uploadModalClose');
    const cancelBtn = document.getElementById('uploadFormCancel');
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('uploadFile');
    const preview = document.getElementById('uploadPreview');
    const categorySelect = document.getElementById('uploadCategory');
    const folderTypeGroup = document.querySelector('.upload-form-group:nth-of-type(2)');

    // 根据分类显示/隐藏文件夹类型选项
    function toggleFolderTypeGroup() {
        if (categorySelect && folderTypeGroup) {
            const category = categorySelect.value;
            // 只有anime和photo才显示文件夹类型选项
            if (category === 'anime' || category === 'photo') {
                folderTypeGroup.style.display = 'block';
            } else {
                folderTypeGroup.style.display = 'none';
                // 重置为normal
                const normalRadio = document.querySelector('input[name="folderType"][value="normal"]');
                if (normalRadio) {
                    normalRadio.checked = true;
                }
            }
        }
    }

    // 监听分类选择变化
    if (categorySelect) {
        categorySelect.addEventListener('change', toggleFolderTypeGroup);
        // 初始化时也检查一次
        toggleFolderTypeGroup();
    }

    // 打开弹出框
    if (manageBtn) {
        manageBtn.addEventListener('click', () => {
            if (isAdmin && modal) {
                modal.classList.add('active');
            }
        });
    }

    // 关闭弹出框
    function closeModal() {
        if (modal) {
            modal.classList.remove('active');
            // 重置表单
            if (uploadForm) {
                uploadForm.reset();
            }
            if (preview) {
                preview.classList.remove('has-image');
                preview.innerHTML = '';
            }
            // 重置文件夹类型选项显示状态
            toggleFolderTypeGroup();
        }
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeModal);
    }

    // 点击遮罩关闭
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    // 文件选择预览
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    if (preview) {
                        preview.classList.add('has-image');
                        preview.innerHTML = `<img src="${event.target.result}" alt="预览">`;
                    }
                };
                reader.readAsDataURL(file);
            } else {
                if (preview) {
                    preview.classList.remove('has-image');
                    preview.innerHTML = '';
                }
            }
        });
    }

    // 表单提交
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!isAdmin) {
                alert('您没有管理员权限');
                return;
            }

            const category = document.getElementById('uploadCategory').value;
            // 只有anime和photo才需要folderType，其他分类默认为normal
            let folderType = 'normal';
            if (category === 'anime' || category === 'photo') {
                folderType = document.querySelector('input[name="folderType"]:checked')?.value || 'normal';
            }
            const source = document.getElementById('uploadSource').value.trim() || '0';
            const file = fileInput.files[0];

            if (!category) {
                alert('请选择分类');
                return;
            }

            if (!file) {
                alert('请选择图片');
                return;
            }

            // 创建FormData
            const formData = new FormData();
            formData.append('category', category);
            formData.append('folder_type', folderType);
            formData.append('source', source);
            formData.append('file', file);

            // 显示加载状态
            const submitBtn = uploadForm.querySelector('.upload-form-btn-submit');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = '上传中...';

            try {
                const response = await fetch('/album/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    alert('上传成功！');
                    closeModal();
                    // 重新加载对应分类的图片
                    if (typeof loadCategoryImages === 'function') {
                        loadCategoryImages(category);
                    }
                } else {
                    alert(data.message || '上传失败，请重试');
                }
            } catch (error) {
                console.error('上传错误:', error);
                alert('上传失败，请检查网络连接');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
}

// 定期检查管理员状态（用于处理登录状态变化）
setInterval(checkAdminStatus, 5000);

