document.getElementById('menu-toggle').addEventListener('click', function() {
        document.getElementById('menu').classList.toggle('hidden');
    });

    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-upload');
    const cameraButton = document.getElementById('camera-button');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('bg-purple-900', 'bg-opacity-25');
    }

    function unhighlight() {
        dropArea.classList.remove('bg-purple-900', 'bg-opacity-25');
    }

    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        ([...files]).forEach(uploadFile);
    }

    function uploadFile(file) {
        toastr.info('Uploading files...');

        const formData = new FormData();
        formData.append('file', file);
        fetch('/docs/upload', {
            method: 'POST',
            body: formData,
        }).then(response => {
                return response.json();
        }).then(data => {
            console.log('File uploaded successfully:', data);
            window.location.href = '/docs/' + data['id'];
        }).catch(error => {
            console.error('Error:', error);
            toastr.error('Error uploading File')
        });

    }

    fileInput.addEventListener('change', function(e) {
        const files = e.target.files;
        handleFiles(files);
    });