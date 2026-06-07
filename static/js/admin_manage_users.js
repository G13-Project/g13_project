function handleSearch(event) {
    if (event.key === "Enter") {
        let input = document.getElementById("searchInput").value.toLowerCase();
        let rows = document.querySelectorAll("#usersTable tr");

        for (let i = 1; i < rows.length; i++) {
            let user = rows[i].cells[0].innerText.toLowerCase();
            let role = rows[i].cells[1].innerText.toLowerCase();

            if (user === input || role === input) {
                rows[i].scrollIntoView({ behavior:"smooth", block:"center" });

                rows[i].style.backgroundColor = "#4FC3F7";
                setTimeout(() => rows[i].style.backgroundColor="", 2000);
                return;
            }
        }

        alert("Not found ❌");
    }
}


function openModal(data, user) {

    let html = "";

    if (data.group === "customer") {
        html = `👤 ${data.name}<br>📧 ${data.email}<br>📱 ${data.phone}<br>🎂 ${data.dob}`;
    }
    else if (data.group === "company") {
        html = `🏢 ${data.name}<br>📅 ${data.begin}<br>💰 Loading...`;

        fetch(`/admin/get_company_lucro/${user}`)
            .then(res => res.json())
            .then(res => {
                document.getElementById("modal-extra").innerHTML += `<br>💰 ${res.lucro} €`;
            });
    }
    else if (data.group === "driver") {
        html = `🚗 ${data.nickname}<br>🆔 ${data.type}<br>⭐ ${data.rating}`;
    }

    document.getElementById("modal-extra").innerHTML = html;
    document.getElementById("userModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("userModal").style.display = "none";
}


function openEditModal(data, user) {

    let form = "";
    document.getElementById("editForm").action = `/admin/edit_user/${user}`;

    if (data.group === "customer") {
        form = `
            <input name="name" value="${data.name}"><br><br>
            <input name="email" value="${data.email}"><br><br>
            <input name="phone" value="${data.phone}"><br><br>
            <input name="dob" value="${data.dob}"><br><br>
        `;
    }
    else if (data.group === "company") {
        form = `
            <input name="name" value="${data.name}"><br><br>
            <input name="begin" value="${data.begin}"><br><br>
        `;
    }
    else if (data.group === "driver") {
        form = `
            <input name="nickname" value="${data.nickname}"><br><br>
            <input name="type" value="${data.type}"><br><br>
        `;
    }

    document.getElementById("edit-fields").innerHTML = form;
    document.getElementById("editModal").style.display = "flex";
}

function closeEditModal() {
    document.getElementById("editModal").style.display = "none";
}


window.onload = function() {

    document.querySelectorAll(".btn-details").forEach(btn => {
        btn.addEventListener("click", () => {
            let data = JSON.parse(btn.dataset.details);
            openModal(data, btn.dataset.user);
        });
    });

    document.querySelectorAll(".btn-edit").forEach(btn => {
        btn.addEventListener("click", () => {
            let data = JSON.parse(btn.dataset.details);
            openEditModal(data, btn.dataset.user);
        });
    });
};
