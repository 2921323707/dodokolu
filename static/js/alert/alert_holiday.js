// 节日相关功能

// 加载节日数据
async function loadHolidays() {
    const holidayList = document.getElementById('holidayList');
    if (!holidayList) return;

    try {
        const response = await fetch(`${API_BASE}/holidays`);
        const result = await response.json();

        if (result.success && result.data && result.data.length > 0) {
            currentHoliday = result.data[0]; // 保存节日信息
            let secondLine = '';

            if (currentHoliday.days_until === 0) {
                // 如果是今天：显示节日名称
                secondLine = currentHoliday.name;
            } else {
                // 如果不是今天：显示距离还有xx天
                secondLine = `距离${currentHoliday.name}还有${currentHoliday.days_until}天`;
            }

            holidayList.innerHTML = `
                <div class="holiday-item-inline">
                    <div class="holiday-date-line">${getCurrentTime()}</div>
                    <div class="comic-update-date" id="comicDate"></div>
                    <div class="holiday-text-line">${secondLine}</div>
                </div>
            `;
        } else {
            currentHoliday = null;
            holidayList.innerHTML = `
                <div class="holiday-item-inline">
                    <div class="comic-update-date" id="comicDate"></div>
                </div>
            `;
        }
    } catch (error) {
        console.error('加载节日数据失败:', error);
        currentHoliday = null;
        holidayList.innerHTML = '<span class="holiday-item-inline">加载失败，请稍后重试</span>';
    }
}

