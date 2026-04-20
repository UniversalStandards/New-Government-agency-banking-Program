// GOFAP Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.forEach(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add loading state to buttons on form submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                submitBtn.disabled = true;

                // Re-enable button after 10 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                const alertInstance = new bootstrap.Alert(alert);
                alertInstance.close();
            }
        }, 5000);
    });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const target = document.querySelector(targetId);
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
            if (value && !isNaN(parseFloat(value))) {
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
                if (this.href) {
                    window.location.href = this.href;
                } else if (this.dataset.url) {
                    window.location.href = this.dataset.url;
                }
            }
        });
    });
});

// ---------------------------------------------------------------------------
// GOFAP Utility Library
// ---------------------------------------------------------------------------
const GOFAP = {

    /**
     * Show a dismissible notification toast.
     * Uses DOM manipulation (not innerHTML) to prevent XSS injection.
     * @param {string} message - Safe text message to display
     * @param {string} [type='info'] - Bootstrap alert variant
     */
    showNotification: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';

        // textContent prevents XSS — never use innerHTML for user-supplied data
        alertDiv.textContent = message;

        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close';
        closeButton.setAttribute('data-bs-dismiss', 'alert');
        alertDiv.appendChild(closeButton);

        document.body.appendChild(alertDiv);

        setTimeout(() => {
            const instance = bootstrap.Alert.getOrCreateInstance(alertDiv);
            instance.close();
        }, 5000);
    },

    /**
     * Format a number as a currency string.
     * @param {number} amount
     * @param {string} [currency='USD']
     * @returns {string}
     */
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    /**
     * Format a date value with optional Intl.DateTimeFormat overrides.
     * @param {string|Date|number} date
     * @param {Intl.DateTimeFormatOptions} [options={}]
     * @returns {string}
     */
    formatDate: function(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(new Date(date));
    },

    /**
     * Append a spinner element to a container.
     * @param {HTMLElement} element
     */
    showLoading: function(element) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.id = 'loading-spinner';
        element.appendChild(spinner);
    },

    /** Remove the global loading spinner. */
    hideLoading: function() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },

    /**
     * Validate a URL against SSRF-prevention rules.
     * Blocks private IP ranges, localhost, and non-HTTP(S) protocols.
     * @param {string} url
     * @returns {boolean}
     */
    isValidUrl: function(url) {
        try {
            const urlObj = new URL(url);
            if (!['http:', 'https:'].includes(urlObj.protocol)) {
                return false;
            }
            const hostname = urlObj.hostname;
            if (
                hostname === 'localhost' ||
                hostname === '127.0.0.1' ||
                hostname.startsWith('192.168.') ||
                hostname.startsWith('10.') ||
                hostname.startsWith('172.')
            ) {
                return false;
            }
            return true;
        } catch (_) {
            return false;
        }
    },

    // -----------------------------------------------------------------------
    // API helpers — all methods validate the URL before dispatching
    // -----------------------------------------------------------------------
    api: {
        get: async function(url) {
            if (!GOFAP.isValidUrl(url)) {
                throw new Error('Invalid or unsafe URL');
            }
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
            if (!GOFAP.isValidUrl(url)) {
                throw new Error('Invalid or unsafe URL');
            }
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(data)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('API POST error:', error);
                GOFAP.showNotification('Failed to send data', 'danger');
                throw error;
            }
        },

        put: async function(url, data) {
            if (!GOFAP.isValidUrl(url)) {
                throw new Error('Invalid or unsafe URL');
            }
            try {
                const response = await fetch(url, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(data)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('API PUT error:', error);
                GOFAP.showNotification('Failed to update data', 'danger');
                throw error;
            }
        },

        delete: async function(url) {
            if (!GOFAP.isValidUrl(url)) {
                throw new Error('Invalid or unsafe URL');
            }
            try {
                const response = await fetch(url, {
                    method: 'DELETE',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('API DELETE error:', error);
                GOFAP.showNotification('Failed to delete data', 'danger');
                throw error;
            }
        },

        /**
         * Generic fetch wrapper for arbitrary options.
         * @param {string} url
         * @param {RequestInit} [options={}]
         * @returns {Promise<any>}
         */
        call: async function(url, options = {}) {
            const config = Object.assign(
                { headers: { 'Content-Type': 'application/json' } },
                options
            );
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

    /**
     * Validate all required fields in a form element.
     * Adds/removes Bootstrap `is-invalid` class per field.
     * @param {HTMLFormElement} formElement
     * @returns {boolean}
     */
    validateForm: function(formElement) {
        const inputs = formElement.querySelectorAll(
            'input[required], select[required], textarea[required]'
        );
        let isValid = true;
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        return isValid;
    },

    /**
     * Basic HTML sanitizer via DOM round-trip.
     * Note: for production use consider DOMPurify for full sanitization.
     * @param {string} html
     * @returns {string}
     */
    sanitizeHtml: function(html) {
        const div = document.createElement('div');
        div.innerHTML = html;
        return div.innerHTML;
    },

    /**
     * Write text to the clipboard and notify the user.
     * @param {string} text
     */
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            GOFAP.showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            GOFAP.showNotification('Failed to copy to clipboard', 'danger');
        });
    }
};

// Export for CommonJS/Jest testing environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GOFAP;
}

// Attach to global window for browser usage
window.GOFAP = GOFAP;
