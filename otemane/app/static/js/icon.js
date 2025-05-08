document.addEventListener("DOMContentLoaded", function () {
    const icons = document.querySelectorAll(".icon-label");
    icons.forEach(icon => {
      icon.addEventListener("click", function () {
        icons.forEach(i => i.classList.remove("selected"));
        icon.classList.add("selected");
      });
    });
  });
  