// Authentication Pages - Enhanced JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initAuthPageFeatures();
    initFormValidation();
    initPasswordStrength();
    initAnimations();
});

// Initialize authentication page features
function initAuthPageFeatures() {
    // Auto-focus first input
    const firstInput = document.querySelector('.auth-form .form-control');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Handle form submission loading state
    const authForm = document.querySelector('.auth-form');
    if (authForm) {
        authForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('.auth-btn-primary');
            if (submitBtn) {
                const originalContent = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                submitBtn.disabled = true;
                
                // Re-enable if form submission fails
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalContent;
                        submitBtn.disabled = false;
                    }
                }, 5000);
            }
        });
    }
    
    // Handle "Remember Me" checkbox animation
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkmark = this.nextElementSibling;
            if (checkmark && checkmark.classList.contains('checkmark')) {
                checkmark.style.transform = this.checked ? 'scale(1.1)' : 'scale(1)';
                setTimeout(() => {
                    checkmark.style.transform = 'scale(1)';
                }, 150);
            }
        });
    });
}

// Form validation enhancements
function initFormValidation() {
    const formControls = document.querySelectorAll('.form-control');
    
    formControls.forEach(input => {
        // Real-time validation feedback
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
        
        // Enhanced focus effects
        input.addEventListener('focus', function() {
            const formGroup = this.closest('.form-group');
            if (formGroup) {
                formGroup.classList.add('focused');
            }
        });
        
        input.addEventListener('blur', function() {
            const formGroup = this.closest('.form-group');
            if (formGroup) {
                formGroup.classList.remove('focused');
            }
        });
    });
    
    // Password confirmation validation
    const password2 = document.getElementById('id_password2');
    if (password2) {
        password2.addEventListener('input', function() {
            const password1 = document.getElementById('id_password1');
            if (password1 && password1.value && this.value) {
                if (password1.value !== this.value) {
                    showFieldError(this, 'Passwords do not match');
                } else {
                    clearFieldError(this);
                    showFieldSuccess(this);
                }
            }
        });
    }
    
    // Email validation
    const emailField = document.getElementById('id_email');
    if (emailField) {
        emailField.addEventListener('blur', function() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                showFieldError(this, 'Please enter a valid email address');
            }
        });
    }
    
    // Username validation
    const usernameField = document.getElementById('id_username');
    if (usernameField) {
        usernameField.addEventListener('blur', function() {
            if (this.value && this.value.length < 3) {
                showFieldError(this, 'Username must be at least 3 characters long');
            }
        });
    }
}

// Password strength indicator
function initPasswordStrength() {
    const passwordField = document.getElementById('id_password1');
    if (passwordField) {
        const strengthIndicator = createPasswordStrengthIndicator();
        passwordField.parentNode.appendChild(strengthIndicator);
        
        passwordField.addEventListener('input', function() {
            updatePasswordStrength(this.value, strengthIndicator);
        });
    }
}

function createPasswordStrengthIndicator() {
    const container = document.createElement('div');
    container.className = 'password-strength-container';
    container.innerHTML = `
        <div class="password-strength-bar">
            <div class="password-strength-fill"></div>
        </div>
        <div class="password-strength-text">Password strength</div>
    `;
    
    // Add CSS for password strength indicator
    const style = document.createElement('style');
    style.textContent = `
        .password-strength-container {
            margin-top: 0.5rem;
        }
        
        .password-strength-bar {
            height: 4px;
            background: #e5e7eb;
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 0.25rem;
        }
        
        .password-strength-fill {
            height: 100%;
            width: 0%;
            transition: all 0.3s ease;
            border-radius: 2px;
        }
        
        .password-strength-text {
            font-size: 0.75rem;
            color: #6c757d;
        }
        
        .strength-weak .password-strength-fill { background: #dc3545; width: 25%; }
        .strength-fair .password-strength-fill { background: #fd7e14; width: 50%; }
        .strength-good .password-strength-fill { background: #ffc107; width: 75%; }
        .strength-strong .password-strength-fill { background: #198754; width: 100%; }
    `;
    document.head.appendChild(style);
    
    return container;
}

function updatePasswordStrength(password, indicator) {
    const strength = calculatePasswordStrength(password);
    const textElement = indicator.querySelector('.password-strength-text');
    
    // Remove all strength classes
    indicator.classList.remove('strength-weak', 'strength-fair', 'strength-good', 'strength-strong');
    
    if (password.length === 0) {
        textElement.textContent = 'Password strength';
        return;
    }
    
    switch (strength) {
        case 1:
            indicator.classList.add('strength-weak');
            textElement.textContent = 'Weak password';
            textElement.style.color = '#dc3545';
            break;
        case 2:
            indicator.classList.add('strength-fair');
            textElement.textContent = 'Fair password';
            textElement.style.color = '#fd7e14';
            break;
        case 3:
            indicator.classList.add('strength-good');
            textElement.textContent = 'Good password';
            textElement.style.color = '#ffc107';
            break;
        case 4:
            indicator.classList.add('strength-strong');
            textElement.textContent = 'Strong password';
            textElement.style.color = '#198754';
            break;
        default:
            textElement.textContent = 'Password strength';
            textElement.style.color = '#6c757d';
    }
}

function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    if (password.length >= 12) score++;
    
    return Math.min(score, 4);
}

// Field validation helpers
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    
    if (field.required && !value) {
        showFieldError(field, `${getFieldLabel(fieldName)} is required`);
        return false;
    }
    
    return true;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('field-error');
    field.style.borderColor = '#dc3545';
    
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error-message';
    errorElement.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    errorElement.style.cssText = `
        color: #dc3545;
        font-size: 0.8rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    field.parentNode.appendChild(errorElement);
}

function showFieldSuccess(field) {
    clearFieldError(field);
    
    field.style.borderColor = '#198754';
    
    const successElement = document.createElement('div');
    successElement.className = 'field-success-message';
    successElement.innerHTML = `<i class="fas fa-check-circle"></i>`;
    successElement.style.cssText = `
        color: #198754;
        font-size: 0.8rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    field.parentNode.appendChild(successElement);
}

function clearFieldError(field) {
    field.classList.remove('field-error');
    field.style.borderColor = '';
    
    const errorMessage = field.parentNode.querySelector('.field-error-message');
    const successMessage = field.parentNode.querySelector('.field-success-message');
    
    if (errorMessage) errorMessage.remove();
    if (successMessage) successMessage.remove();
}

function getFieldLabel(fieldName) {
    const labels = {
        'first_name': 'First name',
        'last_name': 'Last name',
        'email': 'Email address',
        'username': 'Username',
        'password1': 'Password',
        'password2': 'Confirm password',
        'year_of_study': 'Year of study',
        'college_name': 'College name'
    };
    
    return labels[fieldName] || fieldName.replace('_', ' ');
}

// Animations
function initAnimations() {
    // Stagger form field animations
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach((group, index) => {
        group.style.opacity = '0';
        group.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            group.style.transition = 'all 0.5s ease';
            group.style.opacity = '1';
            group.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Animate auth button
    const authBtn = document.querySelector('.auth-btn-primary');
    if (authBtn) {
        authBtn.style.opacity = '0';
        authBtn.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            authBtn.style.transition = 'all 0.5s ease';
            authBtn.style.opacity = '1';
            authBtn.style.transform = 'translateY(0)';
        }, formGroups.length * 100 + 200);
    }
    
    // Removed floating animation for static appearance
}

// Utility function for password toggle (used in templates)
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const button = field.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.className = 'fas fa-eye-slash';
        button.setAttribute('title', 'Hide password');
    } else {
        field.type = 'password';
        icon.className = 'fas fa-eye';
        button.setAttribute('title', 'Show password');
    }
    
    // Add ripple effect
    button.style.transform = 'scale(0.95)';
    setTimeout(() => {
        button.style.transform = 'scale(1)';
    }, 100);
}
