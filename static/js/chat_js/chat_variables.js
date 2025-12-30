// 全局变量和配置
function createSessionId() {
    return 'session_' + Date.now();
}

let sessionId = createSessionId();
let isStreaming = false;
// 模式状态：'normal'，默认为 'normal'
let currentMode = 'normal';

// 当前 session 的头像编号（1-5），每次创建新 session 时随机选择
let currentAvatarIndex = Math.floor(Math.random() * 5) + 1;

// 用户头像URL（全局变量）
let userAvatarUrl = null;

// 获取当前 session 的头像图片路径
function getAvatarImagePath() {
    return `/static/imgs/deco/chat_index/robot_profile/head/head_${currentAvatarIndex}.png`;
}

// 获取用户头像URL
async function getUserAvatarUrl() {
    if (userAvatarUrl) {
        return userAvatarUrl;
    }

    try {
        const response = await fetch('/api/user/avatar');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.has_avatar && data.avatar_url) {
                userAvatarUrl = data.avatar_url;
                return userAvatarUrl;
            }
        }
    } catch (error) {
        console.error('获取用户头像失败:', error);
    }
    return null;
}

// 创建 AI 头像元素（使用图片）
function createAIAvatarElement() {
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    const img = document.createElement('img');
    img.src = getAvatarImagePath();
    img.alt = 'AI';
    img.style.width = '100%';
    img.style.height = '100%';
    img.style.objectFit = 'cover';
    img.style.borderRadius = '50%';
    img.style.cursor = 'pointer';
    img.style.transition = 'transform 0.2s ease, opacity 0.2s ease';

    // 添加点击事件，打开AI信息模态框
    img.addEventListener('click', (e) => {
        e.stopPropagation();
        openAIInfoModal(getAvatarImagePath());
    });

    // 添加悬停效果
    img.addEventListener('mouseenter', () => {
        img.style.transform = 'scale(1.1)';
        img.style.opacity = '0.9';
    });

    img.addEventListener('mouseleave', () => {
        img.style.transform = 'scale(1)';
        img.style.opacity = '1';
    });

    avatar.appendChild(img);
    return avatar;
}

// 创建用户头像元素（使用图片或文本，可点击）
function createUserAvatarElement() {
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';

    if (userAvatarUrl) {
        // 如果有头像，使用图片
        const img = document.createElement('img');
        img.src = userAvatarUrl;
        img.alt = '我';
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '50%';
        img.style.cursor = 'pointer';
        img.style.transition = 'transform 0.2s ease, opacity 0.2s ease';

        // 添加点击事件，打开用户信息模态框
        img.addEventListener('click', (e) => {
            e.stopPropagation();
            openUserInfoModal();
        });

        // 添加悬停效果
        img.addEventListener('mouseenter', () => {
            img.style.transform = 'scale(1.1)';
            img.style.opacity = '0.9';
        });

        img.addEventListener('mouseleave', () => {
            img.style.transform = 'scale(1)';
            img.style.opacity = '1';
        });

        avatar.appendChild(img);
    } else {
        // 如果没有头像，使用文本
        avatar.textContent = '我';
        avatar.style.cursor = 'pointer';
        avatar.style.transition = 'transform 0.2s ease, opacity 0.2s ease';

        // 添加点击事件，打开用户信息模态框
        avatar.addEventListener('click', (e) => {
            e.stopPropagation();
            openUserInfoModal();
        });

        // 添加悬停效果
        avatar.addEventListener('mouseenter', () => {
            avatar.style.transform = 'scale(1.1)';
            avatar.style.opacity = '0.9';
        });

        avatar.addEventListener('mouseleave', () => {
            avatar.style.transform = 'scale(1)';
            avatar.style.opacity = '1';
        });
    }

    return avatar;
}

// 将模式值转换为显示文本
function getModeDisplayText(mode) {
    const modeMap = {
        'normal': '标准版'
    };
    return modeMap[mode] || mode;
}

