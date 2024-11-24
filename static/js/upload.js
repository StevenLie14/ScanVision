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


const uploadFile = (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_id', '{{ docs.id }}');

    fetch('/docs/add/'+ '{{ docs.id }}', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        toastr.error('Error uploading image');
    });
}
const downloadDocs = () => {
    fetch('/docs/download/' + '{{ docs.id }}', {
        method: 'GET',
    })
    .then(response => response.blob()) 
    .then(blob => { 
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob); 
        link.download = '{{docs.name}}.pdf'; 
        link.click();  
    })
    .catch(error => {
        console.log('Error:', error);
        toastr.error('Error downloading document');
    });
}

const toggleEdit = () => {
    const nameDisplay = document.getElementById('doc-name');
    const nameInput = document.getElementById('name-input');

    if (nameInput.classList.contains('hidden')) {
        nameDisplay.classList.add('hidden');
        nameInput.classList.remove('hidden');
        nameInput.focus();
    } else {
        nameDisplay.classList.remove('hidden');
        nameInput.classList.add('hidden');

        fetch('/docs/edit/' + '{{ docs.id }}', {
            method: 'POST',
            headers : {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: nameInput.value }),
        }).then(response => response.json())
        .then(response => {
            nameDisplay.textContent = nameInput.value
            console.log('Updated successfully')
            toastr.success('Updated Successfully')
        })
        .catch(err => {
            console.error(err)
            toastr.error('Update Failed')
        });
    }
}