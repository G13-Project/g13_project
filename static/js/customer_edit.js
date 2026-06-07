function removePhoto() {
    // 1. Limpar o input de ficheiro
    document.getElementById('photoInput').value = '';
    
    // 2. Avisar o backend que queremos remover a foto
    document.getElementById('removePhotoInput').value = 'true';
    
    // 3. Esconder o botão de remover
    document.getElementById('removePhotoBtn').style.display = 'none';
    
    // 4. Mudar a preview para as iniciais (fallback)
    var preview = document.getElementById('photoPreview');
    if (preview.tagName === 'IMG') {
        var div = document.createElement('div');
        div.id = 'photoPreview';
        div.className = 'no-photo photo-preview';
        div.innerText = userInitials;
        preview.parentNode.replaceChild(div, preview);
    }
}

function previewPhoto(input) {
    if (input.files && input.files[0]) {
        // Ao escolher uma foto nova, já não queremos remover
        document.getElementById('removePhotoInput').value = 'false';
        
        // Mostrar o botão de remover
        document.getElementById('removePhotoBtn').style.display = 'inline-block';

        var reader = new FileReader();
        reader.onload = function(e) {
            var preview = document.getElementById('photoPreview');
            // Replace with img if it was a div
            if (preview.tagName !== 'IMG') {
                var img = document.createElement('img');
                img.id = 'photoPreview';
                img.className = 'photo-preview';
                img.src = e.target.result;
                preview.parentNode.replaceChild(img, preview);
            } else {
                preview.src = e.target.result;
            }
        }
        reader.readAsDataURL(input.files[0]);
    }
}
