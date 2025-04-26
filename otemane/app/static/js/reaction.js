document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.reaction-button').forEach(function(button) {
        button.addEventListener('click', function() {
            const recordId = button.getAttribute('data-record-id');
            const reactionImage = button.getAttribute('data-reaction');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch("/app/add_reaction/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                    record_id: recordId,
                    reaction_image: reactionImage
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("サーバーエラー");
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    console.log("リアクション送信成功");
                } else {
                    alert("リアクション失敗");
                }
            })
            .catch(error => {
                console.error("エラー:", error);
                alert("エラーが発生しました");
            });
        });
    });
});
