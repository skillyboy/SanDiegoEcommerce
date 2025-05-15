/**
 * Enhanced Cart Handler with Email Collection
 * This script handles adding products to cart with email collection
 * and provides smooth animations and error handling
 */

// Global variables
let isAddingToCart = false;
let emailCollected = false;

/**
 * Add to cart with email collection
 * @param {number} productId - The ID of the product to add
 * @param {number} quantity - The quantity to add (default: 1)
 */
function addToCartWithEmail(productId, quantity = 1) {
    // Prevent multiple clicks
    if (isAddingToCart) {
        showToast('Please wait while we process your request...', 'info');
        return;
    }

    // Set flag to prevent multiple clicks
    isAddingToCart = true;

    // Check if we already have an email in session
    if (emailCollected) {
        // If we already have an email, add to cart directly
        addToCart(productId, quantity);
        return;
    }

    // Show email collection modal
    Swal.fire({
        title: 'Quick Checkout',
        html: `
            <p class="mb-3">Enter your email to continue shopping</p>
            <input type="email" id="email-input" class="swal2-input" placeholder="Your email address">
            <div class="form-check mt-3">
                <input class="form-check-input" type="checkbox" id="newsletter-checkbox" checked>
                <label class="form-check-label" for="newsletter-checkbox">
                    Subscribe to our newsletter
                </label>
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: 'Continue',
        cancelButtonText: 'Cancel',
        showLoaderOnConfirm: true,
        preConfirm: () => {
            const email = document.getElementById('email-input').value;
            const subscribeToNewsletter = document.getElementById('newsletter-checkbox').checked;

            if (!email) {
                Swal.showValidationMessage('Please enter your email');
                return false;
            }

            if (!isValidEmail(email)) {
                Swal.showValidationMessage('Please enter a valid email');
                return false;
            }

            // Save email to session
            return saveEmailToSession(email, subscribeToNewsletter)
                .then(response => {
                    if (response.success) {
                        emailCollected = true;
                        return { email, subscribeToNewsletter };
                    } else {
                        Swal.showValidationMessage(response.message || 'Failed to save email');
                        return false;
                    }
                })
                .catch(error => {
                    console.error('Error saving email:', error);
                    Swal.showValidationMessage('An error occurred. Please try again.');
                    return false;
                });
        },
        allowOutsideClick: () => !Swal.isLoading()
    }).then((result) => {
        if (result.isConfirmed) {
            // Add to cart
            addToCart(productId, quantity);
        } else {
            // Reset flag
            isAddingToCart = false;
        }
    });
}

/**
 * Save email to session
 * @param {string} email - The email to save
 * @param {boolean} subscribeToNewsletter - Whether to subscribe to newsletter
 * @returns {Promise} - Promise that resolves with the response
 */
function saveEmailToSession(email, subscribeToNewsletter) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '/save_guest_email/',
            type: 'POST',
            data: {
                'email': email,
                'subscribe': subscribeToNewsletter,
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            success: function(response) {
                resolve(response);
            },
            error: function(xhr, status, error) {
                reject(error);
            }
        });
    });
}

/**
 * Add to cart
 * @param {number} productId - The ID of the product to add
 * @param {number} quantity - The quantity to add
 */
function addToCart(productId, quantity) {
    // Show loading toast
    showToast('Adding to cart...', 'loading');

    // Add flying animation
    addToCartAnimation(productId);

    // Make AJAX request
    $.ajax({
        url: `/add_to_cart/${productId}/`,
        type: 'POST',
        data: {
            'quantity': quantity,
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            // Reset flag
            isAddingToCart = false;

            if (response.success) {
                // Update cart count
                updateCartCount(response.cart_count);

                // Show success toast
                showToast(response.message || 'Product added to cart successfully!', 'success');

                // Trigger cart updated event to show the cart sidebar
                document.dispatchEvent(new CustomEvent('cartUpdated', {
                    detail: {
                        productId: productId,
                        quantity: quantity,
                        cartCount: response.cart_count
                    }
                }));
            } else {
                // Show error toast
                showToast(response.message || 'Failed to add product to cart', 'error');
            }
        },
        error: function(xhr, status, error) {
            // Reset flag
            isAddingToCart = false;

            // Show error toast
            showToast('An error occurred. Please try again.', 'error');
            console.error('Error adding to cart:', error);
        }
    });
}

/**
 * Add to cart animation
 * @param {number} productId - The ID of the product
 */
function addToCartAnimation(productId) {
    const productCard = document.querySelector(`[data-product-id="${productId}"]`);
    if (!productCard) return;

    const cartIcon = document.querySelector('.cart-button-count');
    if (!cartIcon) return;

    // Get product image
    const imgElement = productCard.querySelector('img') || document.querySelector(`#modalProduct${productId} img`);
    if (!imgElement) return;

    const imgRect = imgElement.getBoundingClientRect();
    const cartRect = cartIcon.getBoundingClientRect();

    // Create flying element
    const flyingImg = document.createElement('div');
    flyingImg.className = 'flying-cart-item';
    flyingImg.style.backgroundImage = `url(${imgElement.src})`;
    flyingImg.style.width = '50px';
    flyingImg.style.height = '50px';
    flyingImg.style.position = 'fixed';
    flyingImg.style.top = `${imgRect.top}px`;
    flyingImg.style.left = `${imgRect.left}px`;
    flyingImg.style.borderRadius = '50%';
    flyingImg.style.backgroundSize = 'cover';
    flyingImg.style.backgroundPosition = 'center';
    flyingImg.style.zIndex = '9999';
    flyingImg.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
    flyingImg.style.transition = 'all 0.8s cubic-bezier(0.18, 0.89, 0.32, 1.28)';

    // Add to body
    document.body.appendChild(flyingImg);

    // Animate
    setTimeout(() => {
        flyingImg.style.top = `${cartRect.top}px`;
        flyingImg.style.left = `${cartRect.left}px`;
        flyingImg.style.width = '20px';
        flyingImg.style.height = '20px';
        flyingImg.style.opacity = '0';

        // Shake cart icon
        cartIcon.style.animation = 'shake 0.5s ease-in-out';

        // Remove flying element after animation
        setTimeout(() => {
            document.body.removeChild(flyingImg);
            cartIcon.style.animation = '';
        }, 800);
    }, 10);
}

/**
 * Update cart count
 * @param {number} count - The new cart count
 */
function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart-button-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
        cartCountElement.classList.add('cart-count-updated');
        setTimeout(() => {
            cartCountElement.classList.remove('cart-count-updated');
        }, 1000);
    }
}

/**
 * Increase cart item quantity
 * @param {number} itemId - The cart item ID
 */
function increaseCartQuantity(itemId) {
    // Show loading state
    const quantityElement = document.getElementById(`quantity-${itemId}`);
    if (quantityElement) {
        quantityElement.classList.add('quantity-updating');
    }

    // Make AJAX request
    $.ajax({
        url: `/increase_quantity/${itemId}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            // Remove loading state
            if (quantityElement) {
                quantityElement.classList.remove('quantity-updating');
            }

            if (response.success) {
                // Update quantity display
                if (quantityElement) {
                    quantityElement.textContent = response.new_quantity;

                    // Add animation
                    quantityElement.classList.add('quantity-changed');
                    setTimeout(() => {
                        quantityElement.classList.remove('quantity-changed');
                    }, 500);
                }

                // Update item total price
                const totalElement = document.getElementById(`total-${itemId}`);
                if (totalElement) {
                    totalElement.textContent = `$${response.new_total_price.toFixed(2)}`;
                    totalElement.classList.add('price-updated');
                    setTimeout(() => {
                        totalElement.classList.remove('price-updated');
                    }, 500);
                }

                // Update cart summary
                updateCartSummary(response.subtotal, response.vat, response.total);
            } else {
                // Show error toast
                showToast(response.message || 'Failed to increase quantity', 'error');
            }
        },
        error: function() {
            // Remove loading state
            if (quantityElement) {
                quantityElement.classList.remove('quantity-updating');
            }

            // Show error toast
            showToast('Failed to increase quantity. Please try again.', 'error');
        }
    });
}

/**
 * Decrease cart item quantity
 * @param {number} itemId - The cart item ID
 */
function decreaseCartQuantity(itemId) {
    // Get current quantity
    const quantityElement = document.getElementById(`quantity-${itemId}`);
    if (!quantityElement) return;

    const currentQuantity = parseInt(quantityElement.textContent);
    if (currentQuantity <= 1) {
        // Show warning toast
        showToast('Quantity cannot be less than 1', 'info');
        return;
    }

    // Show loading state
    quantityElement.classList.add('quantity-updating');

    // Make AJAX request
    $.ajax({
        url: `/decrease_quantity/${itemId}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            // Remove loading state
            quantityElement.classList.remove('quantity-updating');

            if (response.success) {
                // Update quantity display
                quantityElement.textContent = response.new_quantity;

                // Add animation
                quantityElement.classList.add('quantity-changed');
                setTimeout(() => {
                    quantityElement.classList.remove('quantity-changed');
                }, 500);

                // Update item total price
                const totalElement = document.getElementById(`total-${itemId}`);
                if (totalElement) {
                    totalElement.textContent = `$${response.new_total_price.toFixed(2)}`;
                    totalElement.classList.add('price-updated');
                    setTimeout(() => {
                        totalElement.classList.remove('price-updated');
                    }, 500);
                }

                // Update cart summary
                updateCartSummary(response.subtotal, response.vat, response.total);
            } else {
                // Show error toast
                showToast(response.message || 'Failed to decrease quantity', 'error');
            }
        },
        error: function() {
            // Remove loading state
            quantityElement.classList.remove('quantity-updating');

            // Show error toast
            showToast('Failed to decrease quantity. Please try again.', 'error');
        }
    });
}

/**
 * Update cart summary
 * @param {number} subtotal - The cart subtotal
 * @param {number} vat - The VAT amount
 * @param {number} total - The total amount
 */
function updateCartSummary(subtotal, vat, total) {
    // Update subtotal
    const subtotalElement = document.getElementById('cart-subtotal');
    if (subtotalElement) {
        subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
        subtotalElement.classList.add('price-updated');
        setTimeout(() => {
            subtotalElement.classList.remove('price-updated');
        }, 500);
    }

    // Update VAT
    const vatElement = document.getElementById('cart-vat');
    if (vatElement) {
        vatElement.textContent = `$${vat.toFixed(2)}`;
        vatElement.classList.add('price-updated');
        setTimeout(() => {
            vatElement.classList.remove('price-updated');
        }, 500);
    }

    // Update total
    const totalElement = document.getElementById('cart-total');
    if (totalElement) {
        totalElement.textContent = `$${total.toFixed(2)}`;
        totalElement.classList.add('price-updated');
        setTimeout(() => {
            totalElement.classList.remove('price-updated');
        }, 500);
    }
}

/**
 * Show toast notification
 * @param {string} message - The message to show
 * @param {string} type - The type of toast (success, error, info, loading)
 */
function showToast(message, type) {
    // Check if Toastify is available
    if (typeof Toastify === 'function') {
        Toastify({
            text: message,
            duration: type === 'error' ? 5000 : 3000,
            close: true,
            gravity: 'top',
            position: 'right',
            backgroundColor: getToastColor(type),
            stopOnFocus: true
        }).showToast();
    } else {
        // Fallback to alert
        if (type === 'error') {
            alert(`Error: ${message}`);
        } else if (type !== 'loading') {
            alert(message);
        }
    }
}

/**
 * Get toast color based on type
 * @param {string} type - The type of toast
 * @returns {string} - The color
 */
function getToastColor(type) {
    switch (type) {
        case 'success':
            return '#28a745';
        case 'error':
            return '#dc3545';
        case 'info':
            return '#17a2b8';
        case 'loading':
            return '#6c757d';
        default:
            return '#343a40';
    }
}

/**
 * Validate email
 * @param {string} email - The email to validate
 * @returns {boolean} - Whether the email is valid
 */
function isValidEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

// Initialize on document ready
$(document).ready(function() {
    // Add animation keyframes if not already added
    if (!document.getElementById('cart-animation-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'cart-animation-styles';
        styleElement.textContent = `
            @keyframes shake {
                0% { transform: rotate(0deg); }
                25% { transform: rotate(10deg); }
                50% { transform: rotate(0deg); }
                75% { transform: rotate(-10deg); }
                100% { transform: rotate(0deg); }
            }

            .cart-count-updated {
                animation: pulse 0.5s ease;
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.2); }
                100% { transform: scale(1); }
            }

            .quantity-changed {
                animation: quantityPulse 0.5s ease;
                background-color: rgba(0, 135, 81, 0.1);
            }

            @keyframes quantityPulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }

            .quantity-updating {
                opacity: 0.7;
                position: relative;
            }

            .quantity-updating::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 10px;
                height: 10px;
                margin-top: -5px;
                margin-left: -5px;
                border-radius: 50%;
                border: 2px solid rgba(0, 135, 81, 0.5);
                border-top-color: #008751;
                animation: spin 0.8s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .price-updated {
                animation: priceUpdate 0.5s ease;
                color: #008751;
            }

            @keyframes priceUpdate {
                0% { opacity: 0.5; }
                50% { opacity: 1; }
                100% { opacity: 0.5; }
            }
        `;
        document.head.appendChild(styleElement);
    }

    // Attach event handlers to quantity buttons in cart
    $('.btn-quantity-increase').on('click', function() {
        const itemId = $(this).data('item-id');
        if (itemId) {
            increaseCartQuantity(itemId);
        }
    });

    $('.btn-quantity-decrease').on('click', function() {
        const itemId = $(this).data('item-id');
        if (itemId) {
            decreaseCartQuantity(itemId);
        }
    });
});
