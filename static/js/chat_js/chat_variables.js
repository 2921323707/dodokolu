// 全局变量和配置
function createSessionId() {
    return 'session_' + Date.now();
}

let sessionId = createSessionId();
let isStreaming = false;
// 模式状态：'unnormal' 或 'normal'，默认为 'normal'
let currentMode = 'normal';

