// Library Management Client Helpers
document.addEventListener('DOMContentLoaded', function () {
    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });

    // Form confirmation for destructive actions
    const deleteForms = document.querySelectorAll('form.confirm-action');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const message = form.getAttribute('data-confirm') || 'Bạn có chắc chắn muốn thực hiện thao tác này?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});
