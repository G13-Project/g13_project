function limitCheckboxes(checkbox) {
    const max = 3;
    const checkboxes = document.querySelectorAll('input[name="prefs"]:checked');
    if (checkboxes.length > max) {
        checkbox.checked = false;
        alert("Só podes escolher até 3 preferências");
    }
}
