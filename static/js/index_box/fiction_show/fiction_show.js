// 小说阅读功能 JavaScript

// DOM 元素
const sidebarContent = document.getElementById('sidebarContent');
const readerHeader = document.getElementById('readerHeader');
const readerContent = document.getElementById('readerContent');
const articleTitle = document.getElementById('articleTitle');
const articleDate = document.getElementById('articleDate');
const articleWordCount = document.getElementById('articleWordCount');
const refreshBtn = document.getElementById('refreshBtn');

// 当前选中的文章
let currentArticle = null;
let fictionData = {};

// 初始化
document.addEventListener('DOMContentLoaded', function () {
    loadFictionList();
});

// 加载小说列表
async function loadFictionList() {
    try {
        // 显示加载状态
        sidebarContent.innerHTML = '<div class="loading-state"><p>加载中...</p></div>';
        
        // 添加加载动画到刷新按钮
        refreshBtn.classList.add('loading');
        
        // 请求数据
        const response = await fetch('/fiction/list');
        const result = await response.json();
        
        if (result.success) {
            fictionData = result.data || {};
            renderFictionList();
        } else {
            sidebarContent.innerHTML = `<div class="empty-state"><p>加载失败: ${result.error || '未知错误'}</p></div>`;
        }
    } catch (error) {
        console.error('加载小说列表失败:', error);
        sidebarContent.innerHTML = '<div class="empty-state"><p>加载失败，请稍后重试</p></div>';
    } finally {
        refreshBtn.classList.remove('loading');
    }
}

// 渲染小说列表
function renderFictionList() {
    if (!fictionData || Object.keys(fictionData).length === 0) {
        sidebarContent.innerHTML = '<div class="empty-state"><p>暂无文章</p></div>';
        return;
    }
    
    let html = '';
    
    // 按日期分组渲染（日期从新到旧）
    const dates = Object.keys(fictionData).sort((a, b) => b.localeCompare(a));
    
    dates.forEach(date => {
        const articles = fictionData[date];
        const dateFormatted = formatDate(date);
        
        html += `
            <div class="date-group">
                <div class="date-group-header" onclick="toggleDateGroup(this)">
                    <div>
                        <h3 class="date-group-title">${dateFormatted}</h3>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span class="date-group-count">${articles.length} 篇</span>
                        <svg class="date-group-toggle" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                    </div>
                </div>
                <div class="date-group-content">
        `;
        
        articles.forEach(article => {
            const isActive = currentArticle && 
                           currentArticle.date === article.date && 
                           currentArticle.filename === article.filename;
            
            html += `
                <div class="article-item ${isActive ? 'active' : ''}" 
                     onclick="loadArticle('${article.date}', '${escapeHtml(article.filename)}')">
                    <h4 class="article-item-title">${escapeHtml(article.title)}</h4>
                    <div class="article-item-meta">
                        <span>${formatTime(article.time)}</span>
                        <span class="article-item-word-count">${article.word_count || 0} 字</span>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    sidebarContent.innerHTML = html;
}

// 切换日期分组展开/折叠
function toggleDateGroup(header) {
    header.classList.toggle('collapsed');
}

// 加载文章内容
async function loadArticle(date, filename) {
    try {
        // 更新当前选中的文章
        currentArticle = { date, filename };
        
        // 更新列表中的选中状态
        renderFictionList();
        
        // 显示加载状态
        readerHeader.style.display = 'none';
        readerContent.innerHTML = '<div class="loading-content"><div class="loading-spinner"></div><p>加载中...</p></div>';
        
        // 请求文章内容
        const response = await fetch(`/fiction/article?date=${encodeURIComponent(date)}&filename=${encodeURIComponent(filename)}`);
        const result = await response.json();
        
        if (result.success) {
            const article = result.data;
            
            // 显示文章信息
            articleTitle.textContent = article.title || '无标题';
            articleDate.textContent = formatDateTime(article.time || '');
            articleWordCount.textContent = `${article.word_count || 0} 字`;
            
            // 显示文章内容
            const content = article.content || '';
            readerContent.innerHTML = `<div class="article-content">${formatContent(content)}</div>`;
            
            // 显示头部
            readerHeader.style.display = 'block';
            
            // 滚动到顶部
            readerContent.scrollTop = 0;
        } else {
            readerContent.innerHTML = `<div class="empty-state"><p>加载失败: ${result.error || '未知错误'}</p></div>`;
        }
    } catch (error) {
        console.error('加载文章失败:', error);
        readerContent.innerHTML = '<div class="empty-state"><p>加载失败，请稍后重试</p></div>';
    }
}

// 格式化内容（处理换行和段落）
function formatContent(content) {
    if (!content) return '';
    
    // 将内容按段落分割（双换行或单换行）
    const paragraphs = content.split(/\n\s*\n|\n/).filter(p => p.trim());
    
    // 为每个段落添加 <p> 标签
    return paragraphs.map(p => `<p>${escapeHtml(p.trim())}</p>`).join('');
}

// 转义 HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 格式化日期
function formatDate(dateStr) {
    try {
        const date = new Date(dateStr + 'T00:00:00');
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        
        // 判断是否是今天
        const today = new Date();
        if (date.toDateString() === today.toDateString()) {
            return '今天';
        }
        
        // 判断是否是昨天
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        if (date.toDateString() === yesterday.toDateString()) {
            return '昨天';
        }
        
        return `${year}年${month}月${day}日`;
    } catch (e) {
        return dateStr;
    }
}

// 格式化时间
function formatTime(timeStr) {
    if (!timeStr) return '';
    
    try {
        const time = timeStr.split(' ')[1] || '';
        if (time) {
            return time.substring(0, 5); // HH:MM
        }
        return '';
    } catch (e) {
        return timeStr;
    }
}

// 格式化日期时间
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '';
    
    try {
        const [date, time] = dateTimeStr.split(' ');
        const dateFormatted = formatDate(date);
        const timeFormatted = time ? time.substring(0, 5) : '';
        
        return timeFormatted ? `${dateFormatted} ${timeFormatted}` : dateFormatted;
    } catch (e) {
        return dateTimeStr;
    }
}

