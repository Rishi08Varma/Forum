document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggle
    const togglePassword = document.createElement('button');
    togglePassword.type = 'button';
    togglePassword.className = 'btn btn-outline-secondary position-absolute end-0 top-0';
    togglePassword.innerHTML = '<i class="fas fa-eye"></i>';
    togglePassword.style.height = '100%';
    togglePassword.style.borderTopLeftRadius = '0';
    togglePassword.style.borderBottomLeftRadius = '0';

    const passwordField = document.querySelector('input[type="password"]');
    const passwordWrapper = document.createElement('div');
    passwordWrapper.className = 'position-relative';
    passwordField.parentNode.insertBefore(passwordWrapper, passwordField);
    passwordWrapper.appendChild(passwordField);
    passwordWrapper.appendChild(togglePassword);

    togglePassword.addEventListener('click', function() {
        const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordField.setAttribute('type', type);
        this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
    });

    // Form validation
    const form = document.querySelector('form');
    const emailInput = document.querySelector('input[type="email"]');

    form.addEventListener('submit', function(e) {
        if (!emailInput.value.includes('@')) {
            e.preventDefault();
            emailInput.classList.add('is-invalid');
            if (!emailInput.nextElementSibling) {
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = 'Please enter a valid email address';
                emailInput.parentNode.appendChild(feedback);
            }
        }
    });

    // Remove invalid class on input
    emailInput.addEventListener('input', function() {
        this.classList.remove('is-invalid');
    });
});