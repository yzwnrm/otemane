document.addEventListener("DOMContentLoaded", function () {
    const openButtons = document.querySelectorAll(".open-modal-2");
    const closeButtons = document.querySelectorAll(".close-modal");

    openButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const selector = btn.dataset.target;
            console.log("Opening modal with selector:", selector);  // デバッグ用
            const modal = document.querySelector(selector);
            if (modal) {
                modal.style.display = "block";
            } else {
                console.warn("Modal not found for selector:", selector);
            }
        });
    });

    closeButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const modal = btn.closest(".modal") || btn.closest(".modal-content")?.parentElement;
            if (modal) modal.style.display = "none";
        });
    });

    window.addEventListener("click", function (event) {
        if (event.target.classList.contains("modal")) {
            event.target.style.display = "none";
        }
    });
});