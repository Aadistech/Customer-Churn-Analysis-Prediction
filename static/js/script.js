document.addEventListener("DOMContentLoaded", function () {
    // 1. Bulk Upload File Name Display
    const fileInput = document.getElementById('dataset-upload');
    const fileNameDisplay = document.getElementById('file-name');
    const uploadForm = document.getElementById('upload-form');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                fileNameDisplay.innerHTML = `<strong>Selected file:</strong> ${e.target.files[0].name}`;
            } else {
                fileNameDisplay.innerHTML = "Supports .csv, .xlsx";
            }
        });
    }

    // 2. Form Loading State
    if (uploadForm) {
        uploadForm.addEventListener('submit', function() {
            if(fileInput.files.length === 0) {
                alert("Please upload a dataset before analyzing.");
                return false;
            }
            document.getElementById('loader').style.display = 'flex';
        });
    }

    // 3. Chart.js Initialization for Dashboard
    const chartCanvas = document.getElementById('churnChart');
    if (chartCanvas) {
        const churned = parseInt(chartCanvas.dataset.churn) || 0;
        const staying = parseInt(chartCanvas.dataset.stay) || 0;
        
        new Chart(chartCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Predicted Churn', 'Predicted Stay'],
                datasets: [{
                    data: [churned, staying],
                    backgroundColor: ['#ef4444', '#10b981'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
});

function triggerFileInput() {
    document.getElementById('dataset-upload').click();
}