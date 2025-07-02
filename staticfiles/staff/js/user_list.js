// User List Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Select all checkbox functionality
    const selectAllCheckbox = document.getElementById('selectAll');
    const userCheckboxes = document.querySelectorAll('.user-checkbox');
    const bulkActions = document.getElementById('bulkActions');
    const bulkActionSelect = document.getElementById('bulkActionSelect');
    const applyBulkActionBtn = document.getElementById('applyBulkAction');

    // Handle select all
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            userCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            toggleBulkActions();
        });
    }

    // Handle individual checkboxes
    userCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Update select all checkbox state
            const checkedCount = document.querySelectorAll('.user-checkbox:checked').length;
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = checkedCount === userCheckboxes.length;
                selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < userCheckboxes.length;
            }
            
            toggleBulkActions();
        });
    });

    function toggleBulkActions() {
        const checkedCount = document.querySelectorAll('.user-checkbox:checked').length;
        if (bulkActions) {
            bulkActions.style.display = checkedCount > 0 ? 'flex' : 'none';
        }
    }

    // Handle bulk action application
    if (applyBulkActionBtn) {
        applyBulkActionBtn.addEventListener('click', function() {
            const action = bulkActionSelect ? bulkActionSelect.value : '';
            const selectedUsers = Array.from(document.querySelectorAll('.user-checkbox:checked')).map(cb => cb.value);
            
            if (!action || selectedUsers.length === 0) {
                alert('Please select an action and at least one user.');
                return;
            }

            const actionText = action.replace('_', ' ');
            
            if (confirm(`Are you sure you want to ${actionText} ${selectedUsers.length} user(s)?`)) {
                // Create form and submit
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = window.location.href;
                
                // Add CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
                if (csrfToken) {
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrfmiddlewaretoken';
                    csrfInput.value = csrfToken.value;
                    form.appendChild(csrfInput);
                }
                
                // Add action
                const actionInput = document.createElement('input');
                actionInput.type = 'hidden';
                actionInput.name = 'action';
                actionInput.value = action;
                form.appendChild(actionInput);
                
                // Add selected user IDs
                selectedUsers.forEach(userId => {
                    const userInput = document.createElement('input');
                    userInput.type = 'hidden';
                    userInput.name = 'user_ids';
                    userInput.value = userId;
                    form.appendChild(userInput);
                });
                
                // Submit form
                document.body.appendChild(form);
                form.submit();
            }
        });
    }

    // Auto-submit form on filter change (optional live filtering)
    const filterSelects = document.querySelectorAll('#userSearchForm select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            // Uncomment the next line to enable auto-submit on filter change
            // document.getElementById('userSearchForm').submit();
        });
    });

    // Bulk upload button
    const bulkUploadBtn = document.getElementById('bulkUploadBtn');
    if (bulkUploadBtn) {
        bulkUploadBtn.addEventListener('click', function() {
            alert('Bulk upload feature coming soon!');
        });
    }
});

// Function to toggle user status (activate/deactivate)
function toggleUserStatus(userId, activate) {
    const action = activate ? 'activate' : 'deactivate';
    if (confirm(`Are you sure you want to ${action} this user?`)) {
        // Create form and submit
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = window.location.href;
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken.value;
            form.appendChild(csrfInput);
        }
        
        // Add action
        const actionInput = document.createElement('input');
        actionInput.type = 'hidden';
        actionInput.name = 'action';
        actionInput.value = action;
        form.appendChild(actionInput);
        
        // Add user ID
        const userInput = document.createElement('input');
        userInput.type = 'hidden';
        userInput.name = 'user_ids';
        userInput.value = userId;
        form.appendChild(userInput);
        
        // Submit form
        document.body.appendChild(form);
        form.submit();
    }
}
