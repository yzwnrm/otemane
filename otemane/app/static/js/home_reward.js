document.addEventListener("DOMContentLoaded", function () {
    const records = window.monthlyRecords || [];

    function showMonthlyModal(records) {
        const container = document.getElementById('helpRecordsContainer');
        container.innerHTML = '';

        const grouped = {};
        records.forEach(r => {
            if (!grouped[r.date]) grouped[r.date] = [];
            grouped[r.date].push(r);
        });

        for (const date in grouped) {
            const section = document.createElement('div');
            section.style.marginBottom = '20px';

            const dateTitle = document.createElement('h4');
            dateTitle.textContent = `${date}日`;
            section.appendChild(dateTitle);

            const recordList = document.createElement('div');
            recordList.style.display = 'flex';
            recordList.style.flexDirection = 'column';
            recordList.style.gap = '10px';

            grouped[date].forEach(record => {
                const row = document.createElement('div');
                row.style.display = 'flex';
                row.style.alignItems = 'center';
                row.style.gap = '20px';
                row.style.borderBottom = '1px solid #ccc';
                row.style.paddingBottom = '5px';

                const help = document.createElement('div');
                help.textContent = record.help;

                row.appendChild(help);

                // モーダル表示用
                record.reward.forEach(reward => {
                    const rewardDiv = document.createElement('div');
                    if (reward.type === 'おかね') {
                        rewardDiv.textContent = `${reward.prize}えん`;
                    } else if (reward.type === 'おかし') {
                        rewardDiv.textContent = `おかし1つ`;
                    } else {
                        rewardDiv.textContent = `${reward.type}：${reward.detail}`;
                    }
                    rewardDiv.classList.add("me-3");
                    row.appendChild(rewardDiv);
                });


                const reaction = document.createElement('div');
                reaction.textContent = record.reaction;

                row.appendChild(reaction);

                recordList.appendChild(row);
            });

            section.appendChild(recordList);
            container.appendChild(section);
        }

        document.getElementById('myModal').style.display = "block";
    }

    document.getElementById('openModal').addEventListener('click', function () {
        showMonthlyModal(records);
    });

    document.getElementById('closeModal').addEventListener('click', function () {
        document.getElementById('myModal').style.display = "none";
    });
});
