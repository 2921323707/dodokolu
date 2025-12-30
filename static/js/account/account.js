document.addEventListener('DOMContentLoaded', function () {
    const statusEl = document.getElementById('accountStatus');
    const infoEl = document.getElementById('accountInfo');
    const applyBtn = document.getElementById('applyCreatorBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const switchAdminBtn = document.getElementById('switchAdminBtn');

    // 侧边栏折叠功能
    const sidebar = document.getElementById('accountSidebar');
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');

    // 从本地存储读取折叠状态
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        sidebar.classList.add('collapsed');
    }

    sidebarToggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        const collapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', collapsed);
    });

    // 加载用户头像
    async function loadUserAvatar() {
        const avatarImg = document.getElementById('accountAvatar');
        const avatarPlaceholder = document.getElementById('accountAvatarPlaceholder');

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

    // 加载头像
    loadUserAvatar();

    // 头像上传功能
    const avatarImg = document.getElementById('accountAvatar');
    const avatarPlaceholder = document.getElementById('accountAvatarPlaceholder');
    const avatarInput = document.getElementById('accountAvatarInput');
    const avatarWrapper = document.getElementById('accountAvatarWrapper');

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
            event.target.value = ''; // 清空选择
            return;
        }

        // 验证文件大小（限制为5MB）
        const maxSize = 5 * 1024 * 1024; // 5MB
        if (file.size > maxSize) {
            alert('图片大小不能超过 5MB');
            event.target.value = ''; // 清空选择
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

    // 导航切换功能
    const navLinks = document.querySelectorAll('.sidebar-nav-link');
    const sections = document.querySelectorAll('.account-section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // 移除所有活动状态
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.style.display = 'none');

            // 添加当前活动状态
            link.classList.add('active');
            const sectionId = link.getAttribute('data-section');
            const targetSection = document.getElementById(`section-${sectionId}`);
            if (targetSection) {
                targetSection.style.display = 'block';
            }
        });
    });

    // 对话框相关元素
    const adminVerifyModal = document.getElementById('adminVerifyModal');
    const closeAdminVerifyModal = document.getElementById('closeAdminVerifyModal');
    const adminVerifyError = document.getElementById('adminVerifyError');
    const turnstileContainer = document.getElementById('turnstile-container');

    let turnstileWidgetId = null;
    let turnstileSiteKey = null;

    const labelMap = {
        username: '用户名',
        email: '邮箱'
    };

    function escapeHtml(raw) {
        return String(raw)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function renderProfile(profile) {
        // 只展示用户名和邮箱
        const orderedKeys = ['username', 'email'];
        infoEl.innerHTML = orderedKeys
            .filter(key => profile[key] !== undefined)
            .map(key => {
                const value = profile[key];
                const valueHtml = (value === null || value === undefined || value === '')
                    ? '<span class="placeholder">暂无</span>'
                    : escapeHtml(value);
                return `
                    <div class="info-item">
                        <p class="info-value">${valueHtml}</p>
                        <p class="info-label">${labelMap[key] || ''}</p>
                    </div>
                `;
            })
            .join('');
        infoEl.style.display = 'grid';
    }

    fetch('/api/account/profile')
        .then(res => {
            if (res.status === 401) {
                statusEl.textContent = '未登录，正在跳转...';
                setTimeout(() => window.location.href = '/login', 800);
                return null;
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;
            if (data.success) {
                statusEl.textContent = '已登录';
                renderProfile(data.data || {});
            } else {
                statusEl.textContent = data.message || '获取资料失败';
            }
        })
        .catch(() => {
            statusEl.textContent = '获取资料失败';
        });


    applyBtn.addEventListener('click', () => {
        const code = prompt('请输入邀请码，站主QQ:2921323707');
        if (!code) return;
        fetch('/api/account/apply-creator', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ invite_code: code.trim() })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message || '身份验证通过，身份已更新');
                } else {
                    alert(data.message || '申请失败');
                }
            })
            .catch(() => {
                alert('申请失败，请稍后重试');
            });
    });

    // 退出登录
    logoutBtn.addEventListener('click', () => {
        fetch('/api/account/logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    localStorage.removeItem('userInfo');
                    window.location.href = '/login';
                } else {
                    alert(data.message || '退出登录失败');
                }
            })
            .catch(() => {
                alert('退出登录失败，请稍后重试');
            });
    });

    // 获取 Turnstile site key
    fetch('/api/account/turnstile-site-key')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                turnstileSiteKey = data.site_key;
            } else {
                console.error('获取 Turnstile site key 失败:', data.message);
            }
        })
        .catch(err => {
            console.error('获取 Turnstile site key 错误:', err);
        });

    // 显示管理员验证对话框
    switchAdminBtn.addEventListener('click', () => {
        adminVerifyError.style.display = 'none';

        // 如果未配置 Turnstile，直接验证管理员身份（跳过人机验证）
        if (!turnstileSiteKey) {
            fetch('/api/account/verify-admin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        // 验证成功，跳转到管理员页面
                        window.location.href = '/admin';
                    } else {
                        alert(data.message || '管理员验证失败');
                    }
                })
                .catch(() => {
                    alert('验证失败，请稍后重试');
                });
            return;
        }

        // 配置了 Turnstile，显示验证对话框
        adminVerifyModal.style.display = 'flex';

        // 等待 Turnstile 脚本加载完成
        const initTurnstile = () => {
            if (typeof turnstile === 'undefined') {
                setTimeout(initTurnstile, 100);
                return;
            }

            // 清除之前的 widget
            if (turnstileWidgetId !== null) {
                turnstile.remove(turnstileWidgetId);
                turnstileWidgetId = null;
            }

            // 清空容器
            turnstileContainer.innerHTML = '';

            // 渲染 Turnstile
            turnstileWidgetId = turnstile.render(turnstileContainer, {
                sitekey: turnstileSiteKey,
                callback: (token) => {
                    // 验证通过，发送到后端验证
                    fetch('/api/account/verify-admin', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ turnstile_token: token })
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.success) {
                                // 验证成功，跳转到管理员页面
                                window.location.href = '/admin';
                            } else {
                                adminVerifyError.textContent = data.message || '管理员验证失败';
                                adminVerifyError.style.display = 'block';
                                // 重置 Turnstile
                                if (turnstileWidgetId !== null && typeof turnstile !== 'undefined') {
                                    turnstile.reset(turnstileWidgetId);
                                }
                            }
                        })
                        .catch(() => {
                            adminVerifyError.textContent = '验证失败，请稍后重试';
                            adminVerifyError.style.display = 'block';
                            // 重置 Turnstile
                            if (turnstileWidgetId !== null && typeof turnstile !== 'undefined') {
                                turnstile.reset(turnstileWidgetId);
                            }
                        });
                },
                'error-callback': (error) => {
                    console.error('Turnstile 错误:', error);
                    adminVerifyError.textContent = '人机验证失败，请重试';
                    adminVerifyError.style.display = 'block';
                },
                'expired-callback': () => {
                    adminVerifyError.textContent = '验证已过期，请重新验证';
                    adminVerifyError.style.display = 'block';
                }
            });
        };

        initTurnstile();
    });

    // 关闭管理员验证对话框
    const closeAdminVerifyModalFn = () => {
        adminVerifyModal.style.display = 'none';
        adminVerifyError.style.display = 'none';
        // 移除 Turnstile widget
        if (turnstileWidgetId !== null && typeof turnstile !== 'undefined') {
            turnstile.remove(turnstileWidgetId);
            turnstileWidgetId = null;
        }
        turnstileContainer.innerHTML = '';
    };
    closeAdminVerifyModal.addEventListener('click', closeAdminVerifyModalFn);

    // 点击对话框外部关闭
    adminVerifyModal.addEventListener('click', (e) => {
        if (e.target === adminVerifyModal) {
            closeAdminVerifyModalFn();
        }
    });
});
