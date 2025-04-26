document.addEventListener('DOMContentLoaded', function() {
    // 絵文字ボタンのクリックイベント
    document.querySelectorAll('.reaction-button').forEach(function(button) {
        button.addEventListener('click', function() {
            const recordId = button.getAttribute('data-record-id');
            const reactionImage = button.getAttribute('data-reaction');

            // AjaxでPOSTリクエストを送信
            fetch("{% url 'app:add_reaction' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    'record_id': recordId,
                    'reaction_image': reactionImage
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('リアクションが追加されました！');
                } else {
                    alert('エラーが発生しました');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('エラーが発生しました');
            });
        });
    });
});
