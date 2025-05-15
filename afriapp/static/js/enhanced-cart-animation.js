/**
 * Enhanced Cart Animation
 * This script provides improved animations for adding products to cart
 */

// Global variables to prevent multiple animations at once
let isCartAnimationRunning = false;

/**
 * Add to cart with enhanced bucket animation
 * @param {number} productId - The product ID
 * @param {number} quantity - The quantity to add (default: 1)
 */
function addToCartWithBucketAnimation(productId, quantity = 1) {
    // Prevent multiple animations
    if (isCartAnimationRunning) {
        return;
    }

    isCartAnimationRunning = true;

    // First, collect email if needed
    addToCartWithEmail(productId, quantity);
}

/**
 * Enhanced animation for adding product to cart
 * @param {number} productId - The product ID
 * @param {number} quantity - The quantity to add
 * @param {string} email - The user's email
 */
function enhancedCartAnimation(productId, quantity = 1, email = null) {
    console.log('Running enhanced cart animation for product:', productId);

    // Get the product element
    const productElement = document.querySelector(`[data-product-id="${productId}"]`);
    if (!productElement) {
        console.log('Product element not found, proceeding without animation');
        makeAddToCartRequest(productId, quantity, email);
        return;
    }

    // Get product image
    const productImg = productElement.querySelector('.product-img');
    if (!productImg) {
        console.log('Product image not found, proceeding without animation');
        makeAddToCartRequest(productId, quantity, email);
        return;
    }

    // Get cart icon position
    const cartIcon = document.querySelector('.navbar .fa-shopping-cart');
    if (!cartIcon) {
        console.log('Cart icon not found, proceeding without animation');
        makeAddToCartRequest(productId, quantity, email);
        return;
    }

    // Get product details for toast notification
    const productName = productElement.querySelector('.product-title a')?.textContent || 'Product';
    const productPrice = productElement.querySelector('.price-current')?.textContent || '';

    // Create flying element (product image)
    const flyingElement = document.createElement('div');
    flyingElement.className = 'flying-product';

    // Position the flying element at the product image position
    const imgRect = productImg.getBoundingClientRect();
    flyingElement.style.position = 'fixed';
    flyingElement.style.zIndex = '9999';
    flyingElement.style.width = '80px';
    flyingElement.style.height = '80px';
    flyingElement.style.borderRadius = '50%';
    flyingElement.style.backgroundImage = `url(${productImg.src})`;
    flyingElement.style.backgroundSize = 'cover';
    flyingElement.style.backgroundPosition = 'center';
    flyingElement.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
    flyingElement.style.transition = 'all 0.8s cubic-bezier(0.18, 0.89, 0.32, 1.28)';
    flyingElement.style.left = `${imgRect.left + imgRect.width/2 - 40}px`;
    flyingElement.style.top = `${imgRect.top + imgRect.height/2 - 40}px`;

    // Add to DOM
    document.body.appendChild(flyingElement);

    // Create bucket animation elements
    const bucket = document.createElement('div');
    bucket.className = 'cart-bucket';
    bucket.style.position = 'fixed';
    bucket.style.zIndex = '9998';
    bucket.style.width = '50px';
    bucket.style.height = '50px';
    bucket.style.borderRadius = '50% 50% 10% 10%';
    bucket.style.background = 'linear-gradient(to bottom, rgba(210, 105, 30, 0.8), rgba(139, 69, 19, 0.9))';
    bucket.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2), inset 0 -10px 20px rgba(0, 0, 0, 0.2)';
    bucket.style.border = '2px solid #D2691E';
    bucket.style.left = `${cartIcon.getBoundingClientRect().left}px`;
    bucket.style.top = `${cartIcon.getBoundingClientRect().top + 20}px`;
    bucket.style.opacity = '0';
    bucket.style.transform = 'scale(0) rotate(-15deg)';
    bucket.style.transition = 'all 0.5s cubic-bezier(0.18, 0.89, 0.32, 1.28)';

    // Add handle to bucket
    const handle = document.createElement('div');
    handle.className = 'bucket-handle';
    handle.style.position = 'absolute';
    handle.style.width = '30px';
    handle.style.height = '15px';
    handle.style.borderRadius = '15px 15px 0 0';
    handle.style.border = '2px solid #D2691E';
    handle.style.borderBottom = 'none';
    handle.style.top = '-15px';
    handle.style.left = '10px';
    bucket.appendChild(handle);

    // Add bucket to DOM
    document.body.appendChild(bucket);

    // Show bucket with delay
    setTimeout(() => {
        bucket.style.opacity = '1';
        bucket.style.transform = 'scale(1) rotate(0deg)';
    }, 300);

    // Start animation after a small delay
    setTimeout(() => {
        // Show loading toast with custom styling
        window.currentLoadingToast = toast.loading('Adding to cart...', {
            icon: '🛒',
            style: {
                borderRadius: '10px',
                background: '#fff',
                color: '#D2691E',
            }
        });

        // Animate flying element to bucket first
        const bucketRect = bucket.getBoundingClientRect();
        flyingElement.style.left = `${bucketRect.left + bucketRect.width/2 - 20}px`;
        flyingElement.style.top = `${bucketRect.top - 10}px`;
        flyingElement.style.opacity = '1';
        flyingElement.style.transform = 'scale(0.5)';

        // When product reaches bucket, animate bucket and move to cart
        setTimeout(() => {
            // Hide the flying element
            flyingElement.style.opacity = '0';

            // Animate bucket (tilt and bounce)
            bucket.style.transform = 'scale(1.1) rotate(-10deg)';

            // Add splash effect
            const splash = document.createElement('div');
            splash.className = 'bucket-splash';
            splash.style.position = 'absolute';
            splash.style.top = '0';
            splash.style.left = '0';
            splash.style.right = '0';
            splash.style.height = '10px';
            splash.style.background = 'radial-gradient(circle, rgba(210,105,30,0.8) 0%, rgba(210,105,30,0) 70%)';
            splash.style.borderRadius = '50%';
            splash.style.transform = 'scale(0)';
            splash.style.opacity = '0';
            splash.style.transition = 'all 0.3s ease-out';
            bucket.appendChild(splash);

            // Show splash
            setTimeout(() => {
                splash.style.transform = 'scale(1.5)';
                splash.style.opacity = '1';

                // Hide splash
                setTimeout(() => {
                    splash.style.opacity = '0';
                }, 300);
            }, 50);

            // Move bucket to cart
            setTimeout(() => {
                const cartRect = cartIcon.getBoundingClientRect();
                bucket.style.left = `${cartRect.left}px`;
                bucket.style.top = `${cartRect.top}px`;
                bucket.style.opacity = '0.7';
                bucket.style.transform = 'scale(0.5) rotate(0deg)';

                // Shake cart icon when bucket reaches it
                setTimeout(() => {
                    cartIcon.classList.add('cart-shake');

                    // Make AJAX request to add to cart
                    makeAddToCartRequest(productId, quantity, email);

                    // Remove animation elements
                    setTimeout(() => {
                        if (document.body.contains(flyingElement)) {
                            document.body.removeChild(flyingElement);
                        }
                        if (document.body.contains(bucket)) {
                            document.body.removeChild(bucket);
                        }
                        cartIcon.classList.remove('cart-shake');
                        isCartAnimationRunning = false;
                    }, 500);
                }, 400);
            }, 400);
        }, 400);
    }, 100);
}

/**
 * Make the actual AJAX request to add to cart
 * @param {number} productId - The product ID
 * @param {number} quantity - The quantity to add
 * @param {string} email - The user's email
 */
function makeAddToCartRequest(productId, quantity = 1, email = null) {
    console.log('Making AJAX request to add to cart:', productId, quantity, email);

    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrftoken) {
        console.error('CSRF token not found');
        showErrorToast('Could not add to cart: CSRF token missing');
        return;
    }

    // Prepare data
    const data = {
        'quantity': quantity,
        'csrfmiddlewaretoken': csrftoken
    };

    // Add email if provided
    if (email) {
        data.email = email;
    }

    // Make AJAX request
    $.ajax({
        url: `/add_to_cart/${productId}/`,
        type: 'POST',
        data: data,
        success: function(response) {
            console.log('Add to cart response:', response);

            if (response.success) {
                // Update cart count
                if (response.cart_count !== undefined) {
                    updateCartCountWithEnhancedAnimation(response.cart_count);
                }

                // Show success toast
                showSuccessToast(response.message || 'Product added to cart successfully!');
            } else {
                // Show error toast
                showErrorToast(response.message || 'Failed to add product to cart');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error adding to cart:', error);
            showErrorToast('Failed to add product to cart. Please try again.');
        }
    });
}

/**
 * Show a success toast notification
 * @param {string} message - The message to display
 */
function showSuccessToast(message) {
    if (typeof Toastify === 'function') {
        Toastify({
            text: message,
            duration: 3000,
            close: true,
            gravity: 'top',
            position: 'right',
            backgroundColor: '#28a745',
            stopOnFocus: true
        }).showToast();
    } else {
        alert(message);
    }
}

/**
 * Show an error toast notification
 * @param {string} message - The message to display
 */
function showErrorToast(message) {
    if (typeof Toastify === 'function') {
        Toastify({
            text: message,
            duration: 3000,
            close: true,
            gravity: 'top',
            position: 'right',
            backgroundColor: '#dc3545',
            stopOnFocus: true
        }).showToast();
    } else {
        alert(message);
    }
}

/**
 * Update cart count with enhanced animation
 * @param {number} count - The new cart count
 */
function updateCartCountWithEnhancedAnimation(count) {
    const cartCountElement = document.querySelector('.cart-count');
    if (!cartCountElement) return;

    // Store old value
    const oldValue = parseInt(cartCountElement.textContent) || 0;

    // Set new value
    cartCountElement.textContent = count;

    // Add animation class
    cartCountElement.classList.add('cart-count-pulse');

    // Remove animation class after animation completes
    setTimeout(() => {
        cartCountElement.classList.remove('cart-count-pulse');
    }, 1000);

    // If count increased, show the cart icon animation
    if (count > oldValue) {
        const cartIcon = document.querySelector('.navbar .fa-shopping-cart');
        if (cartIcon) {
            cartIcon.classList.add('cart-icon-bounce');
            setTimeout(() => {
                cartIcon.classList.remove('cart-icon-bounce');
            }, 1000);
        }
    }
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    /* Cart animations */
    @keyframes cartShake {
        0% { transform: rotate(0); }
        15% { transform: rotate(15deg); }
        30% { transform: rotate(-15deg); }
        45% { transform: rotate(10deg); }
        60% { transform: rotate(-10deg); }
        75% { transform: rotate(5deg); }
        85% { transform: rotate(-5deg); }
        100% { transform: rotate(0); }
    }

    .cart-shake {
        animation: cartShake 0.7s cubic-bezier(0.36, 0.07, 0.19, 0.97);
    }

    @keyframes cartCountPulse {
        0% { transform: scale(1); color: inherit; }
        50% { transform: scale(1.5); color: #D2691E; }
        100% { transform: scale(1); color: inherit; }
    }

    .cart-count-pulse {
        animation: cartCountPulse 0.7s cubic-bezier(0.18, 0.89, 0.32, 1.28);
    }

    @keyframes cartIconBounce {
        0% { transform: translateY(0); }
        40% { transform: translateY(-15px); }
        60% { transform: translateY(-10px); }
        80% { transform: translateY(-5px); }
        100% { transform: translateY(0); }
    }

    .cart-icon-bounce {
        animation: cartIconBounce 0.8s cubic-bezier(0.18, 0.89, 0.32, 1.28);
    }

    @keyframes bucketSplash {
        0% { transform: scale(0); opacity: 0; }
        50% { transform: scale(1.5); opacity: 1; }
        100% { transform: scale(2); opacity: 0; }
    }

    .bucket-splash {
        animation: bucketSplash 0.5s ease-out;
    }

    .flying-product {
        pointer-events: none;
        box-shadow: 0 5px 15px rgba(210, 105, 30, 0.3);
    }

    .cart-bucket {
        pointer-events: none;
    }

    /* Add to cart button animation */
    @keyframes addToCartPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    .btn-add-to-cart-african {
        animation: addToCartPulse 2s infinite;
    }

    .btn-add-to-cart-african:hover {
        animation: none;
    }
`;
document.head.appendChild(style);

// Define the core cart functions if they don't exist
window.addToCartWithEmailProvided = function(productId, quantity = 1, email) {
    // Use enhanced animation
    enhancedCartAnimation(productId, quantity, email);
};

window.updateCartCountWithAnimation = function(count) {
    // Use enhanced animation
    updateCartCountWithEnhancedAnimation(count);
};

// Define the addToCartWithEmail function if it doesn't exist
window.addToCartWithEmail = function(productId, quantity = 1) {
    console.log('Adding to cart with email collection:', productId);

    // Check if we already have an email in session storage
    const storedEmail = sessionStorage.getItem('guest_user_email');
    if (storedEmail) {
        console.log('Using stored email:', storedEmail);
        addToCartWithEmailProvided(productId, quantity, storedEmail);
        return;
    }

    // Show the email collection modal
    const emailModal = document.getElementById('emailCollectionModal');
    if (emailModal) {
        // Store the product ID and quantity in data attributes
        emailModal.setAttribute('data-product-id', productId);
        emailModal.setAttribute('data-quantity', quantity);

        // Show the modal
        try {
            const modal = new bootstrap.Modal(emailModal);
            modal.show();
        } catch (error) {
            console.error('Error showing email modal:', error);
            // Fallback: add to cart without email
            addToCartWithEmailProvided(productId, quantity, null);
        }
    } else {
        console.error('Email collection modal not found');
        // Fallback: add to cart without email
        addToCartWithEmailProvided(productId, quantity, null);
    }
};

// Add event listener to the email collection form
document.addEventListener('DOMContentLoaded', function() {
    const emailForm = document.getElementById('emailCollectionForm');
    if (emailForm) {
        emailForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Get the email from the form
            const email = document.getElementById('emailCollectionEmail').value;

            // Get the product ID and quantity from the modal
            const modal = document.getElementById('emailCollectionModal');
            const productId = modal.getAttribute('data-product-id');
            const quantity = modal.getAttribute('data-quantity') || 1;

            // Save the email to session storage
            sessionStorage.setItem('guest_user_email', email);

            // Hide the modal safely using multiple fallback methods
            if (!modal) {
                console.error('Modal element not found');
            } else {
                // Try all available methods to hide the modal
                if (window.ModalManager) {
                    window.ModalManager.hide(modal);
                } else if (bootstrap && bootstrap.Modal && bootstrap.Modal.hideModal) {
                    bootstrap.Modal.hideModal(modal);
                } else if (bootstrap && bootstrap.Modal) {
                    try {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        if (modalInstance) {
                            modalInstance.hide();
                        } else {
                            const newModal = new bootstrap.Modal(modal);
                            newModal.hide();
                        }
                    } catch (error) {
                        console.error('Error hiding modal with bootstrap:', error);
                        // Try jQuery as fallback
                        if (typeof $ !== 'undefined') {
                            $(modal).modal('hide');
                        } else {
                            // Last resort: manual DOM manipulation
                            modal.classList.remove('show');
                            modal.style.display = 'none';
                            document.body.classList.remove('modal-open');

                            // Remove backdrop if exists
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop && backdrop.parentNode) {
                                backdrop.parentNode.removeChild(backdrop);
                            }
                        }
                    }
                }
            }

            // Add to cart with the email
            if (productId) {
                addToCartWithEmailProvided(productId, quantity, email);
            }
        });
    }
});
