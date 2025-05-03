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

    fetch(deleteUrl, {
      method: 'POST',
      body: formData,
    })
    .then(response => {
      if (response.ok) {
        // 行の削除（削除対象の行に data-child-id または data-user-id を指定しておく必要がある）
        const id = deleteUrl.split('/').filter(Boolean).pop(); // URLの末尾のIDを取得
        const row = document.querySelector(`[data-user-id="${id}"], [data-child-id="${id}"]`);
        if (row) row.remove();

        // 成功後にリロードまたはリダイレクト
        window.location.href = window.location.href; // または指定URLにリダイレクト
      } else {
        alert('削除に失敗しました');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('削除に失敗しました');
    });
  });
});
