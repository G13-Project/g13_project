let editing = false;

function toggleEdit() {

    editing = !editing;

    document.getElementById("usernameText").style.display = editing ? "none" : "inline";
    document.getElementById("usernameInput").style.display = editing ? "inline" : "none";
    document.getElementById("passwordBlock").style.display = editing ? "block" : "none";
    document.getElementById("saveBtn").style.display = editing ? "inline" : "none";
}

function openAbout() {
    document.getElementById("aboutModal").style.display = "flex";
}

function closeAbout() {
    document.getElementById("aboutModal").style.display = "none";
}

window.onclick = function(event) {
    let modal = document.getElementById("aboutModal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
}