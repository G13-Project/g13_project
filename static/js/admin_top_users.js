const metrics = {
    customers: ["rides", "distance", "amount"],
    drivers: ["rides", "distance", "amount", "contracts", "rating"],
    companies: ["drivers", "cars", "profit", "contracts", "rating"]
};

document.getElementById("groupSelect").addEventListener("change", function () {

    const group = this.value;
    const metricSelect = document.getElementById("metricSelect");

    metricSelect.innerHTML = `<option value="">Select metric...</option>`;

    if (!group) return;

    metrics[group].forEach(m => {
        metricSelect.innerHTML += `<option value="${m}">${m}</option>`;
    });

});

function formatValue(metric, value) {

    if(metric === "distance") return value + " km";
    if(metric === "amount" || metric === "profit") return value + " €";
    if(metric === "rating") return value.toFixed(2) + " ⭐";

    return value;
}

function confirmSelection() {

    const group = document.getElementById("groupSelect").value;
    const metric = document.getElementById("metricSelect").value;
    const podium = document.getElementById("podium");

    if (!group || !metric) {
        podium.innerHTML = "<p>Please select both options</p>";
        return;
    }

    podium.innerHTML = "<p>Loading...</p>";

    fetch(`/admin/get_top/${group}/${metric}`)
        .then(res => res.json())
        .then(data => {

            if (data.length < 3) {
                podium.innerHTML = "<p>No data</p>";
                return;
            }

            podium.innerHTML = `
            <div class="place silver">
                🥈
                <h3>${data[1].name}</h3>
                <p>${data[1].subtitle || ""}</p>
                <p>${formatValue(metric, data[1].value)}</p>
            </div>

            <div class="place gold">
                🥇
                <h3>${data[0].name}</h3>
                <p>${data[0].subtitle || ""}</p>
                <p>${formatValue(metric, data[0].value)}</p>
            </div>

            <div class="place bronze">
                🥉
                <h3>${data[2].name}</h3>
                <p>${data[2].subtitle || ""}</p>
                <p>${formatValue(metric, data[2].value)}</p>
            </div>
            `;
        });
}