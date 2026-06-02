
    let estimateData = {};
    let recommendedDriver = null;
    let selectedPreferences = {};
    let currentRideId = null;
    let pollingInterval = null;
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
                document.getElementById('est-distance').textContent = data.distance;
                document.getElementById('est-time').textContent = data.duration;
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

    function recommendDriver() {
        const pickup = document.getElementById('pickup').value.trim();
        const dest = document.getElementById('destination').value.trim();

        fetch('/recommend_driver', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                origin: pickup,
                destination: dest,
                preferences: selectedPreferences
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.driver) {
                recommendedDriver = data.driver;
                document.getElementById('driver-name').textContent = data.driver.name;
                document.getElementById('driver-type').textContent = `Type: ${data.driver.driver_type}`;
                document.getElementById('driver-rating').textContent = `⭐ ${data.driver.rating}`;
                document.getElementById('driver-modal').style.display = 'flex';
            } else {
                alert('No drivers available with your preferences');
                openPayModal();
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Error recommending driver');
        });
    }

    function acceptRecommendedDriver() {
        closeDriverModal();
        openPayModal();
    }

    function rejectRecommendedDriver() {
        recommendedDriver = null;  // Limpar driver recomendado
        closeDriverModal();
        openPayModal();
    }

    function closeDriverModal() {
        document.getElementById('driver-modal').style.display = 'none';
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
        document.getElementById('modal-dist').textContent = estimateData.distance;
        document.getElementById('modal-time').textContent = estimateData.duration;
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
        event.preventDefault();

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

    function showRidePendingMessage() {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-msg';
        successDiv.id = 'ride-pending-msg';
        successDiv.innerHTML = '⏳ Waiting for driver response...';
        
        document.body.insertBefore(successDiv, document.body.firstChild);
        
        setTimeout(() => {
            const msg = document.getElementById('ride-pending-msg');
            if (msg) msg.style.opacity = '0.7';
        }, 3000);
    }

    function startPollingRideStatus() {
        // Polling a cada 2 segundos
        pollingInterval = setInterval(() => {
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
            if (data.success) {
                const status = data.ride.status;
                
                if (status === 'aceite') {
                    // Viagem foi aceita!
                    clearInterval(pollingInterval);
                    currentRideId = null;
                    
                    // Limpar form
                    document.getElementById('ride-form').reset();
                    document.querySelectorAll('.pref-checkbox').forEach(cb => cb.checked = false);
                    document.querySelectorAll('.pref-select').forEach(s => { s.disabled = true; s.value = ''; });
                    selectedPreferences = {};
                    recommendedDriver = null;
                    estimateData = {};
                    
                    // Mostrar mensagem de sucesso final
                    const msg = document.getElementById('ride-pending-msg');
                    if (msg) {
                        msg.innerHTML = '✅ Viagem aceite!';
                        msg.id = 'success-msg';
                        setTimeout(() => {
                            if (msg) msg.style.display = 'none';
                        }, 4000);
                    }
                }
            } else {
                console.error('Erro ao verificar status:', data.error);
                // Se houver erro recorrente, para o polling
                clearInterval(pollingInterval);
                alert('Erro ao atualizar viagem: ' + data.error);
            }
        })
        .catch(err => {
            console.error('Polling error:', err);
            clearInterval(pollingInterval);
        });
    }

    function closePayModal() {
        document.getElementById('pay-modal').style.display = 'none';
    }

    // Fechar modal ao clicar fora
    document.getElementById('pay-modal').addEventListener('click', function(e) {
        if (e.target === this) closePayModal();
    });

    document.getElementById('driver-modal').addEventListener('click', function(e) {
        if (e.target === this) closeDriverModal();
    });

    // Auto-hide success message
    setTimeout(() => {
        const msg = document.getElementById('success-msg');
        if (msg) msg.style.display = 'none';
    }, 4000);
