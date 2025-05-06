document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('generate-btn');
    const resultDiv = document.getElementById('result');

    button.addEventListener('click', () => {
        fetch('/app/invite/ajax/create/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.url) {
                const input = document.getElementById('invite-url');
                input.value = data.url;
            } else {
                resultDiv.textContent = 'エラーが発生しました。';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.textContent = '通信エラー';
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
