document.addEventListener("DOMContentLoaded", function () {
    const rewards = window.monthlyRewards || {};
    //const reaction = window.monthlyReactions || {};
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
    document.getElementById('sweetsTotal').textContent = `🍩 おかし：${reward.sweets}こ`;

    //    const reaction = reactions[currentMonth] ||{
    //        heart: 0,
    //        smile: 0,
    //        good: 0,
    //        flower: 0,
    //        nice: 0,

    //};

    //document.getElementById('heartTotal').textContent = `💗 ：${reaction.heart}`;
    //document.getElementById('smileTotal').textContent = `😊 ：${reaction.smile}`;
    //document.getElementById('goodTotal').textContent = `👍 ：${reaction.good}`;
    //document.getElementById('flowerTotal').textContent = `🌸 ：${reaction.flower}`;
    //document.getElementById('niceTotal').textContent = `😎 ：${reaction.nice}`;
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

// モーダルウインドウについて　
// モーダル要素を取得
var modal = document.getElementById("myModal");
// モーダルを開くボタンを取得
var btn = document.getElementById("openModal");
// モーダルを閉じるアイコン（×）を取得
var span = document.getElementById("closeModal");

// ボタンがクリックされた時にモーダルを表示
btn.onclick = function() {
    modal.style.display = "block"; // モーダルのdisplayスタイルを"block"にして表示
}

// ×（クローズアイコン）がクリックされた時にモーダルを非表示
span.onclick = function() {
    modal.style.display = "none"; // モーダルのdisplayスタイルを"none"にして非表示
}

// モーダルの外側がクリックされた時にモーダルを非表示
window.onclick = function(event) {
    // クリックされた箇所がモーダル自体（外側）であれば
    if (event.target == modal) {
        modal.style.display = "none"; // モーダルのdisplayスタイルを"none"にして非表示
    }
}

