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

            const dateTitle = document.createElement('h3');
            dateTitle.textContent = `🗓️ ${date}`;
            section.appendChild(dateTitle);

            const recordRow = document.createElement('div');
            recordRow.style.display = 'flex';
            recordRow.style.flexWrap = 'wrap';
            recordRow.style.gap = '10px';

            grouped[date].forEach(record => {
                const card = document.createElement('div');
                card.style.border = '1px solid #ccc';
                card.style.padding = '10px';
                card.style.borderRadius = '8px';
                card.style.width = '200px';
                card.style.backgroundColor = '#f9f9f9';

                card.innerHTML = `
                    <p><strong>${record.help}</strong></p>
                    <p>報酬: ${record.reward}</p>
                    <p>リアクション: ${record.reaction}</p>
                `;
                recordRow.appendChild(card);
            });

            section.appendChild(recordRow);
            container.appendChild(section);
        }

        document.getElementById('myModal').style.display = "block";
    }

    document.getElementById('openModal').addEventListener('click', function() {
        showMonthlyModal(records);
    });

    document.getElementById('closeModal').addEventListener('click', function () {
        document.getElementById('myModal').style.display = "none";
    });
});
