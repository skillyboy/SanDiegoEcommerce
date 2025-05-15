/**
 * Email Collection Module
 * Handles collecting emails from users when they add items to cart or wishlist
 * without requiring them to create an account
 */

// Store for email collection state
const EmailCollection = {
    // Has the user already provided their email in this session?
    emailProvided: false,

    // The email the user provided
    userEmail: '',

    // The action that was pending when we asked for email
    pendingAction: null,

    // Initialize from session storage if available
    init: function() {
        // Check if we already have an email in session storage
        const storedEmail = sessionStorage.getItem('guest_user_email');
        if (storedEmail) {
            this.emailProvided = true;
            this.userEmail = storedEmail;
            console.log('Email already provided:', this.userEmail);
        }

        // Check for Django session flag via cookie (more reliable across page loads)
        const emailCollectedCookie = this.getCookie('email_collected');
        if (emailCollectedCookie === 'true') {
            this.emailProvided = true;
            console.log('Email already collected according to Django session');
        }

        // Set up event listeners
        this.setupEventListeners();
    },

    // Helper function to get cookie value
    getCookie: function(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    },

    // Set up event listeners for the email collection form
    setupEventListeners: function() {
        // When the form is submitted
        $('#emailCollectionForm').on('submit', function(e) {
            e.preventDefault();
            EmailCollection.submitEmailForm();
        });

        // When the modal is closed without submitting
        $('#emailCollectionModal').on('hidden.bs.modal', function() {
            // If there was a pending action but the user closed the modal,
            // clear the pending action
            if (EmailCollection.pendingAction) {
                console.log('Modal closed without submitting, clearing pending action');
                EmailCollection.pendingAction = null;
            }
        });
    },

    // Show the email collection modal
    showModal: function(pendingAction) {
        // If the user has already provided their email, just execute the action
        if (this.emailProvided) {
            console.log('Email already provided, executing action directly');
            if (pendingAction) {
                pendingAction(this.userEmail);
            }
            return;
        }

        // Otherwise, store the pending action and show the modal
        this.pendingAction = pendingAction;

        // Show the modal safely using ModalManager
        const emailModal = document.getElementById('emailCollectionModal');
        if (window.ModalManager && emailModal) {
            window.ModalManager.show(emailModal);
        } else {
            try {
                const modal = new bootstrap.Modal(emailModal);
                modal.show();
            } catch (error) {
                console.error('Error showing modal:', error);
                // Try to show with jQuery as fallback
                if (typeof $ !== 'undefined' && emailModal) {
                    $(emailModal).modal('show');
                }
            }
        }
    },

    // Submit the email collection form
    submitEmailForm: function() {
        // Get the email from the form safely
        const emailInput = document.getElementById('emailCollectionEmail');
        if (!emailInput) {
            console.error('Email input element not found');
            toast.error('Could not find email input field. Please try again or refresh the page.');
            return;
        }

        const email = emailInput.value;
        const consentCheckbox = document.getElementById('emailCollectionConsent');
        const consent = consentCheckbox ? consentCheckbox.checked : true; // Default to true if checkbox not found

        // Clear previous validation errors
        $('#emailCollectionEmail').removeClass('is-invalid');
        $('#emailCollectionConsent').removeClass('is-invalid');

        // Validate the email
        if (!this.validateEmail(email)) {
            // Show validation error
            $('#emailCollectionEmail').addClass('is-invalid');
            return;
        }

        // Validate consent
        if (!consent) {
            // Show validation error
            $('#emailCollectionConsent').addClass('is-invalid');
            return;
        }

        // Show loading state on button
        const submitBtn = $('#emailCollectionSubmit');
        const originalBtnText = submitBtn.html();
        submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Saving...');
        submitBtn.prop('disabled', true);

        // Store the email locally first (this ensures the functionality works even if the AJAX call fails)
        this.userEmail = email;
        this.emailProvided = true;

        // Save to session storage (client-side)
        sessionStorage.setItem('guest_user_email', email);

        // Also save to server session and database via AJAX
        $.ajax({
            url: '/save_guest_email/',
            type: 'POST',
            data: {
                'email': email,
                'subscribe': consent,
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            success: (response) => {
                console.log('Email saved:', response);

                // Reset button state
                submitBtn.html(originalBtnText);
                submitBtn.prop('disabled', false);

                // Check if this is a registered user's email
                if (response.registered) {
                    // Show a message asking if they want to log in
                    if (window.toast && window.toast.info) {
                        window.toast.info(response.message, {
                            title: 'Account Found',
                            actionText: 'Log In',
                            actionUrl: '/login/'
                        });
                    }
                }

                // Hide the modal safely using multiple fallback methods
                const emailModal = document.getElementById('emailCollectionModal');
                if (!emailModal) {
                    console.error('Email modal element not found');
                } else {
                    // Try all available methods to hide the modal
                    if (window.ModalManager) {
                        window.ModalManager.hide(emailModal);
                    } else if (bootstrap && bootstrap.Modal && bootstrap.Modal.hideModal) {
                        bootstrap.Modal.hideModal(emailModal);
                    } else if (bootstrap && bootstrap.Modal) {
                        try {
                            const modalInstance = bootstrap.Modal.getInstance(emailModal);
                            if (modalInstance) {
                                modalInstance.hide();
                            } else {
                                const newModal = new bootstrap.Modal(emailModal);
                                newModal.hide();
                            }
                        } catch (error) {
                            console.error('Error hiding modal with bootstrap:', error);
                            // Try jQuery as fallback
                            if (typeof $ !== 'undefined') {
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
                }

                // Execute the pending action if there is one
                if (this.pendingAction) {
                    console.log('Executing pending action with email:', email);
                    this.pendingAction(email);
                    this.pendingAction = null;
                }

                // Show a success toast with animation
                toast.success(response.message || 'Email saved! Your cart will be associated with this email.', {
                    title: 'Thank You!',
                    icon: '<i class="fas fa-envelope-open-text"></i>',
                    style: {
                        borderLeft: '4px solid #D2691E'
                    }
                });

                // If there's a warning, show it
                if (response.warning && window.toast && window.toast.warning) {
                    window.toast.warning(response.warning, {
                        title: 'Note'
                    });
                }
            },
            error: (xhr, status, error) => {
                console.error('Error saving email:', error);

                // Reset button state
                submitBtn.html(originalBtnText);
                submitBtn.prop('disabled', false);

                // Even if the server request fails, we still want to proceed with the action
                // since we've already stored the email locally

                // Hide the modal safely using multiple fallback methods
                const emailModal = document.getElementById('emailCollectionModal');
                if (!emailModal) {
                    console.error('Email modal element not found');
                } else {
                    // Try all available methods to hide the modal
                    if (window.ModalManager) {
                        window.ModalManager.hide(emailModal);
                    } else if (bootstrap && bootstrap.Modal && bootstrap.Modal.hideModal) {
                        bootstrap.Modal.hideModal(emailModal);
                    } else if (bootstrap && bootstrap.Modal) {
                        try {
                            const modalInstance = bootstrap.Modal.getInstance(emailModal);
                            if (modalInstance) {
                                modalInstance.hide();
                            } else {
                                const newModal = new bootstrap.Modal(emailModal);
                                newModal.hide();
                            }
                        } catch (error) {
                            console.error('Error hiding modal with bootstrap:', error);
                            // Try jQuery as fallback
                            if (typeof $ !== 'undefined') {
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
                }

                // Execute the pending action if there is one
                if (this.pendingAction) {
                    console.log('Executing pending action with email despite server error:', email);
                    this.pendingAction(email);
                    this.pendingAction = null;
                }

                // Show a warning toast
                toast.warning('Your action was completed, but we had trouble saving your email for future sessions.', {
                    title: 'Partial Success',
                    icon: '<i class="fas fa-exclamation-triangle"></i>'
                });
            }
        });
    },

    // Validate an email address
    validateEmail: function(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }
};

// Initialize the email collection module when the document is ready
$(document).ready(function() {
    EmailCollection.init();

    // Check for items already in cart and update buttons
    checkCartItemsAndUpdateButtons();
});

/**
 * Add to cart with email collection
 * This function wraps the original add_to_cart function to collect email first
 */
function addToCartWithEmail(productId, quantity = 1) {
    // Show the email collection modal with a callback to add to cart
    EmailCollection.showModal(function(email) {
        // Now add to cart with the email
        addToCartWithEmailProvided(productId, quantity, email);
    });
}

/**
 * Add to cart when email is already provided
 */
function addToCartWithEmailProvided(productId, quantity = 1, email) {
    // Prevent double clicks
    if (window.isAddingToCart) {
        toast.info('Please wait while we process your request...', {
            title: 'Processing',
            duration: 2000
        });
        return;
    }

    window.isAddingToCart = true;

    // Create a timeout to automatically clear the loading state if the request takes too long
    const timeoutId = setTimeout(() => {
        if (window.isAddingToCart) {
            window.isAddingToCart = false;
            if (window.currentLoadingToast) {
                toast.close(window.currentLoadingToast);
                window.currentLoadingToast = null;
            }
            toast.error('Request timed out. Please try again.', {
                title: 'Timeout Error'
            });
        }
    }, 10000); // 10 second timeout

    // Get product details for the animation and toast
    const productElement = document.querySelector(`[data-product-id="${productId}"]`);
    const productName = productElement ? productElement.getAttribute('data-product-name') || 'Product' : 'Product';
    const productImage = productElement ? productElement.getAttribute('data-product-image') || '' : '';
    const productPrice = productElement ? productElement.getAttribute('data-product-price') || '' : '';

    // Show immediate feedback with flying animation
    if (productElement) {
        // Create flying element
        const flyingElement = document.createElement('div');
        flyingElement.className = 'flying-item';
        flyingElement.style.position = 'fixed';
        flyingElement.style.zIndex = '9999';
        flyingElement.style.width = '50px';
        flyingElement.style.height = '50px';
        flyingElement.style.borderRadius = '50%';
        flyingElement.style.backgroundSize = 'cover';
        flyingElement.style.backgroundPosition = 'center';
        flyingElement.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
        flyingElement.style.transition = 'all 0.8s cubic-bezier(0.18, 0.89, 0.32, 1.28)';

        // Get product image if available
        const productImg = productElement.querySelector('img');
        if (productImg) {
            flyingElement.style.backgroundImage = `url(${productImg.src})`;
        } else {
            flyingElement.style.backgroundColor = 'var(--service-primary, #008751)';
        }

        // Get positions
        const rect = productElement.getBoundingClientRect();
        flyingElement.style.left = `${rect.left + rect.width / 2 - 25}px`;
        flyingElement.style.top = `${rect.top + rect.height / 2 - 25}px`;
        flyingElement.style.opacity = '1';

        // Get cart icon position
        const cartIcon = document.querySelector('.navbar .fa-shopping-cart');
        if (cartIcon) {
            document.body.appendChild(flyingElement);

            // Start animation after a small delay
            setTimeout(() => {
                const cartRect = cartIcon.getBoundingClientRect();
                flyingElement.style.left = `${cartRect.left}px`;
                flyingElement.style.top = `${cartRect.top}px`;
                flyingElement.style.opacity = '0';
                flyingElement.style.transform = 'scale(0.3)';

                // Show loading toast after animation starts
                window.currentLoadingToast = toast.loading('Adding to cart...');
            }, 100);

            // Remove flying element after animation completes
            setTimeout(() => {
                if (document.body.contains(flyingElement)) {
                    document.body.removeChild(flyingElement);
                }
            }, 1000);
        } else {
            // If cart icon not found, just show loading toast
            window.currentLoadingToast = toast.loading('Adding to cart...');
        }
    } else {
        // If product element not found, just show loading toast
        window.currentLoadingToast = toast.loading('Adding to cart...');
    }

    // Make AJAX request to add to cart
    $.ajax({
        url: `/add_to_cart/${productId}/`,
        type: 'POST',
        data: {
            'quantity': quantity,
            'email': email,
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            // Clear timeout and loading state
            clearTimeout(timeoutId);
            window.isAddingToCart = false;

            // Close loading toast
            if (window.currentLoadingToast) {
                toast.close(window.currentLoadingToast);
                window.currentLoadingToast = null;
            }

            if (response.success) {
                // Update cart count
                updateCartCountWithAnimation(response.cart_count);

                // Show success toast
                toast.cart({
                    name: productName,
                    image: productImage,
                    price: productPrice,
                    link: '/cart/'
                }, response.message || 'Product added to cart successfully!');

                // Update the add to cart button state
                updateAddToCartButtonState(productId, true);
            } else {
                // Show error toast
                toast.error(response.message || 'Failed to add product to cart', {
                    title: 'Error Adding to Cart'
                });
            }
        },
        error: function() {
            // Clear timeout and loading state
            clearTimeout(timeoutId);
            window.isAddingToCart = false;

            // Close loading toast
            if (window.currentLoadingToast) {
                toast.close(window.currentLoadingToast);
                window.currentLoadingToast = null;
            }

            // Show error toast
            toast.error('Failed to add product to cart. Please try again.', {
                title: 'Error Adding to Cart'
            });
        }
    });
}

/**
 * Add to wishlist with email collection
 */
function addToWishlistWithEmail(productId) {
    // Show the email collection modal with a callback to add to wishlist
    EmailCollection.showModal(function(email) {
        // Now add to wishlist with the email
        addToWishlistWithEmailProvided(productId, email);
    });
}

/**
 * Add to wishlist when email is already provided
 */
function addToWishlistWithEmailProvided(productId, email) {
    // Create a timeout to automatically clear the loading state if the request takes too long
    const timeoutId = setTimeout(() => {
        if (window.isAddingToWishlist) {
            window.isAddingToWishlist = false;
            if (window.currentWishlistToast) {
                toast.close(window.currentWishlistToast);
                window.currentWishlistToast = null;
            }
            toast.error('Request timed out. Please try again.', {
                title: 'Timeout Error'
            });
        }
    }, 10000); // 10 second timeout

    // Set flag to prevent double clicks
    window.isAddingToWishlist = true;

    // Get the product element
    const productElement = document.querySelector(`[data-product-id="${productId}"]`);

    // Get the heart icon and add pulse animation
    const heartIcon = document.querySelector(`.btn-add-to-wishlist[onclick*="${productId}"] i`);
    if (heartIcon) {
        heartIcon.classList.add('heart-pulse');
    }

    // Show immediate visual feedback
    if (productElement) {
        // Create heart animation
        const heart = document.createElement('div');
        heart.className = 'flying-heart';
        heart.innerHTML = '<i class="fas fa-heart"></i>';
        heart.style.position = 'fixed';
        heart.style.zIndex = '9999';
        heart.style.color = '#ff3366';
        heart.style.fontSize = '30px';
        heart.style.transition = 'all 0.8s cubic-bezier(0.18, 0.89, 0.32, 1.28)';
        heart.style.opacity = '1';

        // Get positions
        const rect = productElement.getBoundingClientRect();
        heart.style.left = `${rect.left + rect.width / 2 - 15}px`;
        heart.style.top = `${rect.top + rect.height / 2 - 15}px`;

        document.body.appendChild(heart);

        // Start animation after a small delay
        setTimeout(() => {
            heart.style.transform = 'translateY(-100px) scale(1.5)';
            heart.style.opacity = '0';

            // Show loading toast after animation starts
            window.currentWishlistToast = toast.loading('Adding to wishlist...');
        }, 100);

        // Remove heart element after animation completes
        setTimeout(() => {
            if (document.body.contains(heart)) {
                document.body.removeChild(heart);
            }
        }, 1000);
    } else {
        // If product element not found, just show loading toast
        window.currentWishlistToast = toast.loading('Adding to wishlist...');
    }

    // Make AJAX request to add to wishlist
    $.ajax({
        url: '/add_to_wishlist/',
        type: 'POST',
        data: {
            'product_id': productId,
            'email': email,
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            // Clear timeout and loading state
            clearTimeout(timeoutId);
            window.isAddingToWishlist = false;

            // Close loading toast
            if (window.currentWishlistToast) {
                toast.close(window.currentWishlistToast);
                window.currentWishlistToast = null;
            }

            if (response.success) {
                // Show success toast
                toast.success(response.message || 'Product added to wishlist!', {
                    title: 'Added to Wishlist',
                    actions: [
                        {
                            id: 'view-wishlist',
                            text: 'View Wishlist',
                            class: 'toast-btn-primary',
                            callback: () => {
                                window.location.href = '/wishlist/';
                            }
                        }
                    ]
                });

                // Update heart icon
                if (heartIcon) {
                    heartIcon.classList.remove('heart-pulse');
                    heartIcon.classList.remove('far');
                    heartIcon.classList.add('fas');
                    heartIcon.classList.add('text-danger');
                }

                // Update all instances of this product's wishlist button
                const allHeartIcons = document.querySelectorAll(`.btn-add-to-wishlist[onclick*="${productId}"] i`);
                allHeartIcons.forEach(icon => {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    icon.classList.add('text-danger');
                });
            } else {
                // Show error toast
                toast.error(response.message || 'Failed to add to wishlist', {
                    title: 'Error',
                    actions: [
                        {
                            id: 'try-again',
                            text: 'Try Again',
                            class: 'toast-btn-primary',
                            callback: () => addToWishlistWithEmail(productId)
                        }
                    ]
                });

                // Reset heart icon
                if (heartIcon) {
                    heartIcon.classList.remove('heart-pulse');
                }
            }
        },
        error: function() {
            // Clear timeout and loading state
            clearTimeout(timeoutId);
            window.isAddingToWishlist = false;

            // Close loading toast
            if (window.currentWishlistToast) {
                toast.close(window.currentWishlistToast);
                window.currentWishlistToast = null;
            }

            // Show error toast
            toast.error('Failed to add to wishlist. Please try again.', {
                title: 'Error',
                actions: [
                    {
                        id: 'try-again',
                        text: 'Try Again',
                        class: 'toast-btn-primary',
                        callback: () => addToWishlistWithEmail(productId)
                    }
                ]
            });

            // Reset heart icon
            if (heartIcon) {
                heartIcon.classList.remove('heart-pulse');
            }
        }
    });
}

/**
 * Check if items are already in cart and update button states
 */
function checkCartItemsAndUpdateButtons() {
    // Make an AJAX request to get current cart items
    $.ajax({
        url: '/get-cart-items/',
        type: 'GET',
        success: function(response) {
            if (response.success && response.cart_items) {
                // Update button states for each product in cart
                response.cart_items.forEach(item => {
                    updateAddToCartButtonState(item.product_id, true);
                });
            }
        },
        error: function() {
            console.error('Failed to fetch cart items');
        }
    });
}

/**
 * Update the state of Add to Cart button based on whether item is in cart
 * @param {number} productId - The product ID
 * @param {boolean} inCart - Whether the product is in cart
 */
function updateAddToCartButtonState(productId, inCart) {
    // Find all add to cart buttons for this product
    const addToCartButtons = document.querySelectorAll(`.btn-add-to-cart-nigerian-large[data-product-id="${productId}"], .btn-add-to-cart[data-product-id="${productId}"]`);

    // Also try to find the button by its onclick attribute
    const onclickButtons = document.querySelectorAll(`[onclick*="add_to_cart(${productId})"]`);

    // Combine the button collections
    const allButtons = [...addToCartButtons, ...onclickButtons];

    // If we found the main product page button that doesn't have a data-product-id
    const mainProductButton = document.getElementById('add-to-cart-btn');
    if (mainProductButton && window.location.href.includes(`/product/${productId}/`)) {
        allButtons.push(mainProductButton);
    }

    // Update each button
    allButtons.forEach(button => {
        if (inCart) {
            // If item is in cart, change button text and style
            button.innerHTML = '<i class="fas fa-check me-2"></i>In Cart';
            button.classList.add('in-cart');

            // Don't disable the button, but change its function to increase quantity
            button.setAttribute('onclick', `updateCartQuantity(${productId}, 'increase')`);

            // If it's an event listener button, we need to update differently
            if (button.id === 'add-to-cart-btn') {
                // Remove existing listeners and add new one
                button.replaceWith(button.cloneNode(true));
                const newButton = document.getElementById('add-to-cart-btn');
                if (newButton) {
                    newButton.addEventListener('click', function() {
                        updateCartQuantity(productId, 'increase');
                    });
                }
            }
        } else {
            // If item is not in cart, reset button
            button.innerHTML = '<i class="fas fa-shopping-cart me-2"></i>Add to Cart';
            button.classList.remove('in-cart');

            // Reset onclick to original function
            button.setAttribute('onclick', `add_to_cart(${productId})`);

            // If it's the main product button, reset its event listener
            if (button.id === 'add-to-cart-btn') {
                button.replaceWith(button.cloneNode(true));
                const newButton = document.getElementById('add-to-cart-btn');
                if (newButton) {
                    newButton.addEventListener('click', function() {
                        const quantity = parseInt(document.getElementById('quantity').value);
                        addToCartWithEmail(productId, quantity);
                    });
                }
            }
        }
    });
}

/**
 * Update cart item quantity
 * @param {number} productId - The product ID
 * @param {string} action - 'increase' or 'decrease'
 */
function updateCartQuantity(productId, action) {
    // Prevent multiple clicks
    if (window.isUpdatingCart) {
        return;
    }

    window.isUpdatingCart = true;

    // Show loading toast
    const loadingToast = toast.loading(`${action === 'increase' ? 'Increasing' : 'Decreasing'} quantity...`);

    // Make AJAX request to update quantity
    $.ajax({
        url: `/cart/${action}/${productId}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            window.isUpdatingCart = false;
            toast.close(loadingToast);

            if (response.success) {
                // Show success toast
                toast.success(`Quantity ${action === 'increase' ? 'increased' : 'decreased'} successfully`, {
                    title: 'Cart Updated'
                });

                // Update cart count if needed
                if (response.cart_count) {
                    updateCartCountWithAnimation(response.cart_count);
                }

                // Refresh the cart modal if it's open
                if ($('#modalShoppingCart').hasClass('show')) {
                    setTimeout(() => {
                        $('.navbar .fa-shopping-cart').parent().click();
                    }, 500);
                }
            } else {
                // Show error toast
                toast.error(response.message || `Failed to ${action} quantity`, {
                    title: 'Error'
                });
            }
        },
        error: function() {
            window.isUpdatingCart = false;
            toast.close(loadingToast);
            toast.error(`Failed to ${action} quantity. Please try again.`, {
                title: 'Error'
            });
        }
    });
}