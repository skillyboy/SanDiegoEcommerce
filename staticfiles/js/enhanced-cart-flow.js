/**
 * Enhanced Cart Flow
 * Provides a smoother add-to-cart experience with improved email collection
 */

// Global variables
let isAddingToCart = false;
let emailCollected = false;
let pendingCartAction = null;

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    EnhancedCartFlow.init();
});

const EnhancedCartFlow = {
    /**
     * Initialize the enhanced cart flow
     */
    init: function() {
        console.log('Initializing Enhanced Cart Flow');
        
        // Check if email is already collected
        this.checkEmailStatus();
        
        // Add animation styles
        this.addAnimationStyles();
        
        // Override existing cart functions
        this.overrideCartFunctions();
        
        console.log('Enhanced Cart Flow initialized');
    },
    
    /**
     * Check if email is already collected
     */
    checkEmailStatus: function() {
        // Check session storage
        const storedEmail = sessionStorage.getItem('guest_user_email');
        if (storedEmail) {
            emailCollected = true;
            console.log('Email already collected from session storage');
        }
        
        // Also check if user is authenticated
        const isAuthenticated = document.body.classList.contains('user-authenticated');
        if (isAuthenticated) {
            emailCollected = true;
            console.log('User is authenticated, no need to collect email');
        }
    },
    
    /**
     * Add animation styles
     */
    addAnimationStyles: function() {
        if (!document.getElementById('enhanced-cart-styles')) {
            const styleElement = document.createElement('style');
            styleElement.id = 'enhanced-cart-styles';
            styleElement.textContent = `
                /* Flying item animation */
                @keyframes flyToCart {
                    0% { transform: scale(1); opacity: 1; }
                    70% { transform: scale(0.5); opacity: 0.8; }
                    100% { transform: scale(0.3); opacity: 0; }
                }
                
                /* Cart icon animation */
                @keyframes cartBounce {
                    0% { transform: scale(1); }
                    40% { transform: scale(1.2); }
                    60% { transform: scale(0.9); }
                    80% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
                
                /* Add to cart button animation */
                @keyframes addedToCart {
                    0% { background-color: #008751; }
                    50% { background-color: #28a745; }
                    100% { background-color: #008751; }
                }
                
                /* Cart count animation */
                @keyframes countPulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.3); }
                    100% { transform: scale(1); }
                }
                
                /* Email collection modal animation */
                .email-modal-enter {
                    animation: modalEnter 0.4s ease-out;
                }
                
                @keyframes modalEnter {
                    0% { transform: translateY(20px); opacity: 0; }
                    100% { transform: translateY(0); opacity: 1; }
                }
                
                /* Flying cart item */
                .flying-cart-item {
                    position: fixed;
                    z-index: 9999;
                    border-radius: 50%;
                    background-size: cover;
                    background-position: center;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    pointer-events: none;
                }
                
                /* Cart button animation */
                .cart-button-bounce {
                    animation: cartBounce 0.6s ease;
                }
                
                /* Cart count animation */
                .cart-count-pulse {
                    animation: countPulse 0.6s ease;
                }
                
                /* Added to cart button state */
                .added-to-cart {
                    background-color: #28a745 !important;
                    color: white !important;
                    animation: addedToCart 1s ease;
                }
                
                /* Email collection modal */
                .email-collection-modal {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    padding: 0;
                    overflow: hidden;
                    max-width: 400px;
                    width: 100%;
                    position: relative;
                }
                
                .email-modal-header {
                    background: linear-gradient(135deg, #008751, #006B3C);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    position: relative;
                }
                
                .email-modal-body {
                    padding: 20px;
                }
                
                .email-modal-footer {
                    padding: 15px 20px;
                    display: flex;
                    justify-content: space-between;
                    border-top: 1px solid #eee;
                }
            `;
            document.head.appendChild(styleElement);
        }
    },
    
    /**
     * Override existing cart functions
     */
    overrideCartFunctions: function() {
        // Override addToCartWithEmail function
        if (typeof window.addToCartWithEmail === 'function') {
            window.originalAddToCartWithEmail = window.addToCartWithEmail;
            window.addToCartWithEmail = this.addToCartWithEmail;
        }
        
        // Override addToCartWithAnimation function
        if (typeof window.addToCartWithAnimation === 'function') {
            window.originalAddToCartWithAnimation = window.addToCartWithAnimation;
            window.addToCartWithAnimation = this.addToCartWithAnimation;
        }
    },
    
    /**
     * Enhanced add to cart with email collection
     * @param {number} productId - The product ID
     * @param {number} quantity - The quantity to add
     */
    addToCartWithEmail: function(productId, quantity = 1) {
        // Prevent multiple clicks
        if (isAddingToCart) {
            console.log('Already adding to cart, please wait...');
            return;
        }
        
        isAddingToCart = true;
        
        // If email already collected, add to cart directly
        if (emailCollected) {
            EnhancedCartFlow.addToCart(productId, quantity);
            return;
        }
        
        // Store pending action
        pendingCartAction = { productId, quantity };
        
        // Show email collection modal
        EnhancedCartFlow.showEmailCollectionModal();
    },
    
    /**
     * Show email collection modal
     */
    showEmailCollectionModal: function() {
        // Create modal if it doesn't exist
        if (!document.getElementById('enhanced-email-modal')) {
            const modalHtml = `
                <div id="enhanced-email-modal" class="email-collection-modal email-modal-enter">
                    <div class="email-modal-header">
                        <h4>Quick Checkout</h4>
                        <p class="mb-0">Enter your email to continue shopping</p>
                    </div>
                    <div class="email-modal-body">
                        <div class="form-group mb-3">
                            <label for="email-input">Email Address</label>
                            <input type="email" id="email-input" class="form-control" placeholder="your@email.com" required>
                            <div id="email-error" class="invalid-feedback">Please enter a valid email address</div>
                        </div>
                        <div class="form-check mb-3">
                            <input class="form-check-input" type="checkbox" id="newsletter-checkbox" checked>
                            <label class="form-check-label" for="newsletter-checkbox">
                                Subscribe to our newsletter for exclusive offers
                            </label>
                        </div>
                    </div>
                    <div class="email-modal-footer">
                        <button id="email-modal-cancel" class="btn btn-outline-secondary">Cancel</button>
                        <button id="email-modal-submit" class="btn btn-primary">Continue</button>
                    </div>
                </div>
            `;
            
            // Create modal container
            const modalContainer = document.createElement('div');
            modalContainer.id = 'enhanced-email-modal-container';
            modalContainer.style.position = 'fixed';
            modalContainer.style.top = '0';
            modalContainer.style.left = '0';
            modalContainer.style.width = '100%';
            modalContainer.style.height = '100%';
            modalContainer.style.backgroundColor = 'rgba(0,0,0,0.5)';
            modalContainer.style.display = 'flex';
            modalContainer.style.alignItems = 'center';
            modalContainer.style.justifyContent = 'center';
            modalContainer.style.zIndex = '9999';
            modalContainer.style.opacity = '0';
            modalContainer.style.transition = 'opacity 0.3s ease';
            modalContainer.innerHTML = modalHtml;
            
            document.body.appendChild(modalContainer);
            
            // Add event listeners
            document.getElementById('email-modal-cancel').addEventListener('click', this.hideEmailCollectionModal);
            document.getElementById('email-modal-submit').addEventListener('click', this.submitEmailForm);
            document.getElementById('email-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    EnhancedCartFlow.submitEmailForm();
                }
            });
            
            // Show modal with animation
            setTimeout(() => {
                modalContainer.style.opacity = '1';
            }, 10);
        } else {
            // Show existing modal
            const modalContainer = document.getElementById('enhanced-email-modal-container');
            modalContainer.style.display = 'flex';
            setTimeout(() => {
                modalContainer.style.opacity = '1';
            }, 10);
        }
        
        // Focus email input
        setTimeout(() => {
            document.getElementById('email-input').focus();
        }, 300);
    },
    
    /**
     * Hide email collection modal
     */
    hideEmailCollectionModal: function() {
        const modalContainer = document.getElementById('enhanced-email-modal-container');
        if (modalContainer) {
            modalContainer.style.opacity = '0';
            setTimeout(() => {
                modalContainer.style.display = 'none';
                
                // Reset pending action
                pendingCartAction = null;
                isAddingToCart = false;
            }, 300);
        }
    },
    
    /**
     * Submit email form
     */
    submitEmailForm: function() {
        // Get email and newsletter subscription
        const emailInput = document.getElementById('email-input');
        const email = emailInput.value.trim();
        const subscribeToNewsletter = document.getElementById('newsletter-checkbox').checked;
        
        // Validate email
        if (!email || !EnhancedCartFlow.isValidEmail(email)) {
            emailInput.classList.add('is-invalid');
            return;
        }
        
        // Remove error state
        emailInput.classList.remove('is-invalid');
        
        // Show loading state
        const submitButton = document.getElementById('email-modal-submit');
        const originalButtonText = submitButton.textContent;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Saving...';
        submitButton.disabled = true;
        
        // Save email to session
        EnhancedCartFlow.saveEmailToSession(email, subscribeToNewsletter)
            .then(response => {
                if (response.success) {
                    // Set email collected flag
                    emailCollected = true;
                    
                    // Hide modal
                    EnhancedCartFlow.hideEmailCollectionModal();
                    
                    // Execute pending cart action
                    if (pendingCartAction) {
                        EnhancedCartFlow.addToCart(pendingCartAction.productId, pendingCartAction.quantity);
                        pendingCartAction = null;
                    }
                } else {
                    // Show error
                    emailInput.classList.add('is-invalid');
                    document.getElementById('email-error').textContent = response.message || 'Failed to save email';
                    
                    // Reset button
                    submitButton.innerHTML = originalButtonText;
                    submitButton.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error saving email:', error);
                
                // Show error
                emailInput.classList.add('is-invalid');
                document.getElementById('email-error').textContent = 'An error occurred. Please try again.';
                
                // Reset button
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            });
    },
    
    /**
     * Save email to session
     * @param {string} email - The email to save
     * @param {boolean} subscribeToNewsletter - Whether to subscribe to newsletter
     * @returns {Promise} - Promise that resolves with the response
     */
    saveEmailToSession: function(email, subscribeToNewsletter) {
        return new Promise((resolve, reject) => {
            // Save to session storage first (client-side)
            sessionStorage.setItem('guest_user_email', email);
            
            // Make AJAX request to save on server
            fetch('/save_guest_email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    'email': email,
                    'subscribe': subscribeToNewsletter
                })
            })
            .then(response => response.json())
            .then(data => resolve(data))
            .catch(error => {
                console.error('Error saving email:', error);
                // Still resolve with success since we saved to session storage
                resolve({ success: true, message: 'Email saved to session storage' });
            });
        });
    },
    
    /**
     * Add to cart
     * @param {number} productId - The product ID
     * @param {number} quantity - The quantity to add
     */
    addToCart: function(productId, quantity = 1) {
        // Show loading state
        const addToCartBtn = document.querySelector(`.btn-add-to-cart-nigerian[onclick*="${productId}"], .btn-add-to-cart[onclick*="${productId}"]`);
        if (addToCartBtn) {
            const originalButtonText = addToCartBtn.innerHTML;
            addToCartBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
            addToCartBtn.disabled = true;
        }
        
        // Add flying animation
        EnhancedCartFlow.addToCartAnimation(productId);
        
        // Make AJAX request
        fetch(`/add_to_cart/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                'quantity': quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            // Reset flag
            isAddingToCart = false;
            
            if (data.success) {
                // Update cart count
                EnhancedCartFlow.updateCartCount(data.cart_count);
                
                // Show success state on button
                if (addToCartBtn) {
                    addToCartBtn.innerHTML = '<i class="fas fa-check me-2"></i> Added';
                    addToCartBtn.classList.add('added-to-cart');
                    
                    // Reset button after delay
                    setTimeout(() => {
                        addToCartBtn.innerHTML = originalButtonText;
                        addToCartBtn.classList.remove('added-to-cart');
                        addToCartBtn.disabled = false;
                    }, 2000);
                }
                
                // Show success toast
                EnhancedCartFlow.showToast(data.message || 'Product added to cart successfully!', 'success');
            } else {
                // Reset button
                if (addToCartBtn) {
                    addToCartBtn.innerHTML = originalButtonText;
                    addToCartBtn.disabled = false;
                }
                
                // Show error toast
                EnhancedCartFlow.showToast(data.message || 'Failed to add product to cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
            
            // Reset flag
            isAddingToCart = false;
            
            // Reset button
            if (addToCartBtn) {
                addToCartBtn.innerHTML = originalButtonText;
                addToCartBtn.disabled = false;
            }
            
            // Show error toast
            EnhancedCartFlow.showToast('An error occurred. Please try again.', 'error');
        });
    },
    
    /**
     * Add to cart animation
     * @param {number} productId - The product ID
     */
    addToCartWithAnimation: function(productId, quantity = 1) {
        // Just call addToCartWithEmail
        EnhancedCartFlow.addToCartWithEmail(productId, quantity);
    },
    
    /**
     * Add flying animation to cart
     * @param {number} productId - The product ID
     */
    addToCartAnimation: function(productId) {
        // Find product card
        const productCard = document.querySelector(`[data-product-id="${productId}"]`);
        if (!productCard) return;
        
        // Find cart button
        const cartButton = document.querySelector('.cart-button-count');
        if (!cartButton) return;
        
        // Find product image
        const productImg = productCard.querySelector('img');
        if (!productImg) return;
        
        // Get positions
        const imgRect = productImg.getBoundingClientRect();
        const cartRect = cartButton.getBoundingClientRect();
        
        // Create flying element
        const flyingImg = document.createElement('div');
        flyingImg.className = 'flying-cart-item';
        flyingImg.style.backgroundImage = `url(${productImg.src})`;
        flyingImg.style.width = '50px';
        flyingImg.style.height = '50px';
        flyingImg.style.top = `${imgRect.top}px`;
        flyingImg.style.left = `${imgRect.left}px`;
        
        // Add to body
        document.body.appendChild(flyingImg);
        
        // Force reflow
        flyingImg.offsetWidth;
        
        // Add transition
        flyingImg.style.transition = 'all 0.8s cubic-bezier(0.18, 0.89, 0.32, 1.28)';
        
        // Start animation
        flyingImg.style.top = `${cartRect.top + 10}px`;
        flyingImg.style.left = `${cartRect.left + 10}px`;
        flyingImg.style.width = '20px';
        flyingImg.style.height = '20px';
        flyingImg.style.opacity = '0';
        
        // Add cart button animation
        setTimeout(() => {
            cartButton.classList.add('cart-button-bounce');
            
            // Remove flying element
            setTimeout(() => {
                if (document.body.contains(flyingImg)) {
                    document.body.removeChild(flyingImg);
                }
                
                // Remove animation class
                cartButton.classList.remove('cart-button-bounce');
            }, 800);
        }, 500);
    },
    
    /**
     * Update cart count
     * @param {number} count - The new cart count
     */
    updateCartCount: function(count) {
        // Find cart count element
        const cartCount = document.getElementById('cart-button-count');
        if (cartCount) {
            // Update count
            cartCount.textContent = count;
            
            // Add animation
            cartCount.classList.add('cart-count-pulse');
            
            // Remove animation after delay
            setTimeout(() => {
                cartCount.classList.remove('cart-count-pulse');
            }, 600);
        }
    },
    
    /**
     * Show toast notification
     * @param {string} message - The message to show
     * @param {string} type - The type of toast (success, error, info)
     */
    showToast: function(message, type) {
        // Check if toast container exists
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            // Create toast container
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.position = 'fixed';
            toastContainer.style.top = '20px';
            toastContainer.style.right = '20px';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast
        const toast = document.createElement('div');
        toast.className = 'toast show';
        toast.style.minWidth = '250px';
        toast.style.background = type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8';
        toast.style.color = 'white';
        toast.style.borderRadius = '4px';
        toast.style.padding = '12px 20px';
        toast.style.marginBottom = '10px';
        toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        toast.style.display = 'flex';
        toast.style.alignItems = 'center';
        toast.style.justifyContent = 'space-between';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        toast.style.transition = 'all 0.3s ease';
        
        // Add icon based on type
        const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle';
        
        // Set toast content
        toast.innerHTML = `
            <div style="display: flex; align-items: center;">
                <i class="fas fa-${icon} me-2"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white" style="font-size: 0.8rem; background: none; border: none; color: white; cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Show with animation
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);
        
        // Add close button event
        toast.querySelector('.btn-close').addEventListener('click', function() {
            hideToast(toast);
        });
        
        // Auto hide after delay
        setTimeout(() => {
            hideToast(toast);
        }, type === 'error' ? 5000 : 3000);
        
        // Hide toast function
        function hideToast(toastElement) {
            toastElement.style.opacity = '0';
            toastElement.style.transform = 'translateY(-20px)';
            
            setTimeout(() => {
                if (toastContainer.contains(toastElement)) {
                    toastContainer.removeChild(toastElement);
                }
                
                // Remove container if empty
                if (toastContainer.children.length === 0) {
                    document.body.removeChild(toastContainer);
                }
            }, 300);
        }
    },
    
    /**
     * Validate email
     * @param {string} email - The email to validate
     * @returns {boolean} - Whether the email is valid
     */
    isValidEmail: function(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }
};
