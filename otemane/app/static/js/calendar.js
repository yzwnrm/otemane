document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('recordModal');
  const modalContent = document.getElementById('modalContent');
  const closeBtn = document.querySelector('.close-modal');

  document.querySelectorAll('.achievement-mark').forEach(mark => {
    mark.addEventListener('click', (event) => {
      event.stopPropagation();
      const date = mark.getAttribute('data-date');

      fetch(`/otemane/records_by_date/?date=${date}`)
        .then(response => response.json())
        .then(data => {
            modalContent.innerHTML = '';
            if (data.records && data.records.length > 0) {
                modalContent.innerHTML = '';

                const table = document.createElement('table');
                table.style.width = '100%';
                table.style.borderCollapse = 'collapse';
                table.style.marginTop = '10px';

                // テーブルヘッダー
                const thead = document.createElement('thead');
                thead.innerHTML = `
                  <tr>
                    <th style="border-bottom: 1px solid #ccc; padding: 8px; text-align: center;">だれの？</th>
                    <th style="border-bottom: 1px solid #ccc; padding: 8px; text-align: center;">おてつだい</th>
                  </tr>
                  `;
                table.appendChild(thead);

// テーブル本文
                const tbody = document.createElement('tbody');
                data.records.forEach(record => {
                const row = document.createElement('tr');

                const childTd = document.createElement('td'); 
                childTd.textContent = record.child_name;
                childTd.style.padding = '8px';
                row.appendChild(childTd);

                const helpTd = document.createElement('td');
                helpTd.textContent = record.help_name;
                helpTd.style.padding = '8px';
                row.appendChild(helpTd);

                tbody.appendChild(row);
                });

                table.appendChild(tbody);
                modalContent.appendChild(table);

                //modalContent.innerHTML = '';
                //data.records.forEach(record => {
                //  const item = document.createElement('p');
                //  item.textContent = `${record.child_name}：${record.help_name}`;
                //  modalContent.appendChild(item);
                //});
            } else {
                modalContent.textContent = 'この日に達成されたおてつだいはありません。';
            }
            modal.style.display = 'block';
        })
        .catch(error => {
            console.error('Fetch error:', error);
            modalContent.textContent = 'データ取得に失敗しました。';
            modal.style.display = 'block'
        });
    });
  });
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      modal.style.display = 'none';
    });
  }
  window.addEventListener('click', (event) => {
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  });
});



document.addEventListener('DOMContentLoaded', () => {
  const yearSelect = document.getElementById('year');
  const monthSelect = document.getElementById('month');
  const form = document.getElementById('monthSelectorForm');

  if (yearSelect && monthSelect && form) {
    function autoSubmit() {
      if (yearSelect.value && monthSelect.value) {
        form.submit();
      }
    }

  yearSelect.addEventListener('change', autoSubmit);
  monthSelect.addEventListener('change', autoSubmit);
  }
});
