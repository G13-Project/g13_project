    let recommendedRideData = null;
    let pollingInterval = null;

    // Carregar viagens ao abrir a página
    document.addEventListener('DOMContentLoaded', function() {
        loadRides();
        
        // Iniciar polling a cada 3 segundos
        pollingInterval = setInterval(loadRides, 3000);
    });

    // Parar polling ao fechar a página
    window.addEventListener('beforeunload', function() {
        if (pollingInterval) clearInterval(pollingInterval);
    });

    function loadRides() {
        fetch('/get_driver_rides', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Mostrar viagem recomendada se existir
                if (data.recommended_ride) {
                    displayRecommendedRide(data.recommended_ride);
                } else {
                    // Se não há viagem recomendada, esconder a seção
                    document.getElementById('recommended-section').style.display = 'none';
                }

                // Mostrar viagens pendentes
                displayPendingRides(data.pending_rides);
            }
        })
        .catch(err => {
            console.error('Error loading rides:', err);
            document.getElementById('pending-rides-container').innerHTML = 
                '<p class="empty-message">Error loading rides</p>';
        });
    }

    function displayRecommendedRide(ride) {
        recommendedRideData = ride;

        document.getElementById('rec-customer').textContent = ride.customer_name || 'Unknown';
        document.getElementById('rec-origin').textContent = ride.origin;
        document.getElementById('rec-destination').textContent = ride.destination;
        document.getElementById('rec-distance').textContent = ride.distance;
        document.getElementById('rec-duration').textContent = ride.duration;
        document.getElementById('rec-amount').textContent = ride.amount;

        document.getElementById('recommended-section').style.display = 'block';
        if (ride.status === "aceite") {
            document.getElementById("finish-btn").style.display = "inline-block";
        } else {
            document.getElementById("finish-btn").style.display = "none";
        }

    }

    function displayPendingRides(rides) {
        const container = document.getElementById('pending-rides-container');

        if (!rides || rides.length === 0) {
            container.innerHTML = '<p class="empty-message">No rides available</p>';
            return;
        }

        container.innerHTML = rides.map((ride, index) => `
            <div class="ride-card pending-ride">
                <div class="ride-header">
                    <p class="customer-name">From <strong>${ride.customer_name || 'Unknown'}</strong></p>
                </div>
                
                <div class="ride-route">
                    <p>📍 ${ride.origin}</p>
                    <p>↓</p>
                    <p>🏁 ${ride.destination}</p>
                </div>

                <div class="ride-details">
                    <span>📏 <strong>${ride.distance}</strong> km</span>
                    <span>⏱️ <strong>${ride.duration}</strong> min</span>
                    <span>💰 <strong>${ride.amount}</strong> €</span>
                </div>

                <div class="ride-actions">
                    <button class="btn btn-accept" onclick="acceptPendingRide(${ride.id})">✅ Accept</button>
                    <button class="btn btn-reject" onclick="rejectPendingRide(${ride.id})">❌ Reject</button>
                </div>
            </div>
        `).join('');
    }

    function acceptRecommendedRide() {
        if (!recommendedRideData) return;

        fetch('/accept_ride', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ride_id: recommendedRideData.id })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('✅ Ride accepted!');
                loadRides(); // Recarregar imediatamente
            } else {
                alert('Error accepting ride: ' + data.error);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Error accepting ride');
        });
    }

    function rejectRecommendedRide() {
        if (!recommendedRideData) return;

        fetch('/reject_ride', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ride_id: recommendedRideData.id })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('❌ Ride rejected');
                loadRides(); // Recarregar imediatamente
            } else {
                alert('Error rejecting ride: ' + data.error);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Error rejecting ride');
        });
    }

    function acceptPendingRide(rideId) {
        fetch('/accept_ride', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ride_id: rideId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('✅ Ride accepted!');
                loadRides(); // Recarregar imediatamente
            } else {
                alert('Error accepting ride: ' + data.error);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Error accepting ride');
        });
    }

    function rejectPendingRide(rideId) {
        fetch('/reject_ride', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ride_id: rideId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('❌ Ride rejected');
                loadRides(); // Recarregar imediatamente
            } else {
                alert('Error rejecting ride: ' + data.error);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Error rejecting ride');
        });
    }
    function finishRide() {
    if (!recommendedRideData) return;

    fetch('/finish_ride', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ride_id: recommendedRideData.id })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("🏁 Viagem concluída!");
            loadRides(); // atualizar lista
        } else {
            alert("Erro ao concluir viagem: " + data.error);
        }
    })
    .catch(err => {
        console.error("Error:", err);
        alert("Erro ao concluir viagem");
    });
    }
