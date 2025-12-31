// 项目点赞功能
document.addEventListener('DOMContentLoaded', function () {
    const likeBtn = document.getElementById('projectLikeBtn');
    const likeCountEl = document.getElementById('projectLikeCount');
    
    if (!likeBtn || !likeCountEl) {
        return; // 如果元素不存在，直接返回
    }
    
    let isLiking = false; // 防止重复点击
    
    // 加载总点赞数
    async function loadLikeCount() {
        try {
            const response = await fetch('/api/account/project-likes/count');
            const data = await response.json();
            
            if (data.success) {
                likeCountEl.textContent = data.count || 0;
            }
        } catch (error) {
            console.error('加载点赞数失败:', error);
        }
    }
    
    // 处理点赞
    async function handleLike() {
        if (isLiking) {
            return; // 正在处理中，防止重复点击
        }
        
        isLiking = true;
        
        // 添加动画类
        likeBtn.classList.add('animating');
        
        try {
            const response = await fetch('/api/account/project-likes/like', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 更新点赞数
                likeCountEl.textContent = data.total_count || 0;
                
                // 添加已点赞样式
                likeBtn.classList.add('liked');
                
                // 显示提示（可选）
                // console.log('点赞成功！今日已点赞 ' + data.today_count + ' 次');
            } else {
                // 显示错误提示
                alert(data.message || '点赞失败');
                
                // 移除动画类（因为失败了）
                likeBtn.classList.remove('animating');
            }
        } catch (error) {
            console.error('点赞失败:', error);
            alert('点赞失败，请稍后重试');
            
            // 移除动画类
            likeBtn.classList.remove('animating');
        } finally {
            // 延迟移除动画类，让动画完成
            setTimeout(() => {
                likeBtn.classList.remove('animating');
                isLiking = false;
            }, 500);
        }
    }
    
    // 绑定点击事件
    likeBtn.addEventListener('click', handleLike);
    
    // 初始化：加载点赞数
    loadLikeCount();
});

