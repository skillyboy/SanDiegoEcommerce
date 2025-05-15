/**
 * Cart Email Handler
 * This script handles email collection when adding to cart
 */

const CartEmailHandler = {
    /**
     * Initialize the handler
     */
    init: function() {
        // Set up event listeners
        this.setupEventListeners();
    },

    /**
     * Set up event listeners
     */
    setupEventListeners: function() {
        // Listen for add to cart button clicks
        document.addEventListener('click', function(event) {
            // Check if the clicked element is an add to cart button
            if (event.target.classList.contains('btn-add-to-cart') ||
                event.target.classList.contains('btn-add-to-cart-nigerian')) {
                // Get product ID from data attribute or parent element
                const productId = event.target.getAttribute('data-product-id') ||
                                 event.target.closest('[data-product-id]')?.getAttribute('data-product-id');

                if (productId) {
                    // Prevent default action
                    event.preventDefault();

                    // Show email collection modal if user is not logged in
                    CartEmailHandler.handleAddToCart(productId);
                }
            }
        });
    },

    /**
     * Handle add to cart action
     * @param {string} productId - The ID of the product to add to cart
     */
    handleAddToCart: function(productId) {
        // Check if user is logged in
        const isLoggedIn = document.body.classList.contains('user-logged-in');

        if (isLoggedIn) {
            // User is logged in, add to cart directly
            this.addToCart(productId);
        } else {
            // User is not logged in, show email collection modal
            this.showEmailModal(productId);
        }
    },

    /**
     * Show email collection modal
     * @param {string} productId - The ID of the product to add to cart
     */
    showEmailModal: function(productId) {
        // Get the email collection modal
        const modal = document.getElementById('emailCollectionModal');

        if (modal) {
            // Set product ID in hidden field
            const productIdField = modal.querySelector('input[name="product_id"]');
            if (productIdField) {
                productIdField.value = productId;
            }

            // Show the modal
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();

            // Set up form submission
            const form = modal.querySelector('form');
            if (form) {
                form.addEventListener('submit', function(event) {
                    event.preventDefault();

                    // Get email from form safely
                    const emailInput = form.querySelector('input[name="email"]');
                    const email = emailInput ? emailInput.value : '';

                    // Check if email is valid
                    if (!email) {
                        console.error('Email input not found or empty');
                        // Fallback to using the emailCollectionEmail input
                        const alternativeInput = document.getElementById('emailCollectionEmail');
                        if (alternativeInput && alternativeInput.value) {
                            CartEmailHandler.addToCartWithEmail(productId, alternativeInput.value);
                        } else {
                            // If no email found, add to cart without email
                            CartEmailHandler.addToCart(productId);
                        }
                    } else {
                        // Add to cart with email
                        CartEmailHandler.addToCartWithEmail(productId, email);
                    }

                    // Hide the modal safely using multiple fallback methods
                    try {
                        bootstrapModal.hide();
                    } catch (error) {
                        console.error('Error hiding modal with bootstrapModal:', error);

                        // Try other methods
                        const emailModal = document.getElementById('emailCollectionModal');
                        if (emailModal) {
                            if (window.ModalManager) {
                                window.ModalManager.hide(emailModal);
                            } else if (bootstrap && bootstrap.Modal && bootstrap.Modal.hideModal) {
                                bootstrap.Modal.hideModal(emailModal);
                            } else if (typeof $ !== 'undefined') {
                                $(emailModal).modal('hide');
                            } else {
                                // Last resort: manual DOM manipulation
                                emailModal.classList.remove('show');
                                emailModal.style.display = 'none';
                                document.body.classList.remove('modal-open');

                                // Remove backdrop if exists
                                const backdrop = document.querySelector('.modal-backdrop');
                                if (backdrop && backdrop.parentNode) {
                                    backdrop.parentNode.removeChild(backdrop);
                                }
                            }
                        }
                    }
                });
            }
        } else {
            // Modal not found, add to cart directly
            this.addToCart(productId);
        }
    },

    /**
     * Add to cart with email
     * @param {string} productId - The ID of the product to add to cart
     * @param {string} email - The email address to associate with the cart
     */
    addToCartWithEmail: function(productId, email) {
        // Create form data
        const formData = new FormData();
        formData.append('email', email);
        formData.append('csrfmiddlewaretoken', this.getCSRFToken());

        // Send AJAX request
        fetch(`/add_to_cart/${productId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            // Check if response is ok (status in the range 200-299)
            if (!response.ok) {
                // If we get a 500 error, show a specific message
                if (response.status === 500) {
                    throw new Error('Server error: The server encountered an issue. This might be due to a missing customer table or database configuration.');
                }
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Show success message
                this.showSuccessMessage(data.message);

                // Update cart count
                this.updateCartCount(data.cart_count);

                // Play success sound
                this.playSuccessSound();
            } else {
                // Show error message
                this.showErrorMessage(data.message || 'Error adding to cart');
            }
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
            this.showErrorMessage(error.message || 'Error adding to cart. Please try again.');
        });
    },

    /**
     * Add to cart without email
     * @param {string} productId - The ID of the product to add to cart
     */
    addToCart: function(productId) {
        // Create form data
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.getCSRFToken());

        // Send AJAX request
        fetch(`/add_to_cart/${productId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            // Check if response is ok (status in the range 200-299)
            if (!response.ok) {
                // If we get a 500 error, show a specific message
                if (response.status === 500) {
                    throw new Error('Server error: The server encountered an issue. This might be due to a missing customer table or database configuration.');
                }
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Show success message
                this.showSuccessMessage(data.message);

                // Update cart count
                this.updateCartCount(data.cart_count);

                // Play success sound
                this.playSuccessSound();
            } else {
                // Show error message
                this.showErrorMessage(data.message || 'Error adding to cart');
            }
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
            this.showErrorMessage(error.message || 'Error adding to cart. Please try again.');
        });
    },

    /**
     * Get CSRF token
     * @returns {string} The CSRF token
     */
    getCSRFToken: function() {
        return document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';
    },

    /**
     * Show success message
     * @param {string} message - The success message to show
     */
    showSuccessMessage: function(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Success!',
                text: message,
                icon: 'success',
                timer: 2000,
                showConfirmButton: false
            });
        } else if (typeof toast !== 'undefined') {
            toast.success(message);
        } else {
            alert(message);
        }
    },

    /**
     * Show error message
     * @param {string} message - The error message to show
     */
    showErrorMessage: function(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Error!',
                text: message,
                icon: 'error'
            });
        } else if (typeof toast !== 'undefined') {
            toast.error(message);
        } else {
            alert(message);
        }
    },

    /**
     * Update cart count
     * @param {number} count - The new cart count
     */
    updateCartCount: function(count) {
        // Update cart count in header
        const cartCountElements = document.querySelectorAll('.cart-count');
        cartCountElements.forEach(element => {
            element.textContent = count;
        });
    },

    /**
     * Play success sound
     */
    playSuccessSound: function() {
        try {
            const audio = new Audio('/static/sounds/success.mp3');
            audio.play();
        } catch (error) {
            console.error('Error playing success sound:', error);
        }
    }
};

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    CartEmailHandler.init();
});
