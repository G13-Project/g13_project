function toggleDropdown() {
    var dropdown = document.getElementById("customSelectDropdown");
    if (dropdown.style.display === "none" || dropdown.style.display === "") {
        dropdown.style.display = "block";
    } else {
        dropdown.style.display = "none";
    }
}

function selectOption(value) {
    // Atualiza o select nativo invisível
    document.getElementById("nativeDriverType").value = value;
    // Atualiza o texto visível
    document.getElementById("customSelectText").innerText = value;
    // Esconde a lista
    document.getElementById("customSelectDropdown").style.display = "none";
}

// Fechar dropdown ao clicar fora
document.addEventListener("click", function(event) {
    var wrapper = document.querySelector(".custom-select-wrapper");
    if (wrapper && !wrapper.contains(event.target)) {
        var dropdown = document.getElementById("customSelectDropdown");
        if(dropdown) {
            dropdown.style.display = "none";
        }
    }
});
