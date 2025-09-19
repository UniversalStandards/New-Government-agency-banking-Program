// GOFAP Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
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
            }
        });
    });
});

// Utility functions
const GOFAP = {
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
window.GOFAP = GOFAP;