document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('recordModal');
  const modalContent = document.getElementById('modalContent');
  const closeBtn = document.querySelector('.close-modal');

  document.querySelectorAll('.achievement-mark').forEach(mark => {
    mark.addEventListener('click', (event) => {
      event.stopPropagation();
      const date = mark.getAttribute('data-date');

      fetch(`/app/records_by_date/?date=${date}`)
        .then(response => response.json())
        .then(data => {
            modalContent.innerHTML = '';
            if (data.records && data.records.length > 0) {
                modalContent.innerHTML = '';
                data.records.forEach(record => {
                  const item = document.createElement('p');
                  item.textContent = `${record.child_name}：${record.help_name}`;
                  modalContent.appendChild(item);
                });
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
