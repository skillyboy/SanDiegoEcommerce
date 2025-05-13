/**
 * Enhanced Modern Toast Notifications for African Food San Diego
 * This script handles the creation and management of toast notifications with modern UI/UX
 */

// Enhanced Toast Notification System
class ToastNotification {
    constructor() {
        this.container = null;
        this.defaultDuration = 5000; // 5 seconds
        this.maxToasts = 3; // Maximum number of toasts to show at once
        this.toasts = []; // Array to track active toasts
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }

        // Add sound effects for notifications
        this.sounds = {
            success: new Audio('/static/sounds/success.mp3'),
            error: new Audio('/static/sounds/error.mp3'),
            info: new Audio('/static/sounds/info.mp3')
        };

        // Set volume
        Object.values(this.sounds).forEach(sound => {
            sound.volume = 0.3;
        });
    }

    /**
     * Show a toast notification with enhanced features
     * @param {Object} options - Toast options
     * @param {string} options.title - Toast title
     * @param {string} options.message - Toast message
     * @param {string} options.type - Toast type (success, error, info)
     * @param {number} options.duration - Duration in milliseconds
     * @param {Object} options.product - Product information (optional)
     * @param {string} options.product.name - Product name
     * @param {string} options.product.image - Product image URL
     * @param {string} options.product.price - Product price
     * @param {string} options.product.link - Product link URL
     * @param {Array} options.actions - Array of action buttons (optional)
     * @param {string} options.actions[].id - Button ID
     * @param {string} options.actions[].text - Button text
     * @param {string} options.actions[].class - Button class
     * @param {Function} options.actions[].callback - Button callback function
     * @param {boolean} options.playSound - Whether to play sound (default: true)
     */
    show(options) {
        const {
            title = 'Notification',
            message = '',
            type = 'success',
            duration = this.defaultDuration,
            product = null,
            actions = [],
            playSound = true
        } = options;

        // Manage maximum number of toasts
        if (this.toasts.length >= this.maxToasts) {
            // Close the oldest toast
            this.close(this.toasts[0]);
        }

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');

        // Create toast content with enhanced structure
        let toastContent = `
            <div class="toast-header">
                <h5 class="toast-title">${title}</h5>
                <button class="toast-close" aria-label="Close">&times;</button>
            </div>
            <div class="toast-body">
                <p class="toast-message">${message}</p>
        `;

        // Add product information if provided with enhanced styling
        if (product) {
            toastContent += `
                <div class="toast-product" ${product.link ? `data-link="${product.link}"` : ''}>
                    <img src="${product.image}" alt="${product.name}" class="toast-product-image">
                    <div class="toast-product-info">
                        <h6 class="toast-product-name">${product.name}</h6>
                        <p class="toast-product-price">${product.price}</p>
                    </div>
                    ${product.link ? '<div class="toast-view-indicator"><i class="fas fa-external-link-alt"></i> View in Cart</div>' : ''}
                </div>
            `;
        }

        // Add action buttons if provided with enhanced styling
        if (actions.length > 0) {
            toastContent += '<div class="toast-actions">';
            actions.forEach(action => {
                toastContent += `<button class="toast-btn ${action.class || ''}" data-action="${action.id}">${action.text}</button>`;
            });
            toastContent += '</div>';
        }

        // Add progress bar with enhanced styling
        toastContent += `
                <div class="toast-progress"></div>
            </div>
        `;

        // Set toast content
        toast.innerHTML = toastContent;

        // Add toast to container
        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Play sound effect if enabled
        if (playSound && this.sounds[type]) {
            try {
                this.sounds[type].play().catch(e => console.log('Sound play error:', e));
            } catch (e) {
                console.log('Sound error:', e);
            }
        }

        // Animate progress bar
        const progressBar = toast.querySelector('.toast-progress');
        progressBar.style.transition = `width ${duration}ms linear`;

        // Show toast with enhanced animation
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                toast.classList.add('show');
                progressBar.style.width = '0';
            });
        });

        // Set up close button
        const closeButton = toast.querySelector('.toast-close');
        closeButton.addEventListener('click', () => {
            this.close(toast);
        });

        // Set up action buttons with enhanced interaction
        actions.forEach(action => {
            const actionButton = toast.querySelector(`[data-action="${action.id}"]`);
            if (actionButton && action.callback) {
                actionButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    action.callback();
                    this.close(toast);
                });
            }
        });

        // Make product section clickable if link provided
        const productSection = toast.querySelector('.toast-product');
        if (productSection && product && product.link) {
            productSection.style.cursor = 'pointer';
            productSection.addEventListener('click', () => {
                window.location.href = product.link;
            });
        }

        // Auto close after duration
        const autoCloseTimeout = setTimeout(() => {
            this.close(toast);
        }, duration);

        // Store timeout ID on toast element
        toast.dataset.timeoutId = autoCloseTimeout;

        // Pause progress on hover for better UX
        toast.addEventListener('mouseenter', () => {
            progressBar.style.transition = 'none';
            clearTimeout(toast.dataset.timeoutId);
        });

        // Resume progress on mouse leave
        toast.addEventListener('mouseleave', () => {
            const remainingTime = duration * (parseFloat(getComputedStyle(progressBar).width) / parseFloat(getComputedStyle(toast).width));
            progressBar.style.transition = `width ${remainingTime}ms linear`;
            progressBar.style.width = '0';

            toast.dataset.timeoutId = setTimeout(() => {
                this.close(toast);
            }, remainingTime);
        });

        return toast;
    }

    /**
     * Close a toast notification with enhanced animation
     * @param {HTMLElement} toast - Toast element to close
     */
    close(toast) {
        // Clear timeout
        clearTimeout(toast.dataset.timeoutId);

        // Hide toast with enhanced animation
        toast.classList.add('hide');

        // Remove toast after animation
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
                // Remove from tracked toasts
                this.toasts = this.toasts.filter(t => t !== toast);
            }
        }, 500);
    }

    /**
     * Show a success toast notification
     * @param {string} message - Toast message
     * @param {Object} options - Additional options
     */
    success(message, options = {}) {
        return this.show({
            title: options.title || 'Success',
            message,
            type: 'success',
            ...options
        });
    }

    /**
     * Show an error toast notification
     * @param {string} message - Toast message
     * @param {Object} options - Additional options
     */
    error(message, options = {}) {
        return this.show({
            title: options.title || 'Error',
            message,
            type: 'error',
            ...options
        });
    }

    /**
     * Show an info toast notification
     * @param {string} message - Toast message
     * @param {Object} options - Additional options
     */
    info(message, options = {}) {
        return this.show({
            title: options.title || 'Information',
            message,
            type: 'info',
            ...options
        });
    }

    /**
     * Show an enhanced cart notification
     * @param {Object} product - Product information
     * @param {string} message - Toast message
     */
    cart(product, message = 'Product added to cart') {
        return this.success(message, {
            title: 'Added to Cart',
            product,
            actions: [
                {
                    id: 'view-cart',
                    text: 'View Cart',
                    class: 'toast-btn-primary',
                    callback: () => {
                        window.location.href = '/cart/';
                    }
                },
                {
                    id: 'continue-shopping',
                    text: 'Continue Shopping',
                    callback: () => {}
                }
            ]
        });
    }

    /**
     * Show an enhanced cart error notification
     * @param {string} message - Error message
     * @param {Object} options - Additional options
     */
    cartError(message, options = {}) {
        return this.error(message, {
            title: options.title || 'Cart Error',
            duration: 7000, // Show error for longer
            actions: [
                {
                    id: 'try-again',
                    text: 'Try Again',
                    class: 'toast-btn-primary',
                    callback: options.retryCallback || (() => {})
                },
                {
                    id: 'view-cart',
                    text: 'View Cart',
                    callback: () => {
                        window.location.href = '/cart/';
                    }
                }
            ]
        });
    }

    /**
     * Show an enhanced loading notification with spinner
     * @param {string} message - Toast message
     */
    loading(message = 'Processing...') {
        const toast = this.show({
            title: 'Please Wait',
            message,
            type: 'info',
            duration: 30000, // Long duration for loading
            playSound: false // Don't play sound for loading
        });

        // Add enhanced loading spinner
        const toastBody = toast.querySelector('.toast-body');
        const loadingSpinner = document.createElement('div');
        loadingSpinner.className = 'loading-spinner';
        loadingSpinner.innerHTML = `
            <div class="spinner"></div>
        `;
        toastBody.appendChild(loadingSpinner);

        // Add CSS for enhanced spinner
        if (!document.getElementById('spinner-style')) {
            const style = document.createElement('style');
            style.id = 'spinner-style';
            style.textContent = `
                .loading-spinner {
                    display: flex;
                    justify-content: center;
                    margin-top: 15px;
                }
                .spinner {
                    width: 30px;
                    height: 30px;
                    border: 3px solid rgba(0, 135, 81, 0.1);
                    border-radius: 50%;
                    border-top-color: #008751;
                    animation: spin 1s cubic-bezier(0.68, -0.55, 0.27, 1.55) infinite;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }

        return toast;
    }

    /**
     * Show a login required notification
     * @param {string} message - Toast message
     */
    loginRequired(message = 'Please log in to continue') {
        return this.info(message, {
            title: 'Login Required',
            actions: [
                {
                    id: 'login',
                    text: 'Login',
                    class: 'toast-btn-primary',
                    callback: () => {
                        window.location.href = '/accounts/login/?next=' + window.location.pathname;
                    }
                },
                {
                    id: 'signup',
                    text: 'Sign Up',
                    callback: () => {
                        window.location.href = '/signup/?next=' + window.location.pathname;
                    }
                }
            ]
        });
    }
}

// Initialize enhanced toast notification system
const toast = new ToastNotification();
