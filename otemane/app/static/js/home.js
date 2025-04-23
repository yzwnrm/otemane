document.addEventListener("DOMContentLoaded", function () {
    const rewards = window.monthlyRewards || {};
    let currentMonth = window.currentMonth; // "2025-04"

    function updateRewardDisplay() {
        const monthDate = new Date(currentMonth + '-01');
        const jpMonth = monthDate.getMonth() + 1;
        document.getElementById('monthTitle').textContent = `${jpMonth}月のごほうび`;

        const reward = rewards[currentMonth] ||{
            money: 0,
            sweets: 0
    };

    document.getElementById('moneyTotal').textContent = `💰 おかね：${reward.money}えん`;
    document.getElementById('snackTotal').textContent = `🍭 おかし：${reward.snack}こ`;
}    
        
    function changeMonth(offset) {
        const date = new Date(currentMonth + '-01');
        date.setMonth(date.getMonth() + offset);
        const y = date.getFullYear();
        const m = (date.getMonth() + 1).toString().padStart(2, '0');
        currentMonth = `${y}-${m}`;
        updateRewardDisplay();
    }

    document.getElementById('prevMonth').addEventListener('click', () => changeMonth(-1));
    document.getElementById('nextMonth').addEventListener('click', () => changeMonth(1));

    updateRewardDisplay();
});
