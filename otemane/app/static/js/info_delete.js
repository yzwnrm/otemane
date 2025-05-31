document.addEventListener('DOMContentLoaded', function () {
  const deleteModal = document.getElementById('deleteModal');
  const deleteForm = document.getElementById('deleteForm');
  let rowId = null;

  deleteModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const deleteUrl = button.getAttribute('data-delete-url');
    rowId = button.getAttribute('data-row-id');
    deleteForm.setAttribute('action', deleteUrl);
  });


  // 削除フォーム送信時の非同期リクエスト処理
  deleteForm.addEventListener('submit', function (e) {
    e.preventDefault();

    const deleteUrl = deleteForm.getAttribute('action');    
    const formData = new FormData(deleteForm);
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(deleteUrl, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrftoken,
      },
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        //const id = deleteUrl.split('/').filter(Boolean).pop(); 
        //const row = document.querySelector(`[data-user-id="${id}"], [data-child-id="${id}"]`);
        //if (row) row.remove();

        const row = document.querySelector(`[data-row-id="${rowId}"]`);
        if (row) row.remove();

        const modalInstance = bootstrap.Modal.getInstance(deleteModal);
        if (modalInstance) modalInstance.hide();


        const messageContainer = document.getElementById('message-container');
        if (messageContainer && data.message) {
          messageContainer.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
              ${data.message}
            </div>
          `;

          setTimeout(() => {
            messageContainer.innerHTML = '';
          }, 3000);
        }
        
      } else {
        alert('削除に失敗しました');
      }
    })
    .catch(error => {
      alert('削除に失敗しました');
    });
  });
});
