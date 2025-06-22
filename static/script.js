document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const form = document.getElementById('spoilage-form');
    const resultContainer = document.getElementById('result');
    const sampleBtn = document.getElementById('sample-btn');

    // Error handling if elements not found
    if (!form || !resultContainer) {
        console.error('Required elements not found');
        return;
    }

    // Sample data for testing
    const sampleData = {
        MQ8A: 320,
        MQ135A: 450,
        MQ9A: 410,
        MQ4A: 390,
        MQ2A: 470,
        MQ3A: 510
    };

    // Load sample data
    if (sampleBtn) {
        sampleBtn.addEventListener('click', function() {
            for (const [key, value] of Object.entries(sampleData)) {
                const input = document.getElementById(key);
                if (input) {
                    input.value = value;
                    // Trigger floating label effect
                    input.dispatchEvent(new Event('input'));
                }
            }
        });
    }

    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get and validate form data
        const formData = getFormData();
        if (!formData) return;

        // Show loading state
        showLoadingState();

        try {
            // Send to API and process response
            const response = await fetch('http://localhost:5000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            showError(error.message);
            console.error('API Error:', error);
        }
    });

    // Helper function to get and validate form data
    function getFormData() {
        const formData = {};
        let isValid = true;

        // Get all sensor inputs
        const inputs = form.querySelectorAll('input[type="number"]');
        
        inputs.forEach(input => {
            const value = parseFloat(input.value);
            const id = input.id;

            // Validate range (0-1023)
            if (isNaN(value) || value < 0 || value > 1023) {
                showError(`${id} must be between 0-1023`);
                input.classList.add('invalid');
                isValid = false;
            } else {
                formData[id] = value;
                input.classList.remove('invalid');
            }
        });

        return isValid ? formData : null;
    }

    // Show loading animation
    function showLoadingState() {
        resultContainer.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p class="loading-text">Analyzing food spoilage patterns...</p>
            </div>
        `;
    }

    // Display results with animations
    function displayResults(data) {
        if (data.error) {
            showError(data.error);
            return;
        }

        const statusClass = data.label.toLowerCase();
        const confidence = (data.confidence * 100).toFixed(1);
        
        resultContainer.innerHTML = `
            <div class="result-card ${statusClass}">
                <h3 class="result-status">${data.label}</h3>
                <span class="result-confidence">Confidence: ${confidence}%</span>
                <div class="result-details">
                    <p>Sensor analysis complete</p>
                    <small>Prediction value: ${data.prediction}</small>
                </div>
            </div>
        `;

        // Add visual feedback to form inputs
        updateInputVisuals(data.prediction);
    }

    // Show error message
    function showError(message) {
        resultContainer.innerHTML = `
            <div class="error-message">
                <p>⚠️ ${message}</p>
                <small>Please check your inputs and try again</small>
            </div>
        `;
    }

    // Update input visuals based on prediction
    function updateInputVisuals(prediction) {
        const inputs = form.querySelectorAll('input[type="number"]');
        const threshold = 0.5; // Adjust based on your model
        
        inputs.forEach(input => {
            const value = parseFloat(input.value);
            input.classList.remove('normal', 'warning', 'danger');
            
            if (prediction > threshold) {
                // Spoiled - highlight high values
                if (value > 700) input.classList.add('danger');
                else if (value > 400) input.classList.add('warning');
            } else {
                // Fresh - highlight low values
                if (value < 100) input.classList.add('danger');
                else if (value < 300) input.classList.add('warning');
                else input.classList.add('normal');
            }
        });
    }

    // Initialize floating labels
    function initFloatingLabels() {
        const inputs = form.querySelectorAll('.input-group input');
        
        inputs.forEach(input => {
            // Check if input has value on page load
            if (input.value) {
                input.dispatchEvent(new Event('input'));
            }
            
            // Add event listeners
            input.addEventListener('input', function() {
                const label = this.parentElement.querySelector('label');
                if (this.value) {
                    label.classList.add('active');
                } else {
                    label.classList.remove('active');
                }
            });
        });
    }

    // Initialize the form
    initFloatingLabels();
});