function loadWarnings() {

    const modal = document.getElementById("warningsModal");
    const text = document.getElementById("warningText");
    const list = document.getElementById("warningsList");

    modal.style.display = "flex";

    text.innerText = "Loading warnings...";
    list.innerHTML = "";

    fetch('/admin/get_warnings')
        .then(res => res.json())
        .then(data => {

            text.innerText = `⚠️ ${data.count} illegal rides detected`;

            let html = "";

            if (data.data.length === 0) {
                html = "<p>No illegal rides ✅</p>";
            } else {
                data.data.forEach(r => {
                    html += `
                        <p style="margin-bottom:10px;">
                            <strong>Driver ${r.driver_id}</strong><br>
                            Ride: ${r.ride_date}<br>
                            Contract: ${r.contract}
                        </p>
                    `;
                });
            }

            list.innerHTML = html;
        });
}

function closeWarnings(){
    document.getElementById("warningsModal").style.display="none";
}