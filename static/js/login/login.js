// 随机加载背景图片
function loadRandomBackground() {
    // 背景图片（login_back_x.jpg格式）
    const backgroundImages = [
        '/static/imgs/deco/login/login_back_1.jpg',
        '/static/imgs/deco/login/login_back_2.jpg'
    ];

    // 随机选择一张
    const randomIndex = Math.floor(Math.random() * backgroundImages.length);
    setBackgroundImage(backgroundImages[randomIndex]);
}

// 设置背景图片
function setBackgroundImage(imagePath) {
    document.body.style.backgroundImage = `url('${imagePath}')`;
    document.body.style.backgroundSize = 'cover';
    document.body.style.backgroundPosition = 'center';
    document.body.style.backgroundRepeat = 'no-repeat';
}

// 页面加载时设置随机背景
document.addEventListener('DOMContentLoaded', function () {
    loadRandomBackground();
});

// 忘记密码功能
function forgotman() {
    const modal = document.getElementById('forgotPasswordModal');
    if (modal) {
        modal.classList.add('active');
    }
    return false;
}

// 关闭忘记密码模态框
function closeForgotModal() {
    const modal = document.getElementById('forgotPasswordModal');
    if (modal) {
        modal.classList.remove('active');
        // 清空表单
        document.getElementById('changePasswordUsername').value = '';
        document.getElementById('changePasswordOld').value = '';
        document.getElementById('changePasswordNew').value = '';
        document.getElementById('changePasswordConfirm').value = '';
        const errorEl = document.getElementById('changePasswordError');
        if (errorEl) {
            errorEl.style.display = 'none';
            errorEl.textContent = '';
        }
    }
}

// 修改密码功能
function changePassword() {
    const username = document.getElementById('changePasswordUsername').value.trim();
    const oldPassword = document.getElementById('changePasswordOld').value.trim();
    const newPassword = document.getElementById('changePasswordNew').value.trim();
    const confirmPassword = document.getElementById('changePasswordConfirm').value.trim();
    const errorEl = document.getElementById('changePasswordError');

    // 隐藏错误信息
    if (errorEl) {
        errorEl.style.display = 'none';
        errorEl.textContent = '';
    }

    // 验证输入
    if (!username || !oldPassword || !newPassword || !confirmPassword) {
        if (errorEl) {
            errorEl.textContent = '请填写所有字段';
            errorEl.style.display = 'block';
        }
        return;
    }

    if (newPassword.length < 6) {
        if (errorEl) {
            errorEl.textContent = '新密码长度至少6位';
            errorEl.style.display = 'block';
        }
        return;
    }

    if (newPassword !== confirmPassword) {
        if (errorEl) {
            errorEl.textContent = '两次输入的密码不一致';
            errorEl.style.display = 'block';
        }
        return;
    }

    // 发送修改密码请求
    fetch('/api/account/change-password-by-username', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            old_password: oldPassword,
            new_password: newPassword
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('密码修改成功！');
            closeForgotModal();
        } else {
            if (errorEl) {
                errorEl.textContent = data.message || '密码修改失败';
                errorEl.style.display = 'block';
            }
        }
    })
    .catch(error => {
        console.error('修改密码错误:', error);
        if (errorEl) {
            errorEl.textContent = '密码修改失败，请稍后重试';
            errorEl.style.display = 'block';
        }
    });
}

// 点击模态框外部关闭
window.addEventListener('click', function(event) {
    const modal = document.getElementById('forgotPasswordModal');
    if (event.target === modal) {
        closeForgotModal();
    }
});

// 用户密码和配置
// Admin
const adminUser = "Admin";
const adminPass = "Pass";

// 登录功能
function loginBrungle() {
    var pass = document.querySelector('#passwordInput');
    var name = document.querySelector('#usernameInput');

    var passValue = pass.value.trim();
    var nameValue = name.value.trim();

    // 验证输入
    if (!nameValue || !passValue) {
        alert('请输入用户名和密码');
        return;
    }

    // 发送登录请求
    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: nameValue,
            password: passValue
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 登录成功，跳转到首页
            alert('登录成功！');
            // 记录登录状态
            if (data.user) {
                localStorage.setItem('userInfo', JSON.stringify(data.user));
            }
            window.location.href = '/';
        } else {
            // 登录失败，显示错误信息
            alert(data.message || '登录失败，请检查用户名和密码');
        }
    })
    .catch(error => {
        console.error('登录错误:', error);
        alert('登录失败，请稍后重试');
    });
}

// 注册功能（用于 register.html）
function registerBrungle() {
    var pass = document.querySelector('#passwordInput');
    var name = document.querySelector('#usernameInput');
    var email = document.querySelector('#emailInput');
    var confirmPass = document.querySelector('#confirmPasswordInput');

    if (!name || !pass || !confirmPass || !email) {
        alert('Please fill in all fields');
        return;
    }

    var passValue = pass.value;
    var nameValue = name.value;
    var emailValue = email.value;
    var confirmPassValue = confirmPass.value;

    if (!emailValue || emailValue.indexOf('@') === -1) {
        alert('Please enter a valid email');
        return;
    }

    if (passValue !== confirmPassValue) {
        alert('Passwords do not match');
        return;
    }

    if (passValue.length < 6) {
        alert('Password must be at least 6 characters long');
        return;
    }

    // 暂存注册信息到 sessionStorage，跳转到邮箱验证页
    const pending = {
        username: nameValue,
        email: emailValue,
        password: passValue
    };
    sessionStorage.setItem('pendingRegister', JSON.stringify(pending));
    window.location.href = '/email-verification';
}

