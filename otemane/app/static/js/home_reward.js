document.addEventListener("DOMContentLoaded", function () {
    const allRecords = window.monthlyRecords || [];
    const selectedChild = (window.selectedChild || "").split('(')[0].trim();; 
    
    const targetGroup = allRecords.find(group => group.child === selectedChild);
    const records = targetGroup ? targetGroup.records : [];

    function showMonthlyModal(records) {
        const container = document.getElementById('helpRecordsContainer');
        container.innerHTML = '';

        if (!Array.isArray(records)) {
            container.textContent = '報酬の記録データがありません。';
            document.getElementById('myModal').style.display = "block";
            return;
        }

        records.sort((a, b) => new Date(a.date) - new Date(b.date));

        records.forEach(record => {
           const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.alignItems = 'center';
            row.style.gap = '20px';
            row.style.marginBottom = '8px';

        // 日付
            const dateDiv = document.createElement('div');
            dateDiv.textContent = record.date;
            row.appendChild(dateDiv);

        // おてつだい内容
        // if (!record.reward || record.reward.length === 0) {
            const helpDiv = document.createElement('div');
            helpDiv.textContent = record.help;
            row.appendChild(helpDiv);
        //    }

        // 報酬
            if (Array.isArray(record.reward)) {
                record.reward.forEach(reward => {
                    const rewardDiv = document.createElement('div');
                    if (reward.type === 'おかね') {
                        rewardDiv.textContent = `${reward.prize}えん`;
                    } else if (reward.type === 'おかし') {
                        rewardDiv.textContent = `おかし1`;
                    } else {
                        rewardDiv.textContent = `${reward.type}：${reward.detail}`;
                    }
                    row.appendChild(rewardDiv);
                });
    }

        // リアクション（絵文字）
            const reactionDiv = document.createElement('div');
            if (Array.isArray(record.reaction)) {
                reactionDiv.textContent = record.reaction.join(' ');
            } else {
                reactionDiv.textContent = record.reaction || '';
            }
            row.appendChild(reactionDiv);

            container.appendChild(row);
        });
        

    document.getElementById('myModal').style.display = "block";
}

    document.getElementById('openModal').addEventListener('click', function () {
        showMonthlyModal(records);
    });

    document.getElementById('closeModal').addEventListener('click', function () {
        document.getElementById('myModal').style.display = "none";
    });
});
