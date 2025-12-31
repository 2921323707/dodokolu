// 智能体列表功能
document.addEventListener('DOMContentLoaded', function () {
    // 加载智能体列表
    async function loadAgentsList() {
        const agentsLoading = document.getElementById('agentsLoading');
        const agentsError = document.getElementById('agentsError');
        const agentsList = document.getElementById('agentsList');

        if (!agentsLoading || !agentsError || !agentsList) return;

        // 显示加载状态
        agentsLoading.style.display = 'block';
        agentsError.style.display = 'none';
        agentsList.style.display = 'none';

        try {
            const response = await fetch('/api/account/agents');
            const data = await response.json();

            if (data.success && data.agents) {
                // 生成智能体列表HTML
                const agentsHtml = data.agents.map(agent => {
                    const statusClass = agent.is_online ? 'online' : 'offline';
                    const statusIcon = agent.is_online ? '●' : '○';
                    return `
                        <div class="agent-card">
                            <div class="agent-header">
                                <h3 class="agent-name">${escapeHtml(agent.name)}</h3>
                                <span class="agent-status ${statusClass}">
                                    <span class="status-icon">${statusIcon}</span>
                                    <span class="status-text">${agent.status}</span>
                                </span>
                            </div>
                            <div class="agent-info">
                                <div class="agent-info-item">
                                    <span class="info-label">模型：</span>
                                    <span class="info-value">${escapeHtml(agent.model)}</span>
                                </div>
                                <div class="agent-info-item">
                                    <span class="info-label">描述：</span>
                                    <span class="info-value">${escapeHtml(agent.description)}</span>
                                </div>
                            </div>
                            <div class="agent-actions">
                                <p class="action-placeholder">功能待定义</p>
                            </div>
                        </div>
                    `;
                }).join('');

                agentsList.innerHTML = agentsHtml;
                agentsLoading.style.display = 'none';
                agentsList.style.display = 'grid';
            } else {
                throw new Error(data.message || '获取智能体列表失败');
            }
        } catch (error) {
            console.error('加载智能体列表失败:', error);
            agentsLoading.style.display = 'none';
            agentsError.textContent = error.message || '加载智能体列表失败，请稍后重试';
            agentsError.style.display = 'block';
        }
    }

    // 暴露给导航模块使用
    window.loadAgentsList = loadAgentsList;
});

