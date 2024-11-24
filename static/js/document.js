

document.getElementById('menu-toggle').addEventListener('click', function() {
    document.getElementById('menu').classList.toggle('hidden');
});
const onEdit = (docId) => {
    window.location.href = `/docs/${docId}`;
};



const uploadArea = document.querySelector('.upload-area');
const fileInput = document.getElementById('file-upload');

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('border-purple-500/50');
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('border-purple-500/50');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('border-purple-500/50');
    const files = e.dataTransfer.files;
    handleFiles(files);
});

fileInput.addEventListener('change', (e) => {
    e.preventDefault();
    const files = e.target.files;
    handleFiles(files);
});

const handleFiles = (files) => {
    ([...files]).forEach(uploadFile);
}

function uploadFile(files) {
    toastr.info('Uploading files...');
    console.log(files)
    
    const formData = new FormData();
    formData.append('file', files);
    fetch('/docs/upload', {
        method: 'POST',
        body: formData,
    }).then(response => {
        return response.json();
    }).then(data => {
        window.location.reload();
        console.log('File uploaded successfully:', data);
        window.location.href = '/docs/' + data['id'];
    }).catch(error => {
        console.error('Error:', error);
        toastr.error('Failed to upload file.');
    });
}

function onDelete(docId) {
    fetch(`/docs/${docId}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}