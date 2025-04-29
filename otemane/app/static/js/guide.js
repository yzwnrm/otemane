document.addEventListener("DOMContentLoaded", function () {
    const openButtons = document.querySelectorAll(".open-modal");
    const closeButtons = document.querySelectorAll(".close-modal");

    openButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const modal = btn.closest("body").querySelector(btn.dataset.target);
            if (modal) modal.style.display = "block";
        });
    });

    closeButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const modal = btn.closest(".modal");
            modal.style.display = "none";
        });
    });

    window.addEventListener("click", function (event) {
        if (event.target.classList.contains("modal")) {
            event.target.style.display = "none";
        }
    });
});
