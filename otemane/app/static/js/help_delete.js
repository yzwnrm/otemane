document.addEventListener('DOMContentLoaded', function () {
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
      deleteModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const helpId = button.getAttribute('data-help-id');
        const form = deleteModal.querySelector('#deleteForm');
        form.action = `/otemane/help_delete/${helpId}/`;
      });
    }
  });
  