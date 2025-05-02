document.addEventListener("DOMContentLoaded", function () {
    const deleteModal = document.getElementById("deleteModal");
    const deleteForm = document.getElementById("deleteForm");
  
    if (deleteModal && deleteForm) {
      deleteModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const deleteUrl = button.getAttribute("data-delete-url");
        deleteForm.action = deleteUrl;
      });
    }
  });
  