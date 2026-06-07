function removePhoto() {

    
    const input = document.getElementById('photoInput');
    if (input) {
        input.value = '';
    }

    
    const removeInput = document.getElementById('removePhotoInput');
    if (removeInput) {
        removeInput.value = 'true';
    }

    
    const removeBtn = document.getElementById('removePhotoBtn');
    if (removeBtn) {
        removeBtn.style.display = 'none';
    }

    
    const preview = document.getElementById('photoPreview');

    if (!preview) return;

    if (typeof userInitialFallback !== 'undefined' && userInitialFallback !== '') {

        
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

    
    if (file.size > 5 * 1024 * 1024) {
        alert("Image too large (max 5MB).");
        input.value = '';
        return;
    }

    
    const removeInput = document.getElementById('removePhotoInput');
    if (removeInput) {
        removeInput.value = 'false';
    }

    
    const removeBtn = document.getElementById('removePhotoBtn');
    if (removeBtn) {
        removeBtn.style.display = 'inline-block';
    }

    const reader = new FileReader();

    reader.onload = function(e) {
        const preview = document.getElementById('photoPreview');
        if (!preview) return;

        
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
