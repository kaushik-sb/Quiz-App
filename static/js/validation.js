// Client-side validation for all forms
document.addEventListener('DOMContentLoaded', function() {
    // Register Form Validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.querySelector('input[name="password"]');
            const dob = document.querySelector('input[name="dob"]');
            
            // Password check
            if (password.value.length < 8) {
                alert('Password must be at least 8 characters');
                e.preventDefault();
            }
            
            // Age check (minimum 13 years)
            const dobDate = new Date(dob.value);
            const minAgeDate = new Date();
            minAgeDate.setFullYear(minAgeDate.getFullYear() - 13);
            
            if (dobDate > minAgeDate) {
                alert('You must be at least 13 years old');
                e.preventDefault();
            }
        });
    }

    // Login Form Validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const password = document.querySelector('input[name="password"]');
            if (password.value.length < 8) {
                alert('Password must be at least 8 characters');
                e.preventDefault();
            }
        });
    }
});