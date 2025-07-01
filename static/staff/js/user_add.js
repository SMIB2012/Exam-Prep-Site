/**
 * User Add Page JavaScript
 * Handles dynamic functionality for the add user form
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form functionality
    initPasswordToggles();
    initFormValidation();
    initRoleBasedFields();
    initCollegeDropdown();
    
    console.log('User Add page initialized');
});

/**
 * Initialize password show/hide toggles
 */
function initPasswordToggles() {
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Find the password input (previous sibling)
            const passwordInput = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (passwordInput && passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
                this.setAttribute('aria-label', 'Hide password');
            } else if (passwordInput) {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
                this.setAttribute('aria-label', 'Show password');
            }
        });
    });
}

/**
 * Toggle password visibility for specific field
 * @param {string} fieldId - The ID of the password field
 */
function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const toggleButton = passwordField.nextElementSibling;
    const icon = toggleButton.querySelector('i');
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
        toggleButton.setAttribute('aria-label', 'Hide password');
    } else {
        passwordField.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
        toggleButton.setAttribute('aria-label', 'Show password');
    }
}

/**
 * Initialize form validation enhancements
 */
function initFormValidation() {
    const form = document.querySelector('form');
    const passwordField = document.querySelector('input[name="password"]');
    const confirmPasswordField = document.querySelector('input[name="confirm_password"]');
    const emailField = document.querySelector('input[name="email"]');
    
    // Real-time password validation
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            validatePassword(this);
        });
    }
    
    // Real-time password confirmation
    if (confirmPasswordField && passwordField) {
        confirmPasswordField.addEventListener('input', function() {
            validatePasswordConfirmation(passwordField, this);
        });
    }
    
    // Email validation
    if (emailField) {
        emailField.addEventListener('blur', function() {
            validateEmail(this);
        });
    }
    
    // Form submission validation
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                showValidationErrors();
            }
        });
    }
}

/**
 * Validate password strength
 * @param {HTMLElement} passwordField - The password input field
 */
function validatePassword(passwordField) {
    const password = passwordField.value;
    const minLength = 8;
    
    // Remove existing validation classes
    passwordField.classList.remove('is-valid', 'is-invalid');
    
    // Remove existing feedback
    const existingFeedback = passwordField.parentNode.querySelector('.password-strength-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    if (password.length === 0) {
        return;
    }
    
    // Create feedback element
    const feedback = document.createElement('div');
    feedback.className = 'password-strength-feedback';
    feedback.style.fontSize = '0.8rem';
    feedback.style.marginTop = '5px';
    
    if (password.length < minLength) {
        passwordField.classList.add('is-invalid');
        feedback.className += ' invalid-feedback';
        feedback.textContent = `Password must be at least ${minLength} characters long`;
    } else {
        passwordField.classList.add('is-valid');
        feedback.className += ' valid-feedback';
        feedback.style.color = 'var(--admin-success)';
        feedback.textContent = 'Password strength: Good';
    }
    
    passwordField.parentNode.appendChild(feedback);
}

/**
 * Validate password confirmation
 * @param {HTMLElement} passwordField - The original password field
 * @param {HTMLElement} confirmField - The confirm password field
 */
function validatePasswordConfirmation(passwordField, confirmField) {
    const password = passwordField.value;
    const confirm = confirmField.value;
    
    // Remove existing validation classes
    confirmField.classList.remove('is-valid', 'is-invalid');
    
    // Remove existing feedback
    const existingFeedback = confirmField.parentNode.querySelector('.password-match-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    if (confirm.length === 0) {
        return;
    }
    
    // Create feedback element
    const feedback = document.createElement('div');
    feedback.className = 'password-match-feedback';
    feedback.style.fontSize = '0.8rem';
    feedback.style.marginTop = '5px';
    
    if (password !== confirm) {
        confirmField.classList.add('is-invalid');
        feedback.className += ' invalid-feedback';
        feedback.textContent = 'Passwords do not match';
    } else {
        confirmField.classList.add('is-valid');
        feedback.className += ' valid-feedback';
        feedback.style.color = 'var(--admin-success)';
        feedback.textContent = 'Passwords match';
    }
    
    confirmField.parentNode.appendChild(feedback);
}

/**
 * Validate email format
 * @param {HTMLElement} emailField - The email input field
 */
function validateEmail(emailField) {
    const email = emailField.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    // Remove existing validation classes
    emailField.classList.remove('is-valid', 'is-invalid');
    
    if (email.length === 0) {
        return;
    }
    
    if (!emailRegex.test(email)) {
        emailField.classList.add('is-invalid');
    } else {
        emailField.classList.add('is-valid');
    }
}

/**
 * Initialize role-based field visibility
 */
function initRoleBasedFields() {
    const roleField = document.querySelector('select[name="user_role"]');
    const yearField = document.querySelector('select[name="year_of_study"]');
    const collegeFields = [
        document.querySelector('select[name="college_type"]'),
        document.querySelector('select[name="college_name"]') // Updated to select element
    ];
    
    if (roleField) {
        roleField.addEventListener('change', function() {
            toggleFieldsByRole(this.value, yearField, collegeFields);
        });
        
        // Initialize on page load
        toggleFieldsByRole(roleField.value, yearField, collegeFields);
    }
}

/**
 * Toggle fields based on user role
 * @param {string} role - The selected user role
 * @param {HTMLElement} yearField - Year of study field
 * @param {Array} collegeFields - Array of college-related fields
 */
function toggleFieldsByRole(role, yearField, collegeFields) {
    const isStudent = role === 'student';
    
    // Show/hide year field for students only
    if (yearField) {
        const yearGroup = yearField.closest('.form-group');
        if (yearGroup) {
            yearGroup.style.display = isStudent ? 'block' : 'none';
            yearField.required = isStudent;
        }
    }
    
    // College fields are relevant for both students and faculty
    const showCollegeFields = role === 'student' || role === 'faculty';
    collegeFields.forEach(field => {
        if (field) {
            const fieldGroup = field.closest('.form-group');
            if (fieldGroup) {
                fieldGroup.style.display = showCollegeFields ? 'block' : 'none';
            }
        }
    });
}

/**
 * Initialize college dropdown functionality
 */
function initCollegeDropdown() {
    const provinceField = document.querySelector('select[name="province"]');
    const collegeTypeField = document.querySelector('select[name="college_type"]');
    const collegeNameField = document.querySelector('select[name="college_name"]');
    
    if (provinceField && collegeTypeField && collegeNameField) {
        // Add event listeners
        provinceField.addEventListener('change', updateCollegeChoices);
        collegeTypeField.addEventListener('change', updateCollegeChoices);
        
        // Initialize on page load
        updateCollegeChoices();
    }
}

/**
 * Update college choices based on province and college type selection
 */
function updateCollegeChoices() {
    const provinceField = document.querySelector('select[name="province"]');
    const collegeTypeField = document.querySelector('select[name="college_type"]');
    const collegeNameField = document.querySelector('select[name="college_name"]');
    
    if (!provinceField || !collegeTypeField || !collegeNameField) return;
    
    const province = provinceField.value;
    const collegeType = collegeTypeField.value;
    
    // Medical colleges data (matching the backend)
    const medicalColleges = {
        "Punjab": {
            "Public": [
                "Allama Iqbal Medical College (Lahore)",
                "Ameer-ud-Din (PGMI) Medical College (Lahore)",
                "Army Medical College (Rawalpindi)",
                "D.G. Khan Medical College (Dera Ghazi Khan)",
                "Fatima Jinnah Medical College (Lahore)",
                "Services Institute of Medical Sciences (Lahore)",
                "Gujranwala Medical College",
                "Khawaja Muhammad Safdar MC (Sialkot)",
                "King Edward Medical University (Lahore)",
                "Nawaz Sharif Medical College (Gujrat)",
                "Nishtar Medical College (Multan)",
                "Punjab Medical College (Faisalabad)",
                "Quaid‑e‑Azam Medical College (Bahawalpur)",
                "Rawalpindi Medical College (Rawalpindi)",
                "Sahiwal Medical College",
                "Sargodha Medical College",
                "Shaikh Khalifa Bin Zayed MC (Lahore)",
                "Sheikh Zayed Medical College (Rahim Yar Khan)",
                "Narowal Medical College"
            ],
            "Private": [
                "FMH College of Medicine & Dentistry (Lahore)",
                "Lahore Medical & Dental College",
                "University College of Medicine & Dentistry (Lahore)",
                "Al Aleem Medical College",
                "Rahbar Medical College",
                "Rashid Latif Medical College",
                "Azra Naheed Medical College",
                "Pak Red Crescent Medical College",
                "Sharif Medical & Dental College",
                "Continental Medical College",
                "Akhtar Saeed Medical College",
                "CMH Lahore Medical & Dental College",
                "Shalamar Medical & Dental College",
                "Avicenna Medical College",
                "Abwa Medical College",
                "Independent Medical College",
                "Aziz Fatima Medical College",
                "Multan Medical & Dental College",
                "Bakhtawar Amin Medical & Dental College",
                "Central Park Medical College",
                "CIMS Multan",
                "HITEC Institute of Medical Sciences",
                "Hashmat Medical & Dental College",
                "Shahida Islam Medical College",
                "Wah Medical College",
                "Sahara Medical College",
                "CMH Kharian Medical College",
                "M. Islam Medical College",
                "Islam Medical College",
                "Fazaia Medical College",
                "Rai Medical College",
                "Margalla Institute of Health Sciences",
                "Mohammad Dental College",
                "Islamabad Medical & Dental College",
                "Yusra Medical & Dental College"
            ]
        },
        "Sindh": {
            "Public": [
                "Dow Medical College",
                "Dow International Medical College",
                "Karachi Medical & Dental College",
                "Chandka Medical College (Larkana)",
                "Ghulam Muhammad Mahar Medical College (Sukkur)",
                "Liaquat University of Medical & Health Sciences (Jamshoro)",
                "Peoples UMHS for Women (Nawabshah)",
                "Shaheed Mohtarma Benazir Bhutto MC (Lyari, Karachi)",
                "Jinnah Sindh Medical University",
                "Khairpur Medical College",
                "Bilawal Medical College (Hyderabad)"
            ],
            "Private": [
                "Aga Khan University",
                "Baqai Medical College",
                "Hamdard College of Medicine & Dentistry",
                "Jinnah Medical & Dental College",
                "Sir Syed College of Medical Sciences",
                "Ziauddin Medical College",
                "Liaquat National Medical College",
                "Bahria University Medical College",
                "Karachi Institute of Medical Sciences",
                "Al‑Tibri Medical College",
                "United Medical & Dental College",
                "Indus Medical College (Tando Muhammad Khan)",
                "Isra University Hyderabad",
                "Muhammad Medical College (Mirpurkhas)",
                "Suleman Roshan Medical College (Tando Adam)",
                "Fazaia Ruth Pfau Medical College (Karachi)"
            ]
        },
        "Khyber Pakhtunkhwa": {
            "Public": [
                "Khyber Medical College (Peshawar)",
                "Khyber Girls Medical College",
                "Ayub Medical College (Abbottabad)",
                "Saidu Medical College (Swat)",
                "Gomal Medical College (D.I. Khan)",
                "KMU Institute of Medical Sciences (Kohat)",
                "Bannu Medical College",
                "Bacha Khan Medical College (Mardan)",
                "Gajju Khan Medical College (Swabi)",
                "Nowshera Medical College"
            ],
            "Private": [
                "Abbottabad International Medical College",
                "Al‑Razi Medical College",
                "Frontier Medical College (Abbottabad)",
                "Kabir Medical College (Peshawar)",
                "Northwest School of Medicine",
                "Pak International Medical College",
                "Peshawar Medical College",
                "Rehman Medical College",
                "Women Medical & Dental College (Abbottabad)",
                "Swat Medical College",
                "Jinnah Medical College (Peshawar)"
            ]
        },
        "Balochistan": {
            "Public": [
                "Bolan Medical College (Quetta)",
                "Loralai Medical College",
                "Makran Medical College (Turbat)",
                "Jhalawan Medical College (Khuzdar)"
            ],
            "Private": [
                "Quetta Institute of Medical Sciences (Quetta)"
            ]
        },
        "Azad Jammu & Kashmir": {
            "Public": [
                "Azad Jammu & Kashmir Medical College (Muzaffarabad)",
                "Mohtarma Benazir Bhutto Shaheed Medical College (Mirpur)",
                "Poonch Medical College (Rawalakot)"
            ],
            "Private": [
                "Mohiuddin Islamic Medical College (Mirpur)"
            ]
        }
    };
    
    // Clear college name field
    collegeNameField.innerHTML = '<option value="">Select medical college</option>';
    
    // If both province and college type are selected, populate colleges
    if (province && collegeType && medicalColleges[province] && medicalColleges[province][collegeType]) {
        const colleges = medicalColleges[province][collegeType];
        colleges.forEach(college => {
            const option = document.createElement('option');
            option.value = college;
            option.textContent = college;
            collegeNameField.appendChild(option);
        });
        collegeNameField.disabled = false;
    } else {
        // Set placeholder based on what's missing
        if (!province && !collegeType) {
            collegeNameField.innerHTML = '<option value="">Select province and type first</option>';
        } else if (!province) {
            collegeNameField.innerHTML = '<option value="">Select province first</option>';
        } else if (!collegeType) {
            collegeNameField.innerHTML = '<option value="">Select college type first</option>';
        }
        collegeNameField.disabled = true;
    }
}

/**
 * Validate entire form before submission
 * @returns {boolean} - True if form is valid
 */
function validateForm() {
    let isValid = true;
    const requiredFields = document.querySelectorAll('input[required], select[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // Validate password match
    const passwordField = document.querySelector('input[name="password"]');
    const confirmPasswordField = document.querySelector('input[name="confirm_password"]');
    
    if (passwordField && confirmPasswordField) {
        if (passwordField.value !== confirmPasswordField.value) {
            confirmPasswordField.classList.add('is-invalid');
            isValid = false;
        }
    }
    
    return isValid;
}

/**
 * Show validation errors to user
 */
function showValidationErrors() {
    const firstErrorField = document.querySelector('.is-invalid');
    if (firstErrorField) {
        firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstErrorField.focus();
    }
    
    // Show general error message
    showNotification('Please correct the highlighted fields before submitting.', 'error');
}

/**
 * Show notification to user
 * @param {string} message - The message to show
 * @param {string} type - The type of notification (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.temp-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} temp-notification`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.borderRadius = '8px';
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Generate a strong password suggestion
 * @returns {string} - A generated password
 */
function generatePassword() {
    const length = 12;
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
    let password = "";
    
    for (let i = 0; i < length; i++) {
        password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    
    return password;
}

/**
 * Generate and fill password fields with a strong password
 */
function generateAndFillPassword() {
    const password = generatePassword();
    const passwordField = document.querySelector('input[name="password"]');
    const confirmPasswordField = document.querySelector('input[name="confirm_password"]');
    
    if (passwordField && confirmPasswordField) {
        passwordField.value = password;
        confirmPasswordField.value = password;
        
        // Trigger validation events
        passwordField.dispatchEvent(new Event('input', { bubbles: true }));
        confirmPasswordField.dispatchEvent(new Event('input', { bubbles: true }));
        
        // Show the generated password temporarily
        if (passwordField.type === 'password') {
            togglePassword(passwordField.id);
            
            // Hide it again after 3 seconds
            setTimeout(() => {
                if (passwordField.type === 'text') {
                    togglePassword(passwordField.id);
                }
            }, 3000);
        }
        
        showNotification('Strong password generated and filled!', 'success');
    }
}

/**
 * Auto-fill form with sample data (for development/testing)
 */
function fillSampleData() {
    const sampleData = {
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        password: generatePassword(),
        year_of_study: '1st_year',
        province: 'Punjab',
        college_type: 'Public',
        phone_number: '+92-300-1234567'
    };
    
    Object.keys(sampleData).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.value = sampleData[fieldName];
            
            // Trigger events for validation and dynamic updates
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.dispatchEvent(new Event('change', { bubbles: true }));
            field.dispatchEvent(new Event('blur', { bubbles: true }));
        }
    });
    
    // Fill confirm password
    const confirmPasswordField = document.querySelector('input[name="confirm_password"]');
    if (confirmPasswordField) {
        confirmPasswordField.value = sampleData.password;
        confirmPasswordField.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    // After province and college type are set, wait a moment then set college
    setTimeout(() => {
        const collegeNameField = document.querySelector('select[name="college_name"]');
        if (collegeNameField && collegeNameField.options.length > 1) {
            // Select the first college option (index 1, since 0 is the placeholder)
            collegeNameField.selectedIndex = 1;
            collegeNameField.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }, 100);
    
    showNotification('Sample data filled successfully!', 'success');
}

// Export functions for global access
window.togglePassword = togglePassword;
window.fillSampleData = fillSampleData;
window.generatePassword = generatePassword;
window.generateAndFillPassword = generateAndFillPassword;
