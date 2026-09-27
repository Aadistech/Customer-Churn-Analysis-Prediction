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
            if(fileInput && fileInput.files.length === 0) {
                alert("Please upload a dataset before analyzing.");
                return false;
            }
            const loader = document.getElementById('loader');
            if (loader) {
                loader.style.display = 'flex';
            }
        });
    }

    // 3. Doughnut Chart Initialization for Dashboard
    const churnCanvas = document.getElementById('churnChart');
    if (churnCanvas) {
        const churned = parseInt(churnCanvas.dataset.churn) || 0;
        const staying = parseInt(churnCanvas.dataset.stay) || 0;
        
        new Chart(churnCanvas, {
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

    // 4. Bar Chart for Service Calls vs Churn Rate
    const serviceCanvas = document.getElementById('serviceCallsChart');
    if (serviceCanvas && serviceCanvas.dataset.charts) {
        try {
            const chartsData = JSON.parse(serviceCanvas.dataset.charts);
            const serviceData = chartsData.service_calls || [];
            
            const labels = serviceData.map(item => item.label + ' Calls');
            const values = serviceData.map(item => item.value);

            new Chart(serviceCanvas, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Churn Rate (%)',
                        data: values,
                        backgroundColor: values.map(val => val > 30 ? '#ef4444' : '#3b82f6'),
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Churn Rate: ' + context.parsed.y + '%';
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) { return value + '%'; }
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.error("Error parsing charts JSON:", e);
        }
    }
});

function triggerFileInput() {
    const el = document.getElementById('dataset-upload');
    if (el) el.click();
}