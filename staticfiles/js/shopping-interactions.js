/**
 * Unified Shopping Interactions Handler
 * Manages cart, wishlist, and other shopping interactions with email collection
 */

class ShoppingInteractions {
    constructor() {
        this.emailCollected = false;
        this.modal = new bootstrap.Modal(document.getElementById('emailCollectionModal'));
        this.pendingAction = null;
        this.setupEventListeners();
        this.checkEmailStatus();
    }

    setupEventListeners() {
        // Email collection form submission
        document.getElementById('emailCollectionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleEmailCollection(e);
        });

        // Shopping interactions
        document.querySelectorAll('[data-shopping-action]').forEach(element => {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                const action = e.currentTarget.dataset.shoppingAction;
                const itemId = e.currentTarget.dataset.itemId;
                this.handleShoppingAction(action, itemId);
            });
        });
    }

    async checkEmailStatus() {
        try {
            const response = await fetch('/check-email-status/');
            const data = await response.json();
            this.emailCollected = data.has_email;
        } catch (error) {
            console.error('Error checking email status:', error);
        }
    }

    updateModalContent(action) {
        const modal = document.getElementById('emailCollectionModal');
        const actionMessage = modal.querySelector('.action-message');
        const icons = modal.querySelectorAll('.action-icon i');
        
        // Hide all icons first
        icons.forEach(icon => icon.classList.add('d-none'));
        
        // Show relevant icon and message
        switch(action) {
            case 'cart':
                modal.querySelector('.cart-icon').classList.remove('d-none');
                actionMessage.textContent = 'Enter your email to add items to your cart';
                break;
            case 'wishlist':
                modal.querySelector('.wishlist-icon').classList.remove('d-none');
                actionMessage.textContent = 'Enter your email to save items to your wishlist';
                break;
            case 'save':
                modal.querySelector('.save-icon').classList.remove('d-none');
                actionMessage.textContent = 'Enter your email to save this item for later';
                break;
        }
        
        document.getElementById('action_type').value = action;
    }

    async handleEmailCollection(event) {
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const spinner = submitButton.querySelector('.spinner-border');
        
        try {
            // Show loading state
            submitButton.disabled = true;
            spinner.classList.remove('d-none');
            
            const formData = new FormData(form);
            const response = await fetch('/collect-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    email: formData.get('email'),
                    action_type: formData.get('action_type'),
                    subscribe_newsletter: formData.get('newsletter_subscribe') === 'on'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.emailCollected = true;
                this.modal.hide();
                this.showToast('Success', data.message);
                
                // Execute pending action if any
                if (this.pendingAction) {
                    const { action, itemId } = this.pendingAction;
                    this.executePendingAction(action, itemId);
                    this.pendingAction = null;
                }
            } else {
                if (data.requires_login) {
                    window.location.href = data.redirect_url;
                    return;
                }
                document.getElementById('emailError').textContent = data.error;
            }
        } catch (error) {
            console.error('Error collecting email:', error);
            document.getElementById('emailError').textContent = 'An error occurred. Please try again.';
        } finally {
            // Reset loading state
            submitButton.disabled = false;
            spinner.classList.add('d-none');
        }
    }

    async handleShoppingAction(action, itemId) {
        if (!this.emailCollected) {
            this.pendingAction = { action, itemId };
            this.updateModalContent(action);
            this.modal.show();
            return;
        }
        
        await this.executePendingAction(action, itemId);
    }

    async executePendingAction(action, itemId) {
        try {
            let endpoint;
            switch(action) {
                case 'cart':
                    endpoint = `/add-to-cart/${itemId}/`;
                    break;
                case 'wishlist':
                    endpoint = `/add-to-wishlist/${itemId}/`;
                    break;
                case 'save':
                    endpoint = `/save-for-later/${itemId}/`;
                    break;
                default:
                    console.error('Unknown action:', action);
                    return;
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            const data = await response.json();
            if (data.success) {
                this.showToast('Success', data.message);
                this.updateUI(action, data);
            } else {
                this.showToast('Error', data.error);
            }
        } catch (error) {
            console.error('Error executing action:', error);
            this.showToast('Error', 'An error occurred. Please try again.');
        }
    }

    updateUI(action, data) {
        // Update relevant UI elements based on the action
        switch(action) {
            case 'cart':
                document.querySelector('.cart-count').textContent = data.cart_count;
                // Trigger cart sidebar update if needed
                document.dispatchEvent(new CustomEvent('cartUpdated', { detail: data }));
                break;
            case 'wishlist':
                document.querySelector('.wishlist-count').textContent = data.wishlist_count;
                break;
            // Add other UI updates as needed
        }
    }

    showToast(title, message) {
        const toast = new bootstrap.Toast(document.getElementById('successToast'));
        document.querySelector('#successToast .toast-header strong').textContent = title;
        document.querySelector('#successToast .toast-body').textContent = message;
        toast.show();
    }
}

// Initialize shopping interactions when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.shoppingInteractions = new ShoppingInteractions();
});
