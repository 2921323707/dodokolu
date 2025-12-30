document.addEventListener('DOMContentLoaded', function () {
    const statusEl = document.getElementById('accountStatus');
    const infoEl = document.getElementById('accountInfo');
    const applyBtn = document.getElementById('applyCreatorBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    const switchAdminBtn = document.getElementById('switchAdminBtn');
    
    // 对话框相关元素
    const changePasswordModal = document.getElementById('changePasswordModal');
    const adminVerifyModal = document.getElementById('adminVerifyModal');
    const closeChangePasswordModal = document.getElementById('closeChangePasswordModal');
    const closeAdminVerifyModal = document.getElementById('closeAdminVerifyModal');
    const cancelChangePassword = document.getElementById('cancelChangePassword');
    const confirmChangePassword = document.getElementById('confirmChangePassword');
    const oldPasswordInput = document.getElementById('oldPassword');
    const newPasswordInput = document.getElementById('newPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const changePasswordError = document.getElementById('changePasswordError');
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
        if (confirm('确定要退出登录吗？')) {
            fetch('/api/account/logout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        localStorage.removeItem('userInfo');
                        alert('已退出登录');
                        window.location.href = '/login';
                    } else {
                        alert(data.message || '退出登录失败');
                    }
                })
                .catch(() => {
                    alert('退出登录失败，请稍后重试');
                });
        }
    });

    // 显示修改密码对话框
    changePasswordBtn.addEventListener('click', () => {
        oldPasswordInput.value = '';
        newPasswordInput.value = '';
        confirmPasswordInput.value = '';
        changePasswordError.style.display = 'none';
        changePasswordModal.style.display = 'flex';
    });

    // 关闭修改密码对话框
    const closeChangePasswordModalFn = () => {
        changePasswordModal.style.display = 'none';
        oldPasswordInput.value = '';
        newPasswordInput.value = '';
        confirmPasswordInput.value = '';
        changePasswordError.style.display = 'none';
    };
    closeChangePasswordModal.addEventListener('click', closeChangePasswordModalFn);
    cancelChangePassword.addEventListener('click', closeChangePasswordModalFn);
    
    // 点击对话框外部关闭
    changePasswordModal.addEventListener('click', (e) => {
        if (e.target === changePasswordModal) {
            closeChangePasswordModalFn();
        }
    });

    // 确认修改密码
    confirmChangePassword.addEventListener('click', () => {
        const oldPassword = oldPasswordInput.value.trim();
        const newPassword = newPasswordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();

        changePasswordError.style.display = 'none';

        if (!oldPassword || !newPassword || !confirmPassword) {
            changePasswordError.textContent = '请填写所有字段';
            changePasswordError.style.display = 'block';
            return;
        }

        if (newPassword.length < 6) {
            changePasswordError.textContent = '新密码长度至少6位';
            changePasswordError.style.display = 'block';
            return;
        }

        if (newPassword !== confirmPassword) {
            changePasswordError.textContent = '两次输入的密码不一致';
            changePasswordError.style.display = 'block';
            return;
        }

        fetch('/api/account/change-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('密码修改成功');
                    closeChangePasswordModalFn();
                } else {
                    changePasswordError.textContent = data.message || '密码修改失败';
                    changePasswordError.style.display = 'block';
                }
            })
            .catch(() => {
                changePasswordError.textContent = '密码修改失败，请稍后重试';
                changePasswordError.style.display = 'block';
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
