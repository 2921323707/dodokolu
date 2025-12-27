// 全局变量和配置
function createSessionId() {
    return 'session_' + Date.now();
}

let sessionId = createSessionId();
let isStreaming = false;
// 模式状态：'unnormal' 或 'normal'，默认为 'normal'
let currentMode = 'normal';

// 当前 session 的头像编号（1-5），每次创建新 session 时随机选择
let currentAvatarIndex = Math.floor(Math.random() * 5) + 1;

// 获取当前 session 的头像图片路径
function getAvatarImagePath() {
    return `/static/imgs/deco/chat_index/robot_profile/head/head_${currentAvatarIndex}.png`;
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
    avatar.appendChild(img);
    return avatar;
}

// 将模式值转换为显示文本
function getModeDisplayText(mode) {
    const modeMap = {
        'normal': '标准版',
        'unnormal': '进阶版'
    };
    return modeMap[mode] || mode;
}

