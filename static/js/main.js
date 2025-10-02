// GOFAP Main JavaScript File
// GOFAP Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
        import 'bootstrap'; // Ensure Bootstrap is imported
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add loading states to buttons
    const buttons = document.querySelectorAll('button[type="submit"], .btn-primary, .btn-success');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
                
                // Re-enable after 3 seconds (adjust as needed)
                setTimeout(() => {
                    this.disabled = false;
                    this.textContent = originalText;
                }, 3000);
    popoverTriggerList.forEach(function (popoverTriggerEl) { return new bootstrap.Popover(popoverTriggerEl); });
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add loading state to buttons on form submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                submitBtn.disabled = true;
                
                // Re-enable button after 5 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const alertInstance = new bootstrap.Alert(alert);
            alertInstance.close();
        }, 5000);
    });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Format currency inputs
    const currencyInputs = document.querySelectorAll('input[data-type="currency"]');
    currencyInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^\d.]/g, '');
            if (value) {
                value = parseFloat(value).toFixed(2);
                e.target.value = '$' + value;
            }
        });
    });

    // Add confirmation to delete buttons
    const deleteButtons = document.querySelectorAll('.btn-delete, .btn-danger[data-action="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemName = this.dataset.itemName || 'this item';
            if (confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                // Proceed with deletion
                if (this.href) {
                    window.location.href = escape(this.href);
                } else if (this.onclick) {
                    this.onclick();
                }
            }
        });
    });
});

// Utility functions
const GOFAP = {
    // Show notification
    showNotification: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            const alert = bootstrap.Alert.getOrCreateInstance(alertDiv);
            alert.close();
        }, 5000);
    },

    // Format currency
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    // Format date
    formatDate: function(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Intl.DateTimeFormat('en-US', {...defaultOptions, ...options}).format(new Date(date));
    },

    // Show loading spinner
    showLoading: function(element) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.id = 'loading-spinner';
        element.appendChild(spinner);
    },

    // Hide loading spinner
    hideLoading: function() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },

    // Show notification
    showNotification: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
        }
    formatDate: function(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    },

    // API helper
    api: {
        get: async function(url) {
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('API GET error:', error);
                GOFAP.showNotification('Failed to fetch data', 'danger');
                throw error;
            }
        },

        post: async function(url, data) {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('API POST error:', error);
                GOFAP.showNotification('Failed to save data', 'danger');
        call: async function(url, options = {}) {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            
            const config = Object.assign(defaultOptions, options);
            
            try {
                const response = await fetch(url, config);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'An error occurred');
                }
                
                return data;
            } catch (error) {
                GOFAP.showNotification(error.message, 'danger');
                throw error;
            }
        }
    },

    // Chart helper
    createChart: function(canvasId, config) {
        const ctx = document.getElementById(canvasId);
        if (ctx) {
            return new Chart(ctx, config);
        }
        return null;
    }
};

// Dashboard specific functionality
if (document.querySelector('.dashboard')) {
    // Load dashboard data
    loadDashboardData();
    
    function loadDashboardData() {
        // Load accounts
        GOFAP.api.get('/api/accounts')
            .then(accounts => {
                updateAccountsDisplay(accounts);
            })
            .catch(error => {
                console.error('Failed to load accounts:', error);
            });

        // Load transactions
        GOFAP.api.get('/api/transactions')
            .then(data => {
                updateTransactionsDisplay(data.transactions);
            })
            .catch(error => {
                console.error('Failed to load transactions:', error);
            });
    }

    function updateAccountsDisplay(accounts) {
        // Update accounts section if needed
        console.log('Accounts loaded:', accounts);
    }

    function updateTransactionsDisplay(transactions) {
        // Update transactions section if needed
        console.log('Transactions loaded:', transactions);
    }
}

// Form validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Add form validation to all forms
document.addEventListener('submit', function(e) {
    if (e.target.tagName === 'FORM') {
        if (!validateForm(e.target)) {
            e.preventDefault();
            GOFAP.showNotification('Please fill in all required fields', 'warning');
        }
    }
});

// Export for global access
    // Copy to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            GOFAP.showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            GOFAP.showNotification('Failed to copy to clipboard', 'danger');
        });
    }
};

// Make GOFAP globally available
window.GOFAP = GOFAP;