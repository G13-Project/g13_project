function removePhoto() {

    // 1. Limpar input file
    const input = document.getElementById('photoInput');
    if (input) {
        input.value = '';
    }

    // 2. Avisar backend
    const removeInput = document.getElementById('removePhotoInput');
    if (removeInput) {
        removeInput.value = 'true';
    }

    // 3. Esconder botão remove
    const removeBtn = document.getElementById('removePhotoBtn');
    if (removeBtn) {
        removeBtn.style.display = 'none';
    }

    // 4. Atualizar preview
    const preview = document.getElementById('photoPreview');

    if (!preview) return;

    if (typeof userInitialFallback !== 'undefined' && userInitialFallback !== '') {

        // Mostrar fallback image
        if (preview.tagName !== 'IMG') {
            const img = document.createElement('img');
            img.id = 'photoPreview';
            img.className = 'photo-preview';
            img.src = userInitialFallback;

            preview.parentNode.replaceChild(img, preview);
        } else {
            preview.src = userInitialFallback;
        }

    } else {
        // Sem fallback → mostrar "?"
        if (preview.tagName === 'IMG') {
            const div = document.createElement('div');
            div.id = 'photoPreview';
            div.className = 'no-photo photo-preview';
            div.innerText = '?';

            preview.parentNode.replaceChild(div, preview);
        } else {
            preview.innerText = '?';
        }
    }
}


function previewPhoto(input) {

    if (!input.files || !input.files[0]) return;

    const file = input.files[0];

    // ✅ OPCIONAL: validação de tamanho (5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert("Image too large (max 5MB).");
        input.value = '';
        return;
    }

    // ✅ reset remove flag
    const removeInput = document.getElementById('removePhotoInput');
    if (removeInput) {
        removeInput.value = 'false';
    }

    // ✅ mostrar botão remove
    const removeBtn = document.getElementById('removePhotoBtn');
    if (removeBtn) {
        removeBtn.style.display = 'inline-block';
    }

    const reader = new FileReader();

    reader.onload = function(e) {
        const preview = document.getElementById('photoPreview');
        if (!preview) return;

        // substituir se for div
        if (preview.tagName !== 'IMG') {
            const img = document.createElement('img');
            img.id = 'photoPreview';
            img.className = 'photo-preview';
            img.src = e.target.result;

            preview.parentNode.replaceChild(img, preview);
        } else {
            preview.src = e.target.result;
        }
    };

    reader.readAsDataURL(file);
}
