document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const passwordInput = document.querySelector('input[name="password"]');
    const confirmPasswordInput = document.querySelector('input[name="confirm_password"]');
    const usernameInput = document.querySelector('input[name="username"]');
    const emailInput = document.querySelector('input[name="email"]');

    // Add password strength meter
    const meterContainer = document.createElement('div');
    meterContainer.className = 'password-strength-meter';
    const meter = document.createElement('div');
    meterContainer.appendChild(meter);
    passwordInput.parentNode.insertBefore(meterContainer, passwordInput.nextSibling);

    // Password strength check
    function checkPasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
        if (password.match(/[0-9]/)) strength++;
        if (password.match(/[^a-zA-Z0-9]/)) strength++;
        
        meter.className = '';
        if (strength >= 3) {
            meter.classList.add('strength-strong');
        } else if (strength >= 2) {
            meter.classList.add('strength-medium');
        } else if (strength >= 1) {
            meter.classList.add('strength-weak');
        }
    }

    // Show/hide password toggle
    function createPasswordToggle(inputField) {
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'btn btn-outline-secondary position-absolute end-0 top-0';
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        toggleBtn.style.height = '100%';
        toggleBtn.style.borderTopLeftRadius = '0';
        toggleBtn.style.borderBottomLeftRadius = '0';

        const wrapper = document.createElement('div');
        wrapper.className = 'position-relative';
        inputField.parentNode.insertBefore(wrapper, inputField);
        wrapper.appendChild(inputField);
        wrapper.appendChild(toggleBtn);

        toggleBtn.addEventListener('click', function() {
            const type = inputField.getAttribute('type') === 'password' ? 'text' : 'password';
            inputField.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }

    // Create password toggles
    createPasswordToggle(passwordInput);
    createPasswordToggle(confirmPasswordInput);

    // Real-time validation
    passwordInput.addEventListener('input', function() {
        checkPasswordStrength(this.value);
    });

    form.addEventListener('submit', function(e) {
        let hasError = false;

        // Username validation
        if (usernameInput.value.length < 3) {
            usernameInput.classList.add('is-invalid');
            hasError = true;
        }

        // Email validation
        if (!emailInput.value.includes('@')) {
            emailInput.classList.add('is-invalid');
            hasError = true;
        }

        // Password validation
        if (passwordInput.value !== confirmPasswordInput.value) {
            confirmPasswordInput.classList.add('is-invalid');
            hasError = true;
        }

        if (hasError) {
            e.preventDefault();
        }
    });

    // Remove invalid class on input
    [usernameInput, emailInput, passwordInput, confirmPasswordInput].forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
        });
    });
});