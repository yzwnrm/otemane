document.addEventListener("DOMContentLoaded", function () {
    const rewards = window.monthlyRewards || {};
    let currentMonth = window.currentMonth; // "2025-04"

    function updateRewardDisplay() {
        const monthDate = new Date(currentMonth + '-01');
        const jpMonth = monthDate.getMonth() + 1;
        document.getElementById('monthTitle').textContent = `${jpMonth}月のごほうび`;

        const reward = rewards[currentMonth] || {
            money: 0,
            sweets: 0,
            heart: 0,
            smile: 0,
            good: 0,
            flower: 0,
            nice: 0,
        };

        document.getElementById('moneyTotal').textContent = `💰 おかね：${reward.money}えん`;
        document.getElementById('sweetsTotal').textContent = `🍩 おかし：${reward.sweets}こ`;

        document.getElementById('heartTotal').textContent = `💗 ${reward.heart}`;
        document.getElementById('smileTotal').textContent = `😊 ${reward.smile}`;
        document.getElementById('goodTotal').textContent = `👍 ${reward.good}`;
        document.getElementById('flowerTotal').textContent = `🌸 ${reward.flower}`;
        document.getElementById('niceTotal').textContent = `😎 ${reward.nice}`;
    }

    function changeMonth(offset) {
        const date = new Date(currentMonth + '-01');
        date.setMonth(date.getMonth() + offset);
        const y = date.getFullYear();
        const m = (date.getMonth() + 1).toString().padStart(2, '0');
        const newMonth = `${y}-${m}`;

        const url = new URL(window.location.href);
        url.searchParams.set('month', newMonth);

        window.location.href = url.toString(); // ページリロードしてデータ取り直す
    }

    document.getElementById('prevMonth').addEventListener('click', () => changeMonth(-1));
    document.getElementById('nextMonth').addEventListener('click', () => changeMonth(1));

    updateRewardDisplay();
});

var modal = document.getElementById("myModal");
var btn = document.getElementById("openModal");
var span = document.getElementById("closeModal");

btn.onclick = function () {
    modal.style.display = "block";
}
span.onclick = function () {
    modal.style.display = "none";
}
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
