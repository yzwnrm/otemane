document.addEventListener("DOMContentLoaded", function () {
    const choseLink = document.getElementById("nav-help-chose");
    const listsLink = document.getElementById("nav-help-lists");

    const selectedChild = window.selectedChildId;

    if (!selectedChild || selectedChild === 'all') {
        const showWarningAndRedirect = (e) => {
            e.preventDefault();
            alert("ホーム画面でメンバーを選択してください。");
            window.location.href = window.homeUrl;
        };

        console.log(window.selectedChildId);

        if (choseLink) {
            choseLink.addEventListener("click", showWarningAndRedirect);
        }
        if (listsLink) {
            listsLink.addEventListener("click", showWarningAndRedirect);
        }
    }
});
