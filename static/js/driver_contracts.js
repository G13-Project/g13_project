document.querySelectorAll('.btn-danger').forEach(btn => {
    btn.addEventListener('click', function(e) {
        if (!confirm("Are you sure you want to leave this company?")) {
            e.preventDefault();
        }
    });
});
