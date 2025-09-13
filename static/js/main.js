/**
 * GOFAP - Government Operations and Financial Accounting Platform
 * Main JavaScript file for frontend functionality
 */

// Global GOFAP object
const GOFAP = {
    version: '1.0.0',
    apiUrl: '/api',
    
    // Initialize the application
    init: function() {
        console.log('Initializing GOFAP v' + this.version);
        this.setupEventListeners();
        this.loadSystemHealth();
        this.startHealthMonitoring();
    },
    
    // Setup global event listeners
    setupEventListeners: function() {
        // Add loading spinner to forms
        document.addEventListener('DOMContentLoaded', function() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                form.addEventListener('submit', function() {
                    GOFAP.showLoading(this);
                });
            });
        });
        
        // Handle AJAX requests
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('ajax-link')) {
                e.preventDefault();
                GOFAP.handleAjaxRequest(e.target.href, e.target);
            }
        });
    },
    
    // Show loading spinner
    showLoading: function(element) {
        const spinner = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>';
        if (element.tagName === 'BUTTON') {
            element.innerHTML = spinner + 'Processing...';
            element.disabled = true;
        } else {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'spinner-wrapper';
            loadingDiv.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';
            element.appendChild(loadingDiv);
        }
    },
    
    // Hide loading spinner
    hideLoading: function(element) {
        const spinner = element.querySelector('.spinner-wrapper');
        if (spinner) {
            spinner.remove();
        }
        
        if (element.tagName === 'BUTTON') {
            element.disabled = false;
            // Restore original button text if needed
        }
    },
    
    // Handle AJAX requests
    handleAjaxRequest: function(url, element) {
        this.showLoading(element);
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                this.hideLoading(element);
                this.handleApiResponse(data, element);
            })
            .catch(error => {
                this.hideLoading(element);
                this.showError('Failed to load data: ' + error.message);
            });
    },
    
    // Handle API responses
    handleApiResponse: function(data, element) {
        if (data.status === 'error') {
            this.showError(data.message || 'An error occurred');
        } else {
            this.showSuccess(data.message || 'Request completed successfully');
            // Update UI based on response
            this.updateUI(data, element);
        }
    },
    
    // Update UI with new data
    updateUI: function(data, element) {
        // This can be customized based on the specific response
        if (data.accounts) {
            this.updateAccountsList(data.accounts);
        }
        if (data.transactions) {
            this.updateTransactionsList(data.transactions);
        }
    },
    
    // Update accounts list
    updateAccountsList: function(accounts) {
        const accountsContainer = document.getElementById('accounts-list');
        if (accountsContainer && accounts.length > 0) {
            accountsContainer.innerHTML = accounts.map(account => `
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">${account.account_name}</h5>
                            <p class="card-text">Balance: $${account.balance}</p>
                            <p class="card-text"><small class="text-muted">Type: ${account.account_type}</small></p>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    },
    
    // Update transactions list
    updateTransactionsList: function(transactions) {
        const transactionsContainer = document.getElementById('transactions-list');
        if (transactionsContainer && transactions.length > 0) {
            transactionsContainer.innerHTML = transactions.map(tx => `
                <tr>
                    <td>${tx.transaction_id}</td>
                    <td>$${tx.amount}</td>
                    <td>${tx.transaction_type}</td>
                    <td><span class="badge bg-${this.getStatusColor(tx.status)}">${tx.status}</span></td>
                    <td>${new Date(tx.created_at).toLocaleDateString()}</td>
                </tr>
            `).join('');
        }
    },
    
    // Get status color for badges
    getStatusColor: function(status) {
        const colors = {
            'completed': 'success',
            'pending': 'warning', 
            'failed': 'danger',
            'cancelled': 'secondary'
        };
        return colors[status] || 'primary';
    },
    
    // Load system health
    loadSystemHealth: function() {
        fetch('/api/health')
            .then(response => response.json())
            .then(data => {
                this.updateHealthIndicator(data.status === 'healthy');
            })
            .catch(error => {
                this.updateHealthIndicator(false);
                console.error('Health check failed:', error);
            });
    },
    
    // Update health indicator
    updateHealthIndicator: function(isHealthy) {
        const indicator = document.getElementById('health-indicator');
        if (indicator) {
            indicator.className = `status-indicator ${isHealthy ? 'status-active' : 'status-error'}`;
            indicator.title = isHealthy ? 'System is healthy' : 'System issues detected';
        }
    },
    
    // Start health monitoring
    startHealthMonitoring: function() {
        // Check system health every 30 seconds
        setInterval(() => {
            this.loadSystemHealth();
        }, 30000);
    },
    
    // Show success message
    showSuccess: function(message) {
        this.showAlert(message, 'success');
    },
    
    // Show error message
    showError: function(message) {
        this.showAlert(message, 'danger');
    },
    
    // Show warning message
    showWarning: function(message) {
        this.showAlert(message, 'warning');
    },
    
    // Show alert message
    showAlert: function(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const alertContainer = document.getElementById('alert-container') || document.querySelector('main');
        if (alertContainer) {
            const alertDiv = document.createElement('div');
            alertDiv.innerHTML = alertHtml;
            alertContainer.insertBefore(alertDiv.firstElementChild, alertContainer.firstChild);
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                const alert = alertContainer.querySelector('.alert');
                if (alert) {
                    alert.classList.remove('show');
                    setTimeout(() => alert.remove(), 150);
                }
            }, 5000);
        }
    },
    
    // Format currency
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    // Format date
    formatDate: function(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Validate form
    validateForm: function(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });
        
        return isValid;
    },
    
    // Show field error
    showFieldError: function(field, message) {
        field.classList.add('is-invalid');
        let feedback = field.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    },
    
    // Clear field error
    clearFieldError: function(field) {
        field.classList.remove('is-invalid');
        const feedback = field.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.remove();
        }
    }
};

// Initialize GOFAP when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    GOFAP.init();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GOFAP;
}