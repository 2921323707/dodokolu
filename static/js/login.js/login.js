// 随机加载背景图片
function loadRandomBackground() {
    // 5张背景图片
    const backgroundImages = [
        '/static/login_back_imgs/bg1.jpg',
        // '/static/login_back_imgs/bg2.jpg',
        // '/static/login_back_imgs/bg3.jpg',
        // '/static/login_back_imgs/bg4.jpg',
        // '/static/login_back_imgs/bg5.jpg'
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
    alert('Please email ssnigdhasiraz22@sirhenryfloyd.co.uk to request a password reset');
}

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

