document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const progressBar = document.getElementById('progressBar');
    const nextToPreferences = document.getElementById('nextToPreferences');
    const backToStep1 = document.getElementById('backToStep1');
    const completeSignup = document.getElementById('completeSignup');
    const startSwiping = document.getElementById('startSwiping');
    const selectAll = document.getElementById('selectAll');
    const selectNone = document.getElementById('selectNone');
    const topicCheckboxes = document.querySelectorAll('.topic-checkbox');

    // Form data
    let formData = {
        name: '',
        phone: '',
        password: '',
        preferences: []
    };

    // Event listeners
    nextToPreferences.addEventListener('click', handleNextToPreferences);
    backToStep1.addEventListener('click', handleBackToStep1);
    completeSignup.addEventListener('click', handleCompleteSignup);
    startSwiping.addEventListener('click', handleStartSwiping);
    selectAll.addEventListener('click', () => selectAllTopics(true));
    selectNone.addEventListener('click', () => selectAllTopics(false));

    // Topic checkbox listeners
    topicCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updatePreferences);
    });

    function handleNextToPreferences() {
        // Validate step 1
        const name = document.getElementById('name').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const password = document.getElementById('password').value.trim();

        if (!name || !phone || !password) {
            showAlert('Please fill in all fields', 'error');
            return;
        }

        if (phone.length < 10) {
            showAlert('Please enter a valid phone number', 'error');
            return;
        }

        if (password.length < 6) {
            showAlert('Password must be at least 6 characters long', 'error');
            return;
        }

        // Save step 1 data
        formData.name = name;
        formData.phone = phone;
        formData.password = password;

        // Move to step 2
        step1.style.display = 'none';
        step2.style.display = 'block';
        progressBar.style.width = '66%';
    }

    function handleBackToStep1() {
        step2.style.display = 'none';
        step1.style.display = 'block';
        progressBar.style.width = '33%';
    }

    function handleCompleteSignup() {
        // Get selected preferences
        const selectedTopics = Array.from(topicCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        if (selectedTopics.length === 0) {
            showAlert('Please select at least one topic of interest', 'error');
            return;
        }

        formData.preferences = selectedTopics;

        // Show loading state
        completeSignup.disabled = true;
        completeSignup.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating Account...';

        // Submit form
        submitSignup();
    }

    function submitSignup() {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/signup';

        // Add form fields
        const nameInput = document.createElement('input');
        nameInput.type = 'hidden';
        nameInput.name = 'name';
        nameInput.value = formData.name;
        form.appendChild(nameInput);

        const phoneInput = document.createElement('input');
        phoneInput.type = 'hidden';
        phoneInput.name = 'phone';
        phoneInput.value = formData.phone;
        form.appendChild(phoneInput);

        const passwordInput = document.createElement('input');
        passwordInput.type = 'hidden';
        passwordInput.name = 'password';
        passwordInput.value = formData.password;
        form.appendChild(passwordInput);

        // Add preferences as hidden inputs
        formData.preferences.forEach(preference => {
            const prefInput = document.createElement('input');
            prefInput.type = 'hidden';
            prefInput.name = 'preferences';
            prefInput.value = preference;
            form.appendChild(prefInput);
        });

        document.body.appendChild(form);
        form.submit();
    }

    function handleStartSwiping() {
        window.location.href = '/';
    }

    function selectAllTopics(select) {
        topicCheckboxes.forEach(checkbox => {
            checkbox.checked = select;
        });
        updatePreferences();
    }

    function updatePreferences() {
        const selectedTopics = Array.from(topicCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        
        formData.preferences = selectedTopics;
        
        // Update complete button state
        completeSignup.disabled = selectedTopics.length === 0;
    }

    function showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert after the card title
        const cardBody = document.querySelector('.card-body');
        cardBody.insertBefore(alertDiv, cardBody.querySelector('.form-check, .d-grid, .d-flex'));
    }

    // Initialize
    updatePreferences();
});
