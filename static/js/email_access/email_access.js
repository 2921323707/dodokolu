// 随机加载背景图片（与 login.js 保持一致）
function loadRandomBackground() {
    // 背景图片（login_back_x.jpg格式，与注册页面一致）
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

// 获取验证码
let countdownTimer = null;
let countdownSeconds = 60;

async function getVerificationCode() {
    const getCodeBtn = document.querySelector('#getCodeBtn');
    const pendingRegister = sessionStorage.getItem('pendingRegister');
    const pendingData = pendingRegister ? JSON.parse(pendingRegister) : null;

    // 从sessionStorage获取邮箱
    if (!pendingData || !pendingData.email) {
        alert('Email not found. Please register again.');
        window.location.href = '/register';
        return;
    }
    const email = pendingData.email.trim();

    // 禁用按钮并开始倒计时
    getCodeBtn.disabled = true;
    countdownSeconds = 60;

    function updateCountdown() {
        if (countdownSeconds > 0) {
            getCodeBtn.textContent = `${countdownSeconds}s`;
            getCodeBtn.classList.add('countdown');
            countdownSeconds--;
            countdownTimer = setTimeout(updateCountdown, 1000);
        } else {
            getCodeBtn.disabled = false;
            getCodeBtn.textContent = 'Get Code';
            getCodeBtn.classList.remove('countdown');
        }
    }

    try {
        // 发送请求获取验证码
        const response = await fetch('/api/send-verification-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert('Verification code has been sent to your email');
            updateCountdown(); // 开始倒计时
        } else {
            alert(data.message || 'Failed to send verification code');
            getCodeBtn.disabled = false;
            getCodeBtn.textContent = 'Get Code';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to send verification code. Please try again.');
        getCodeBtn.disabled = false;
        getCodeBtn.textContent = 'Get Code';
    }
}

// 验证验证码
async function verifyCode() {
    const codeInput = document.querySelector('#verificationCodeInput');
    const code = codeInput.value.trim();
    const pendingRegister = sessionStorage.getItem('pendingRegister');
    const pendingData = pendingRegister ? JSON.parse(pendingRegister) : null;

    // 从sessionStorage获取邮箱
    if (!pendingData || !pendingData.email) {
        alert('Email not found. Please register again.');
        window.location.href = '/register';
        return;
    }
    const email = pendingData.email.trim();

    if (!code) {
        alert('Please enter the verification code');
        return;
    }

    try {
        const response = await fetch('/api/verify-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email, code: code })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 如果有待注册信息，则完成注册写库
            if (pendingData) {
                const registerResp = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: pendingData.username,
                        email: pendingData.email,
                        password: pendingData.password
                    })
                });
                const registerData = await registerResp.json();

                if (registerResp.ok && registerData.success) {
                    alert('Verification successful! Registration completed, please login.');
                    sessionStorage.removeItem('pendingRegister');
                    window.location.href = '/login';
                } else {
                    alert(registerData.message || 'Registration failed after verification.');
                }
            } else {
                alert('Verification successful! Redirecting to login page...');
                window.location.href = '/login';
            }
        } else {
            alert(data.message || 'Verification failed. Please check your code.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Verification failed. Please try again.');
    }
}

