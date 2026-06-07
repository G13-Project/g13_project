/**
 * FLUXO DINÂMICO - DRIVER
 * 1. Driver vê ride recomendada (atribuída a ele com status='pending')
 * 2. Driver pode aceitar ou recusar
 * 3. Se aceita (status='active'), aparece botão Finish
 * 4. Se recusa, ride volta ao pool e outro driver pode pegar
 * 5. Quando cliente finaliza, ride some da página
 */

let recommendedRideData = null;
let pollingInterval = null;

// Carregar viagens ao abrir a página
document.addEventListener('DOMContentLoaded', function() {
    loadRides();
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

            // Mostrar viagem recomendada (atribuída ao driver)
            if (data.recommended_ride) {
                displayRecommendedRide(data.recommended_ride);
            } else {
                document.getElementById('recommended-section').style.display = 'none';
            }

            // Mostrar viagens pendentes (disponíveis para aceitar)
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
    document.getElementById('rec-distance').textContent = ride.formatted_distance;
    document.getElementById('rec-duration').textContent = ride.formatted_duration;
    document.getElementById('rec-amount').textContent = ride.amount;

    document.getElementById('recommended-section').style.display = 'block';

    // Mostrar botões Aceitar/Recusar se status é 'pending'
    const actionButtons = document.getElementById('recommended-section').querySelector('.ride-actions');
    const acceptBtn = actionButtons.querySelector('.btn-accept');
    const rejectBtn = actionButtons.querySelector('.btn-reject');
    const finishBtn = actionButtons.querySelector('.btn-finish');

    if (ride.status === 'PENDING') {
        // Mostrar botões de aceitar/recusar
        if (acceptBtn) acceptBtn.style.display = 'inline-block';
        if (rejectBtn) rejectBtn.style.display = 'inline-block';
        if (finishBtn) finishBtn.style.display = 'none';
    } else if (ride.status === 'ACTIVE') {
        // Mostrar apenas botão Finish
        if (acceptBtn) acceptBtn.style.display = 'none';
        if (rejectBtn) rejectBtn.style.display = 'none';
        if (finishBtn) finishBtn.style.display = 'inline-block';
    } else {
        // Status finished - esconder tudo
        document.getElementById('recommended-section').style.display = 'none';
    }
}

function displayPendingRides(rides) {
    const container = document.getElementById('pending-rides-container');

    if (!rides || rides.length === 0) {
        container.innerHTML = '<p class="empty-message">No rides available</p>';
        return;
    }

    container.innerHTML = rides.map(ride => `
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
                <span>📏 <strong>${ride.formatted_distance}</strong></span>
                <span>⏱️ <strong>${ride.formatted_duration}</strong></span>
                <span>💰 <strong>${ride.amount}</strong> €</span>
            </div>

            <div class="ride-actions">
                <button class="btn btn-accept" onclick="acceptPendingRide(${ride.id})">✅ Accept</button>
                <button class="btn btn-reject" onclick="rejectPendingRide(${ride.id})">❌ Reject</button>
            </div>
        </div>
    `).join('');
}

// ========== RECOMENDADA ==========
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
            loadRides();
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
            alert('❌ Ride rejected - returned to pool');
            loadRides();
        } else {
            alert('Error rejecting ride: ' + data.error);
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error rejecting ride');
    });
}

// ========== PENDENTES ==========
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
            loadRides();
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
            alert('❌ Ride rejected - returned to pool');
            loadRides();
        } else {
            alert('Error rejecting ride: ' + data.error);
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error rejecting ride');
    });
}

// ========== FINISH RIDE ==========
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
            const toast = document.createElement('div');
            toast.className = 'success-msg';
            toast.innerText = '🏁 Ride completed successfully!';
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 5000);

            loadRides();
        } else {
            alert("Error finishing ride: " + data.error);
        }
    })
    .catch(err => {
        console.error("Error:", err);
        alert("Error finishing ride");
    });
}
