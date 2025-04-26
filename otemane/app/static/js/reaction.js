document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.reaction-button').forEach(function(button) {
        button.addEventListener('click', function() {
            const recordId = button.getAttribute('data-record-id');
            const reactionImage = button.getAttribute('data-reaction');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(addReactionUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded', 
                    'X-CSRFToken': csrfToken,
                },
                body: new URLSearchParams({  
                    'record_id': recordId,
                    'reaction_image': reactionImage,
                }),
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
