document.addEventListener("DOMContentLoaded", function () {
    const allRecords = window.monthlyRecords || [];
    const selectedChild = (window.selectedChild || "").split('(')[0].trim();; 
    
    const targetGroup = allRecords.find(group => group.child === selectedChild);
    const records = targetGroup ? targetGroup.records : [];
    const modal = document.getElementById('myModal');

    function showMonthlyModal(records) {
        const container = document.getElementById('helpRecordsContainer');
        container.innerHTML = '';

        if (!Array.isArray(records) || records.length === 0) {
            container.textContent = 'まだお手伝いを達成できていません。';
            document.getElementById('myModal').style.display = "block";
            return;
        }

        records.sort((a, b) => new Date(a.date) - new Date(b.date));

          // テーブル作成
        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';

        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th style="border-bottom: 1px solid #ccc; padding: 8px; writing-mode: horizontal-tb; text-align: center; white-space: nowrap;">日付</th>
                <th style="border-bottom: 1px solid #ccc; padding: 8px; writing-mode: horizontal-tb; text-align: center; white-space: nowrap;">おてつだい</th>
                <th style="border-bottom: 1px solid #ccc; padding: 8px; writing-mode: horizontal-tb; text-align: center; white-space: nowrap;">報酬</th>
                <th style="border-bottom: 1px solid #ccc; padding: 8px; writing-mode: horizontal-tb; text-align: center; white-space: nowrap;">🥰</th>
            </tr>
        `;
        
        table.appendChild(thead);

        const tbody = document.createElement('tbody');

        records.forEach(record => {
            const row = document.createElement('tr');

            const dateTd = document.createElement('td');
            const dateObj = new Date(record.date);
            const formattedDate = `${dateObj.getMonth() + 1}/${dateObj.getDate()}`;
            dateTd.textContent = formattedDate;

            dateTd.style.padding = '8px';
            row.appendChild(dateTd);

            const helpTd = document.createElement('td');
            helpTd.textContent = record.help;
            helpTd.style.padding = '8px';
            helpTd.style.whiteSpace = 'nowrap';
            row.appendChild(helpTd);

            const rewardTd = document.createElement('td');
            rewardTd.style.padding = '8px';
            rewardTd.style.whiteSpace = 'nowrap';
            if (Array.isArray(record.reward)) {
                rewardTd.textContent = record.reward.map(reward => {
                    if (reward.type === 'おかね') {
                        return `${reward.prize}えん`;
                    } else if (reward.type === 'おかし') {
                        return 'おかし1';
                    } else {
                        return `${reward.detail}`;
                    }
                }).join(' / ');
            }
            row.appendChild(rewardTd);

            const reactionTd = document.createElement('td');
            reactionTd.style.padding = '8px';
            if (Array.isArray(record.reaction)) {
                reactionTd.textContent = record.reaction.join(' ');
            } else {
                reactionTd.textContent = record.reaction || '';
            }
            row.appendChild(reactionTd);

            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        container.appendChild(table);


    document.getElementById('myModal').style.display = "block";
}

    document.getElementById('openModal').addEventListener('click', function () {
        showMonthlyModal(records);
    });

    document.getElementById('closeModal').addEventListener('click', function () {
        document.getElementById('myModal').style.display = "none";
    });

    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});
