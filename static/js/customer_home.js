/**
 * FLUXO DINÂMICO - CLIENTE
 * 1. Cliente preenche localizações e preferências
 * 2. Sistema recomenda condutor (pode rejeitar e pedir próximo)
 * 3. Cliente aceita e paga → ride criada com status='pending'
 * 4. Cliente aguarda aceita do driver
 * 5. Quando driver aceita (status='active'), pop-up "Ride Accepted"
 * 6. Quando driver conclui (status='finished'), pop-up desaparece
 */

let estimateData = {};
let recommendedDriver = null;
let rejectedDrivers = [];
let selectedPreferences = {};
let currentRideId = null;
let pollingInterval = null;
let rideStatusCheckInterval = null;
let driverTimeout = null;
let isTimeoutReject = false;
let hasPaid = false;
const MAX_PREFERENCES = 3;

// ========== PREFERÊNCIAS ==========
document.querySelectorAll('.pref-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const category = this.value;
        const select = document.querySelector(`select[name="${category}"]`);
        const checkedCount = document.querySelectorAll('.pref-checkbox:checked').length;

        if (this.checked) {
            if (checkedCount > MAX_PREFERENCES) {
                this.checked = false;
                alert(`You can only select up to ${MAX_PREFERENCES} preferences`);
            } else {
                select.disabled = false;
            }
        } else {
            select.disabled = true;
            select.value = '';
            delete selectedPreferences[category];
        }
    });
});

document.querySelectorAll('.pref-select').forEach(select => {
    select.addEventListener('change', function() {
        const category = this.name;
        if (this.value) {
            selectedPreferences[category] = this.value;
        } else {
            delete selectedPreferences[category];
        }
    });
});

// Calcular estimativa quando ambos os campos estiverem preenchidos
document.getElementById('pickup').addEventListener('change', tryEstimate);
document.getElementById('destination').addEventListener('change', tryEstimate);

function tryEstimate() {
    const pickup = document.getElementById('pickup').value.trim();
    const dest = document.getElementById('destination').value.trim();

    if (!pickup || !dest) return;

    const infoDiv = document.getElementById('estimate-info');
    const loadingDiv = document.getElementById('estimate-loading');
    const resultsDiv = document.getElementById('estimate-results');
    const prefDiv = document.getElementById('preferences-section');

    infoDiv.style.display = 'block';
    loadingDiv.style.display = 'flex';
    resultsDiv.style.display = 'none';
    prefDiv.style.display = 'none';

    fetch('/estimate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin: pickup, destination: dest })
    })
    .then(res => res.json())
    .then(data => {
        loadingDiv.style.display = 'none';

        if (data.success) {
            estimateData = data;
            document.getElementById('est-distance').textContent = data.formatted_distance;
            document.getElementById('est-time').textContent = data.formatted_duration;
            document.getElementById('est-price').textContent = data.amount;
            resultsDiv.style.display = 'block';
            prefDiv.style.display = 'block';
        } else {
            resultsDiv.innerHTML = '<p class="estimate-error">⚠️ Could not calculate route</p>';
            resultsDiv.style.display = 'block';
        }
    })
    .catch(() => {
        loadingDiv.style.display = 'none';
        resultsDiv.innerHTML = '<p class="estimate-error">⚠️ Connection error</p>';
        resultsDiv.style.display = 'block';
    });
}

function openPreferencesOrDriver() {
    const pickup = document.getElementById('pickup').value.trim();
    const dest = document.getElementById('destination').value.trim();

    if (!pickup || !dest) {
        alert('Please enter both pickup location and destination.');
        return;
    }

    if (!estimateData.distance) {
        alert('Please wait for the route estimate to load.');
        return;
    }

    // Se há preferências selecionadas, recomendar driver
    if (Object.keys(selectedPreferences).length > 0) {
        recommendDriver();
    } else {
        // Sem preferências, ir direto para pagamento
        openPayModal();
    }
}

// ========== FLUXO DINÂMICO: RECOMENDAÇÃO COM REJEIÇÃO ==========
function recommendDriver() {
    const pickup = document.getElementById('pickup').value.trim();
    const dest = document.getElementById('destination').value.trim();

    fetch('/recommend_driver', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            origin: pickup,
            destination: dest,
            preferences: selectedPreferences,
            rejected_drivers: rejectedDrivers  // ← ENVIAR DRIVERS REJEITADOS
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.driver) {
            recommendedDriver = data.driver;
            
            // Atualizar informações do driver
            document.getElementById('driver-name').textContent = data.driver.name;
            document.getElementById('driver-type').textContent = `Type: ${data.driver.driver_type}`;
            
            // Se não tem reviews, mostrar "Sem viagens realizadas"; senão, mostrar rating
            if (data.driver.has_reviews) {
                document.getElementById('driver-rating').textContent = `⭐ ${data.driver.rating}`;
            } else {
                document.getElementById('driver-rating').textContent = `🆕 Sem viagens realizadas`;
            }
            
            // Mostrar contador se há mais drivers
            if (data.available_drivers > 1) {
                const counter = document.getElementById('driver-counter');
                if (!counter) {
                    const newCounter = document.createElement('p');
                    newCounter.id = 'driver-counter';
                    newCounter.style.fontSize = '0.9em';
                    newCounter.style.color = '#666';
                    newCounter.textContent = `${data.available_drivers - 1} more drivers available`;
                    document.querySelector('.driver-info').appendChild(newCounter);
                } else {
                    counter.textContent = `${data.available_drivers - 1} more drivers available`;
                }
            }
            
            document.getElementById('driver-modal').style.display = 'flex';
        } else {
            alert('No more drivers available with your preferences');
            if (hasPaid) {
                alert('Since no more drivers are available, your ride is cancelled.');
                hasPaid = false;
                rejectedDrivers = [];
                currentRideId = null;
            } else {
                openPayModal();
            }
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error recommending driver');
    });
}

function acceptRecommendedDriver() {
    closeDriverModal();
    if (hasPaid) {
        submitPayment(null);
    } else {
        openPayModal();
    }
}

function rejectRecommendedDriver() {
    // Adicionar driver rejeitado à lista
    if (recommendedDriver) {
        rejectedDrivers.push(recommendedDriver.id);
    }
    
    closeDriverModal();
    
    // Pedir próximo driver
    recommendDriver();
}

function closeDriverModal() {
    document.getElementById('driver-modal').style.display = 'none';
}

function cancelDriverSelection() {
    closeDriverModal();
    hasPaid = false;
    rejectedDrivers = [];
}

function openPayModal() {
    const pickup = document.getElementById('pickup').value.trim();
    const dest = document.getElementById('destination').value.trim();

    if (!pickup || !dest) {
        alert('Please enter both pickup location and destination.');
        return;
    }

    if (!estimateData.distance) {
        alert('Please wait for the route estimate to load.');
        return;
    }

    // Preencher modal
    document.getElementById('modal-origin').textContent = pickup;
    document.getElementById('modal-dest').textContent = dest;
    document.getElementById('modal-dist').textContent = estimateData.formatted_distance;
    document.getElementById('modal-time').textContent = estimateData.formatted_duration;
    document.getElementById('modal-price').textContent = estimateData.amount;

    // Preencher campos hidden
    document.getElementById('h-origin').value = pickup;
    document.getElementById('h-destination').value = dest;
    document.getElementById('h-distance').value = estimateData.distance;
    document.getElementById('h-duration').value = estimateData.duration;
    document.getElementById('h-amount').value = estimateData.amount;

    document.getElementById('pay-modal').style.display = 'flex';
}

function submitPayment(event) {
    if (event) event.preventDefault();

    const formData = new FormData(document.getElementById('pay-form'));
    
    // Adicionar recommended_driver_id se houver
    if (recommendedDriver) {
        formData.append('recommended_driver_id', recommendedDriver.id);
    }

    fetch('/confirm_ride', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            currentRideId = data.ride_id;
            hasPaid = true;
            closePayModal();
            
            // Mostrar mensagem de sucesso
            showRidePendingMessage();
            
            // Iniciar polling para ver atualizações
            startPollingRideStatus();
        } else {
            alert('Error creating ride: ' + data.error);
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error processing payment');
    });

    return false;
}

function disableFormInputs() {
    document.getElementById('pickup').disabled = true;
    document.getElementById('destination').disabled = true;
    document.querySelectorAll('.pref-checkbox').forEach(cb => cb.disabled = true);
    document.querySelectorAll('.pref-select').forEach(sel => sel.disabled = true);
}

function enableFormInputs() {
    document.getElementById('pickup').disabled = false;
    document.getElementById('destination').disabled = false;
    document.querySelectorAll('.pref-checkbox').forEach(cb => cb.disabled = false);
    document.querySelectorAll('.pref-category').forEach(cat => {
        const cb = cat.querySelector('.pref-checkbox');
        const sel = cat.querySelector('.pref-select');
        if (cb && sel) {
            sel.disabled = !cb.checked;
        }
    });
}

function showRidePendingMessage() {
    disableFormInputs();
    const successDiv = document.createElement('div');
    successDiv.className = 'btn';
    successDiv.id = 'ride-pending-msg';
    successDiv.innerHTML = '⏳ Waiting for driver response...';
    
    successDiv.style.cursor = 'default';
    successDiv.style.marginTop = '20px'; // Afasta ligeiramente das preferências
    successDiv.style.marginBottom = '10px';

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn btn-reject';
    cancelBtn.id = 'cancel-ride-btn';
    cancelBtn.innerHTML = '❌ Cancel Ride';
    cancelBtn.style.marginTop = '10px';
    cancelBtn.style.width = '100%';
    cancelBtn.onclick = cancelCurrentRide;
    
    const btnRequest = document.getElementById('btn-request');
    if (btnRequest) {
        btnRequest.style.display = 'none';
        btnRequest.parentNode.insertBefore(successDiv, btnRequest.nextSibling);
        successDiv.parentNode.insertBefore(cancelBtn, successDiv.nextSibling);
    } else {
        document.body.insertBefore(successDiv, document.body.firstChild);
    }
    
    setTimeout(() => {
        const msg = document.getElementById('ride-pending-msg');
        if (msg) msg.style.opacity = '0.7';
    }, 5000);
}

function cancelCurrentRide() {
    if (!currentRideId) return;
    if (!confirm("Are you sure you want to cancel this ride?")) return;
    
    fetch('/cancel_ride', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ride_id: currentRideId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            clearInterval(rideStatusCheckInterval);
            if (driverTimeout) clearTimeout(driverTimeout);
            currentRideId = null;
            
            const msg = document.getElementById('ride-pending-msg') || document.getElementById('ride-accepted-msg');
            if (msg) msg.remove();
            
            const cancelBtn = document.getElementById('cancel-ride-btn');
            if (cancelBtn) cancelBtn.remove();
            
            const btnRequest = document.getElementById('btn-request');
            if (btnRequest) btnRequest.style.display = 'block';
            
            enableFormInputs();
            hasPaid = false;
            rejectedDrivers = [];
        } else {
            alert('Could not cancel ride: ' + data.error);
        }
    })
    .catch(err => console.error('Error canceling ride:', err));
}

function startPollingRideStatus() {
    if (rideStatusCheckInterval) clearInterval(rideStatusCheckInterval);
    if (driverTimeout) clearTimeout(driverTimeout);

    // Timeout de 2 minutos (120000 ms) para o condutor responder
    driverTimeout = setTimeout(() => {
        if (!currentRideId) return;
        
        isTimeoutReject = true;
        
        // Rejeitar viagem automaticamente (timeout)
        fetch('/reject_ride', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ride_id: currentRideId })
        })
        .then(() => console.log("Ride timed out and was rejected."))
        .catch(err => console.error("Timeout reject error:", err));
    }, 120000);

    // Polling a cada 2 segundos
    rideStatusCheckInterval = setInterval(() => {
        checkRideStatus();
    }, 2000);
}

function checkRideStatus() {
    if (!currentRideId) return;

    fetch(`/get_ride_status/${currentRideId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (!currentRideId) return; // Prevent inflight requests from acting after cancel
        
        if (data.success) {
            const status = data.ride.status;
            
            // Se a ride já não estiver pending, cancela o timeout
            if (status !== 'PENDING' && driverTimeout) {
                clearTimeout(driverTimeout);
                driverTimeout = null;
            }
            
            if (status === 'ACTIVE') {
                // 🎉 Viagem foi aceita pelo driver!
                
                const cancelBtn = document.getElementById('cancel-ride-btn');
                if (cancelBtn) cancelBtn.remove();
                
                // Atualizar mensagem
                const msg = document.getElementById('ride-pending-msg');
                if (msg) {
                    msg.id = 'ride-accepted-msg';
                    msg.innerHTML = '✅ Ride Accepted!<br>Wait for your driver…';
                    msg.style.opacity = '1';
                }
            } else if (status === 'FINISHED') {
                // Viagem foi concluída!
                clearInterval(rideStatusCheckInterval);
                currentRideId = null;
                
                // Limpar form
                document.getElementById('ride-form').reset();
                const payForm = document.getElementById('pay-form');
                if (payForm) payForm.reset();
                
                document.querySelectorAll('.pref-checkbox').forEach(cb => cb.checked = false);
                document.querySelectorAll('.pref-select').forEach(s => { s.disabled = true; s.value = ''; });
                selectedPreferences = {};
                estimateData = {};
                hasPaid = false;
                
                // Mostrar mensagem de sucesso final e abrir modal de rating
                const msg = document.getElementById('ride-pending-msg') || document.getElementById('ride-accepted-msg');
                if (msg) {
                    msg.innerHTML = '🏁 Ride Finished!';
                    msg.id = 'ride-finished-msg';
                    setTimeout(() => {
                        if (msg) msg.remove();
                        const cancelBtn = document.getElementById('cancel-ride-btn');
                        if (cancelBtn) cancelBtn.remove();
                        const btnRequest = document.getElementById('btn-request');
                        if (btnRequest) btnRequest.style.display = 'block';
                    }, 5000);
                } else {
                    const cancelBtn = document.getElementById('cancel-ride-btn');
                    if (cancelBtn) cancelBtn.remove();
                    const btnRequest = document.getElementById('btn-request');
                    if (btnRequest) btnRequest.style.display = 'block';
                }
                
                enableFormInputs();
                
                // Show rating modal
                setRating(0);
                document.getElementById('rate-driver-modal').style.display = 'flex';
                
            } else if (status === 'REJECTED') {
                // Driver rejected the ride
                clearInterval(rideStatusCheckInterval);
                currentRideId = null;
                
                const msg = document.getElementById('ride-pending-msg') || document.getElementById('ride-accepted-msg');
                if (msg) {
                    msg.remove();
                    const cancelBtn = document.getElementById('cancel-ride-btn');
                    if (cancelBtn) cancelBtn.remove();
                    const btnRequest = document.getElementById('btn-request');
                    if (btnRequest) btnRequest.style.display = 'block';
                }

                enableFormInputs();

                // Adicionar o condutor rejeitado à lista, se houver recommendedDriver
                if (recommendedDriver && !rejectedDrivers.includes(recommendedDriver.id)) {
                    rejectedDrivers.push(recommendedDriver.id);
                }
                
                // Configurar texto da janela de rejeição
                const title = document.getElementById('rejected-modal-title');
                const desc = document.getElementById('rejected-modal-desc');
                if (title && desc) {
                    if (isTimeoutReject) {
                        title.innerHTML = 'Timeout ⏳';
                        desc.innerHTML = 'Driver took too long to answer.';
                        isTimeoutReject = false; // reset
                    } else {
                        title.innerHTML = 'Driver Rejected ❌';
                        desc.innerHTML = 'The driver has rejected your request.';
                    }
                }
                
                // Mostrar a janela de rejected
                document.getElementById('driver-rejected-modal').style.display = 'flex';
                
                // Chamar o próximo driver após alguns segundos, ou imediatamente
                setTimeout(() => {
                    document.getElementById('driver-rejected-modal').style.display = 'none';
                    recommendDriver();
                }, 5000);
            }
        } else {
            console.error('Erro ao verificar status:', data.error);
            // Se houver erro recorrente, para o polling
            clearInterval(rideStatusCheckInterval);
        }
    })
    .catch(err => {
        console.error('Polling error:', err);
        clearInterval(rideStatusCheckInterval);
    });
}

function closePayModal() {
    document.getElementById('pay-modal').style.display = 'none';
}

function closeDriverRejectedModal() {
    document.getElementById('driver-rejected-modal').style.display = 'none';
}

function closeRateDriverModal() {
    document.getElementById('rate-driver-modal').style.display = 'none';
    recommendedDriver = null;
    rejectedDrivers = [];
}

function setRating(rating) {
    document.getElementById('driver-rating-value').value = rating;
    for (let i = 1; i <= 5; i++) {
        document.getElementById('star-' + i).innerText = i <= rating ? '★' : '☆';
        document.getElementById('star-' + i).style.color = i <= rating ? 'gold' : '#ccc';
    }
}

function submitRating() {
    const rating = document.getElementById('driver-rating-value').value;
    if (rating === "0") {
        alert("Please select a rating!");
        return;
    }
    
    // recommendedDriver should still have the id
    const driverId = recommendedDriver ? recommendedDriver.id : null;
    
    if (!driverId) {
        closeRateDriverModal();
        return;
    }

    fetch('/rate_driver', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ driver_id: driverId, rating: rating })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            closeRateDriverModal();
            alert("Thank you for your feedback!");
        } else {
            alert('Error submitting rating');
        }
    })
    .catch(err => {
        console.error('Error:', err);
    });
}

// Fechar modal ao clicar fora
document.getElementById('pay-modal').addEventListener('click', function(e) {
    if (e.target === this) closePayModal();
});

document.getElementById('driver-modal').addEventListener('click', function(e) {
    if (e.target === this) cancelDriverSelection();
});

// Auto-hide success message
setTimeout(() => {
    const msg = document.getElementById('success-msg');
    if (msg) msg.style.display = 'none';
}, 5000);
