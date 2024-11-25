const preventDefaults = (e) => {
    e.preventDefault();
    e.stopPropagation();
}

const highlight = () => {
    dropZone.classList.add('drag-over');
}

const unhighlight = () => {
    dropZone.classList.remove('drag-over');
}

const showLoading = ()=> { 
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('loading').classList.add('flex');
}

const hideLoading = () => {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('loading').classList.remove('flex');
}


const detectText = (imageId) => {
    showLoading()
    window.location.href = `/image/ocr/${imageId}`;
}

const redirectToEditor = (imageId) => {
    window.location.href = `/image/${imageId}`;
}


const deleteImage = (imageId) => {
    fetch(`/image/${imageId}`, {
        method: 'DELETE',
    }).then(response => {
        return response.json();
    }).then(data => {
        console.log(data);
        toastr.success('Image deleted successfully');
        window.location.reload();
    }).catch(error => {
        console.error('Error:', error);
        toastr.error('Error deleting image');
    });
}

const handleFiles = (files) => {
    ([...files]).forEach(uploadFile);
}

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const imageGrid = document.getElementById('image-grid');

dropZone.addEventListener('click', () => fileInput.click());

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    handleFiles(files);
});
fileInput.addEventListener('change', (e) => {
    e.preventDefault();
    const files = e.target.files;
    handleFiles(files);
});




