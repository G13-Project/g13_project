window.onload = function () {

    const details = document.getElementById("detailsBox");
    const form = document.getElementById("formBox");

    if (details) {
        details.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }

    if (form) {
        form.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }

};