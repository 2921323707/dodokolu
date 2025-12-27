// 全局变量和配置
function createSessionId() {
    return 'session_' + Date.now();
}

let sessionId = createSessionId();
let isStreaming = false;
// 模式状态：'unnormal' 或 'normal'，默认为 'normal'
let currentMode = 'normal';

// 将模式值转换为显示文本
function getModeDisplayText(mode) {
    const modeMap = {
        'normal': '标准版',
        'unnormal': '进阶版'
    };
    return modeMap[mode] || mode;
}

