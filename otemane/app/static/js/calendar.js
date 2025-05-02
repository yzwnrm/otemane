document.addEventListener("DOMContentLoaded", function () {
  const marks = document.querySelectorAll(".achievement-mark");
  
  if (marks.length === 0) {
    console.log("達成マークがページに存在しません。");
    return;
  }
  const modal = document.getElementById("recordModal");
  const modalContent = document.getElementById("modalContent");
  const closeButton = document.querySelector(".close-button");

  marks.forEach(mark => {
    mark.addEventListener("click", function () {
      const date = this.dataset.date;

      fetch(`/app/records_by_date/?date=${date}`)
        .then(response => response.json())
        .then(data => {
          modalContent.innerHTML = "";
          if (data.records.length === 0) {
            modalContent.innerHTML = "<p>記録がありません。</p>";
          } else {
            data.records.forEach(record => {
              const p = document.createElement("p");
              p.textContent = `${record.child}：${record.help}（${record.reward}）`;
              modalContent.appendChild(p);
            });
          }
          modal.style.display = "block";
        });
    });
  });

  closeButton.addEventListener("click", function () {
    modal.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  });
});



document.addEventListener('DOMContentLoaded', () => {
  const yearSelect = document.getElementById('year');
  const monthSelect = document.getElementById('month');
  const form = document.getElementById('monthSelectorForm');

  function autoSubmit() {
    if (yearSelect.value && monthSelect.value) {
      form.submit();
    }
  }

  yearSelect.addEventListener('change', autoSubmit);
  monthSelect.addEventListener('change', autoSubmit);
});
