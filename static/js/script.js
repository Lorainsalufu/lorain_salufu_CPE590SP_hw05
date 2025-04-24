// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const uploadForm = document.getElementById('upload-form');
    const imageUpload = document.getElementById('image-upload');
    const previewImg = document.getElementById('preview-img');
    const predictButton = document.getElementById('predict-button');
    const predictionResultDiv = document.getElementById('prediction-result');
    const exampleButtons = document.querySelectorAll('.use-example-btn');
    const sampleImages = document.querySelectorAll('.sample-img');

    // Initialize Chart.js
    const ctx = document.getElementById('probability-chart').getContext('2d');
    let probabilityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            datasets: [{
                label: 'Probability',
                data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(255, 154, 162, 0.7)',
                    'rgba(181, 234, 215, 0.7)',
                    'rgba(199, 206, 234, 0.7)'
                ],
                borderColor: [
                    'rgb(255, 154, 162)',
                    'rgb(181, 234, 215)',
                    'rgb(199, 206, 234)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    title: {
                        display: true,
                        text: 'Probability'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Digit Class Probabilities'
                }
            }
        }
    });

    // Image preview
    imageUpload.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImg.src = e.target.result;
                previewImg.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle form submission
    predictButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Get input values
        const file = imageUpload.files[0];
        if (!file) {
            alert("Please upload an image first.");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        
        
        // Make prediction request
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Display result
            displayPredictionResult(data);
            // Update chart
            updateProbabilityChart(data.probabilities);
        })
        .catch(error => {
            predictionResultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
        });
    });

    // Handle example images
    sampleImages.forEach(img => {
        img.addEventListener('click', function() {
            const sampleName = this.dataset.sample;
            if (!sampleName) return;

            imageUpload.value = "";

            
            // Set preview image
            previewImg.src = this.src;
            
            fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sample_image: sampleName })
            })
            .then(response => response.json())
            .then(data => {
                displayPredictionResult(data);
                updateProbabilityChart(data.probabilities);
            })
            .catch(error => {
                predictionResultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            });
        });
    });

    // Function to display prediction result
    function displayPredictionResult(data) {
        if (data.error) {
            predictionResultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            return;
        }

        const result = `
            <h3>Predicted Digit: <span style="color: green;">${data.class_name}</span></h3>
            <p>Confidence Score: ${(data.probabilities[data.class_name] * 100).toFixed(2)}%</p>
        `;
        
        predictionResultDiv.innerHTML = result;
    }

    // Function to update probability chart
    function updateProbabilityChart(probabilities) {
        if (!probabilities) return; // prevent chart errors
        const data = [];
        for (let i = 0; i < 10; i++) {
            data.push(probabilities[i.toString()] || 0);
        }
        probabilityChart.data.datasets[0].data = data;
        probabilityChart.update();
    }
});