/**
 * Enhanced Email Collection
 * This script provides improved email collection functionality
 * for guest users when adding to cart or wishlist
 */

// Enhanced Email Collection Object
const EnhancedEmailCollection = {
    // Properties
    userEmail: null,
    emailProvided: false,
    pendingAction: null,
    emailModal: null,
    
    // Initialize the email collection functionality
    init: function() {
        console.log('Initializing Enhanced Email Collection');
        
        // Check if email is already stored in session storage
        const storedEmail = sessionStorage.getItem('guest_user_email');
        if (storedEmail) {
            this.userEmail = storedEmail;
            this.emailProvided = true;
            console.log('Email already provided:', this.userEmail);
        }
        
        // Create email collection modal if it doesn't exist
        if (!document.getElementById('enhancedEmailCollectionModal')) {
            this.createEmailModal();
        }
        
        // Initialize the modal
        this.emailModal = new bootstrap.Modal(document.getElementById('enhancedEmailCollectionModal'));
        
        // Add event listeners
        document.getElementById('enhancedEmailForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitEmail();
        });
        
        // Override the original addToCartWithEmail function
        window.addToCartWithEmail = this.addToCartWithEmail.bind(this);
        
        // Override the original addToWishlistWithEmail function
        window.addToWishlistWithEmail = this.addToWishlistWithEmail.bind(this);
        
        console.log('Enhanced Email Collection initialized');
    },
    
    // Create the email collection modal
    createEmailModal: function() {
        const modalHTML = `
        <div class="modal fade" id="enhancedEmailCollectionModal" tabindex="-1" aria-labelledby="enhancedEmailCollectionModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title" id="enhancedEmailCollectionModalLabel">Please provide your email</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-3">To continue with your purchase and receive updates, please provide your email address:</p>
                        <form id="enhancedEmailForm">
                            <div class="mb-3">
                                <label for="enhancedEmailInput" class="form-label">Email address</label>
                                <input type="email" class="form-control" id="enhancedEmailInput" placeholder="your@email.com" required>
                                <div class="invalid-feedback">Please provide a valid email address.</div>
                            </div>
                            <div class="form-check mb-3">
                                <input class="form-check-input" type="checkbox" id="enhancedSubscribeCheck" checked>
                                <label class="form-check-label" for="enhancedSubscribeCheck">
                                    Subscribe to our newsletter for exclusive offers
                                </label>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">Continue</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        `;
        
        // Append modal to body
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHTML;
        document.body.appendChild(modalContainer);
    },
    
    // Submit email from the modal
    submitEmail: function() {
        const emailInput = document.getElementById('enhancedEmailInput');
        const email = emailInput.value.trim();
        
        // Validate email
        if (!this.validateEmail(email)) {
            emailInput.classList.add('is-invalid');
            return;
        }
        
        // Remove invalid class if previously added
        emailInput.classList.remove('is-invalid');
        
        // Store the email
        this.userEmail = email;
        this.emailProvided = true;
        
        // Save to session storage (client-side)
        sessionStorage.setItem('guest_user_email', email);
        
        // Also save to server session via AJAX
        $.ajax({
            url: '/save_guest_email/',
            type: 'POST',
            data: {
                'email': email,
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'subscribe': document.getElementById('enhancedSubscribeCheck').checked
            },
            success: function(response) {
                console.log('Email saved to session:', response);
            },
            error: function(xhr, status, error) {
                console.error('Error saving email to session:', error);
            }
        });
        
        // Hide the modal
        this.emailModal.hide();
        
        // Execute the pending action if there is one
        if (this.pendingAction) {
            console.log('Executing pending action with email:', email);
            this.pendingAction(email);
            this.pendingAction = null;
        }
        
        // Show a success toast
        toast.success('Email saved! Your cart will be associated with this email.', {
            title: 'Thank You!'
        });
    },
    
    // Add to cart with email
    addToCartWithEmail: function(productId, quantity = 1) {
        if (this.emailProvided) {
            // If email is already provided, proceed with adding to cart
            this.addToCartWithEmailProvided(productId, quantity, this.userEmail);
        } else {
            // Store the pending action and show the email modal
            this.pendingAction = (email) => {
                this.addToCartWithEmailProvided(productId, quantity, email);
            };
            this.emailModal.show();
        }
    },
    
    // Add to cart with email provided
    addToCartWithEmailProvided: function(productId, quantity = 1, email) {
        // Show loading toast
        window.currentLoadingToast = toast.loading('Adding to cart...');
        
        // Make AJAX request to add to cart
        $.ajax({
            url: '/add_to_cart/',
            type: 'POST',
            data: {
                'product_id': productId,
                'quantity': quantity,
                'email': email,
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            success: function(response) {
                // Dismiss loading toast
                toast.dismiss(window.currentLoadingToast);
                
                if (response.success) {
                    // Show success toast
                    toast.success(response.message || 'Product added to cart!');
                    
                    // Update cart count with animation
                    if (response.cart_count !== undefined) {
                        updateCartCountWithAnimation(response.cart_count);
                    }
                    
                    // Update cart button state
                    updateCartButtonState(productId, true);
                } else {
                    // Show error toast
                    toast.error(response.message || 'Failed to add product to cart.');
                }
            },
            error: function(xhr, status, error) {
                // Dismiss loading toast
                toast.dismiss(window.currentLoadingToast);
                
                // Show error toast
                toast.error('An error occurred while adding to cart. Please try again.');
                console.error('Error adding to cart:', error);
            }
        });
    },
    
    // Add to wishlist with email
    addToWishlistWithEmail: function(productId) {
        if (this.emailProvided) {
            // If email is already provided, proceed with adding to wishlist
            this.addToWishlistWithEmailProvided(productId, this.userEmail);
        } else {
            // Store the pending action and show the email modal
            this.pendingAction = (email) => {
                this.addToWishlistWithEmailProvided(productId, email);
            };
            this.emailModal.show();
        }
    },
    
    // Add to wishlist with email provided
    addToWishlistWithEmailProvided: function(productId, email) {
        // Show loading toast
        window.currentLoadingToast = toast.loading('Adding to wishlist...');
        
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
                // Dismiss loading toast
                toast.dismiss(window.currentLoadingToast);
                
                if (response.success) {
                    // Show success toast
                    toast.success(response.message || 'Product added to wishlist!');
                    
                    // Update wishlist button state
                    updateWishlistButtonState(productId, true);
                } else {
                    // Show error toast
                    toast.error(response.message || 'Failed to add product to wishlist.');
                }
            },
            error: function(xhr, status, error) {
                // Dismiss loading toast
                toast.dismiss(window.currentLoadingToast);
                
                // Show error toast
                toast.error('An error occurred while adding to wishlist. Please try again.');
                console.error('Error adding to wishlist:', error);
            }
        });
    },
    
    // Validate an email address
    validateEmail: function(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }
};

// Initialize the enhanced email collection functionality when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    EnhancedEmailCollection.init();
});
