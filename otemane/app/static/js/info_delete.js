document.addEventListener('DOMContentLoaded', function () {
  const deleteModal = document.getElementById('deleteModal');
  const deleteForm = document.getElementById('deleteForm');

  // モーダル表示時に action を設定
  deleteModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const deleteUrl = button.getAttribute('data-delete-url');
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
        // 行の削除（削除対象の行に data-child-id または data-user-id を指定しておく必要がある）
        const id = deleteUrl.split('/').filter(Boolean).pop(); // URLの末尾のIDを取得
        const row = document.querySelector(`[data-user-id="${id}"], [data-child-id="${id}"]`);
        if (row) row.remove();

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
