function toggleForm(id) {
    let form = document.getElementById("form-" + id);
    form.style.display = (form.style.display === "none") ? "block" : "none";
}

function toggleHire(id) {
    let form = document.getElementById("hire-form-" + id);
    form.style.display = (form.style.display === "none") ? "block" : "none";
}

function fireDriver(element, message) {
    if (!confirm(message)) return false;

    let row = element.closest("tr");

    row.style.transition = "0.3s";
    row.style.opacity = "0";
    row.style.transform = "translateX(50px)";

    setTimeout(() => row.remove(), 300);

    return true;
}
