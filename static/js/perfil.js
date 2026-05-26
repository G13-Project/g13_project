// ============ LIMITADOR DE CHECKBOXES ============
function limitCheckboxes(checkbox) {
    const max = 3;
    const checkboxes = document.querySelectorAll('input[name="prefs"]:checked');
    if (checkboxes.length > max) {
        checkbox.checked = false;
        alert("Só podes escolher até 3 preferências");
    }
}

// ============ TAB SWITCHING ============
function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.add('hidden'));

    // Remove active from all buttons
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Show selected tab and activate button
    const selectedTab = document.getElementById(`tab-${tabName}`);
    if (selectedTab) {
        selectedTab.classList.remove('hidden');
    }

    const selectedBtn = document.getElementById(`btn-${tabName}`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }

    // Set as default on page load
    localStorage.setItem('activeTab', tabName);
}

// Initialize tabs on page load
document.addEventListener('DOMContentLoaded', function() {
    const activeTab = localStorage.getItem('activeTab') || 'pedir';
    switchTab(activeTab);
});

// ============ MODAL FUNCTIONS ============
function toggleEditModal() {
    const modal = document.getElementById('edit-modal');
    modal.classList.toggle('hidden');
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('edit-modal');
    const isClickInsideModal = modal.querySelector('.modal-content').contains(event.target);
    const isClickOnEditBtn = event.target.closest('.edit-info-btn');
    
    if (modal && !isClickInsideModal && !isClickOnEditBtn && !modal.classList.contains('hidden')) {
        modal.classList.add('hidden');
    }
});

// ============ SIGARRA PANEL ============
function toggleSiarraInfo() {
    const info = document.getElementById('siarra-info');
    if (info) {
        info.classList.toggle('hidden');
    }
}

// Close Sigarra when clicking outside
document.addEventListener('click', function(event) {
    const siarra = document.querySelector('.sigarra-panel');
    const info = document.getElementById('siarra-info');
    
    if (siarra && !siarra.contains(event.target) && info && !info.classList.contains('hidden')) {
        info.classList.add('hidden');
    }
});

// ============ CONDUCTOR FUNCTIONS ============
function acceptConductor() {
    // Hide action buttons
    const actions = document.querySelector('.conductor-actions');
    const card = document.querySelector('.conductor-card');
    
    actions.style.opacity = '0.5';
    actions.style.pointerEvents = 'none';
    
    // Show spinner
    const spinner = document.getElementById('waiting-spinner');
    if (spinner) {
        spinner.classList.remove('hidden');
    }

    // Simular envio de confirmação ao servidor
    console.log("Pedido de viagem aceite, à espera de confirmação do condutor...");
    
    // Aqui você pode fazer uma chamada AJAX para confirmar com o servidor
    // fetch('/confirmar_pedido', { method: 'POST' })
}

function rejectConductor() {
    // Recarregar para mostrar outro condutor
    window.location.reload();
    
    // Ou fazer uma chamada AJAX:
    // fetch('/proximo_condutor', { method: 'POST' })
    //     .then(response => response.json())
    //     .then(data => {
    //         // Atualizar a página com novo condutor
    //         location.reload();
    //     });
}

// ============ FORM SUBMISSION ============
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.querySelector('form[action="/editar_cliente"]');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const phone = document.getElementById('phone').value.trim();
            
            if (!name || !email || !phone) {
                e.preventDefault();
                alert('Por favor preenche todos os campos obrigatórios');
            }
        });
    }
});

// ============ UTILITY FUNCTIONS ============
function formatDate(dateString) {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
    return new Date(dateString).toLocaleDateString('pt-PT', options);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
