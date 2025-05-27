document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.reaction-button');

    buttons.forEach(button => {
        button.addEventListener('click', function(event) {
            // クリックした要素
            const target = event.target;

            // data-reaction と data-record-id の取得
            const recordId = target.getAttribute('data-record-id');
            const reaction = target.getAttribute('data-reaction');

           
            if (!recordId || !reaction) {
                console.error("Record ID または Reaction が存在しません。");
                return;
            }

            fetch(addReactionUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    record_id: recordId,
                    reaction_image: reaction
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log("リアクション送信成功");
                } else {
                    console.error("送信失敗:", data.error);
                }
            })
            .catch(error => {
                console.error("Fetch error:", error);
            });
        });
    });
});
