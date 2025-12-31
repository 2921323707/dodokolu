// 管理员验证功能
document.addEventListener('DOMContentLoaded', function () {
    const switchAdminBtn = document.getElementById('switchAdminBtn');
    const adminVerifyModal = document.getElementById('adminVerifyModal');
    const closeAdminVerifyModal = document.getElementById('closeAdminVerifyModal');
    const adminVerifyError = document.getElementById('adminVerifyError');
    const turnstileContainer = document.getElementById('turnstile-container');

    if (!switchAdminBtn || !adminVerifyModal || !closeAdminVerifyModal || !adminVerifyError || !turnstileContainer) return;

    let turnstileWidgetId = null;
    let turnstileSiteKey = null;

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

