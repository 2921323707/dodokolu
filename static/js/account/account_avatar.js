// 头像相关功能
document.addEventListener('DOMContentLoaded', function () {
    const avatarImg = document.getElementById('accountAvatar');
    const avatarPlaceholder = document.getElementById('accountAvatarPlaceholder');
    const avatarInput = document.getElementById('accountAvatarInput');

    if (!avatarImg || !avatarPlaceholder || !avatarInput) return;

    // 加载用户头像
    async function loadUserAvatar() {
        try {
            const response = await fetch('/api/user/avatar');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.has_avatar && data.avatar_url) {
                    avatarImg.src = data.avatar_url;
                    avatarImg.style.display = 'block';
                    avatarPlaceholder.style.display = 'none';
                } else {
                    avatarImg.style.display = 'none';
                    avatarPlaceholder.style.display = 'flex';
                }
            }
        } catch (error) {
            console.error('获取头像失败:', error);
            avatarImg.style.display = 'none';
            avatarPlaceholder.style.display = 'flex';
        }
    }

    // 点击头像或占位符时触发文件选择
    avatarImg.addEventListener('click', () => {
        avatarInput.click();
    });

    avatarPlaceholder.addEventListener('click', () => {
        avatarInput.click();
    });

    // 处理头像上传
    async function handleAvatarUpload(event) {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        // 验证文件类型
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'];
        if (!allowedTypes.includes(file.type)) {
            alert('仅支持 PNG 或 JPG 格式的图片');
            event.target.value = '';
            return;
        }

        // 验证文件大小（限制为5MB）
        const maxSize = 5 * 1024 * 1024; // 5MB
        if (file.size > maxSize) {
            alert('图片大小不能超过 5MB');
            event.target.value = '';
            return;
        }

        // 创建 FormData
        const formData = new FormData();
        formData.append('avatar', file);

        try {
            const response = await fetch('/api/user/upload-avatar', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // 更新头像显示
                avatarImg.src = data.avatar_url + '?t=' + Date.now(); // 添加时间戳防止缓存
                avatarImg.style.display = 'block';
                avatarPlaceholder.style.display = 'none';
            } else {
                alert(data.message || '头像上传失败');
            }
        } catch (error) {
            console.error('上传头像失败:', error);
            alert('头像上传失败，请稍后重试');
        }

        // 清空文件选择，允许重复选择同一文件
        event.target.value = '';
    }

    // 绑定文件选择事件
    avatarInput.addEventListener('change', handleAvatarUpload);

    // 初始加载头像
    loadUserAvatar();
});

