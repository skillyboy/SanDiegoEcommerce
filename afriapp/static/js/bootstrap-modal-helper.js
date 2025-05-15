/**
 * Bootstrap Modal Helper
 * This script provides a safe way to work with Bootstrap modals
 * and fixes issues with Modal.getInstance
 */

// Create a global modal manager
window.ModalManager = {
    // Store active modals
    activeModals: {},

    // Show a modal safely
    show: function(modalElement) {
        if (!modalElement) {
            console.error('Modal element not found');
            return null;
        }

        try {
            // Try to use Bootstrap's Modal
            const modalInstance = new bootstrap.Modal(modalElement);

            // Store the instance
            const modalId = modalElement.id || `modal-${Date.now()}`;
            this.activeModals[modalId] = modalInstance;

            // Show the modal
            modalInstance.show();

            return modalInstance;
        } catch (error) {
            console.error('Error showing modal:', error);
            return null;
        }
    },

    // Hide a modal safely
    hide: function(modalElement) {
        if (!modalElement) {
            console.error('Modal element not found');
            return;
        }

        try {
            // Try to get the instance from our store first
            const modalId = modalElement.id || `modal-${Date.now()}`;
            let modalInstance = this.activeModals[modalId];

            // If not found in our store, try Bootstrap's getInstance
            if (!modalInstance) {
                try {
                    modalInstance = bootstrap.Modal.getInstance(modalElement);
                } catch (error) {
                    // If Bootstrap's getInstance fails, create a new instance
                    modalInstance = new bootstrap.Modal(modalElement);
                }
            }

            // Hide the modal
            if (modalInstance) {
                modalInstance.hide();

                // Remove from our store
                delete this.activeModals[modalId];
            } else {
                // Fallback: use jQuery if available
                if (typeof $ !== 'undefined') {
                    $(modalElement).modal('hide');
                } else {
                    // Last resort: add hidden.bs.modal class
                    modalElement.classList.add('hidden');
                    modalElement.style.display = 'none';

                    // Remove modal backdrop if exists
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.parentNode.removeChild(backdrop);
                    }

                    // Remove modal-open class from body
                    document.body.classList.remove('modal-open');
                }
            }
        } catch (error) {
            console.error('Error hiding modal:', error);
        }
    },

    // Get a modal instance safely
    getInstance: function(modalElement) {
        if (!modalElement) {
            console.error('Modal element not found');
            return null;
        }

        try {
            // Try to get the instance from our store first
            const modalId = modalElement.id || `modal-${Date.now()}`;
            let modalInstance = this.activeModals[modalId];

            // If not found in our store, create a new instance
            if (!modalInstance) {
                try {
                    // Create a new instance instead of using getInstance to avoid infinite recursion
                    modalInstance = new bootstrap.Modal(modalElement);

                    // Store the instance
                    this.activeModals[modalId] = modalInstance;
                } catch (error) {
                    console.error('Error creating modal instance:', error);
                    return null;
                }
            }

            return modalInstance;
        } catch (error) {
            console.error('Error getting modal instance:', error);
            return null;
        }
    }
};

// Polyfill for bootstrap.Modal.getInstance if it doesn't exist
if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
    // Add getInstance if it doesn't exist
    if (typeof bootstrap.Modal.getInstance !== 'function') {
        bootstrap.Modal.getInstance = function(element) {
            return ModalManager.getInstance(element);
        };
    }

    // Add a direct hideModal function for convenience
    if (typeof bootstrap.Modal.hideModal !== 'function') {
        bootstrap.Modal.hideModal = function(element) {
            if (!element) return;

            try {
                // Try to get instance first
                const instance = bootstrap.Modal.getInstance(element);
                if (instance) {
                    instance.hide();
                    return true;
                }

                // If no instance, try jQuery
                if (typeof $ !== 'undefined') {
                    $(element).modal('hide');
                    return true;
                }

                // Last resort: manual DOM manipulation
                element.classList.remove('show');
                element.style.display = 'none';
                document.body.classList.remove('modal-open');

                // Remove backdrop if exists
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.parentNode.removeChild(backdrop);
                }

                return true;
            } catch (error) {
                console.error('Error hiding modal:', error);
                return false;
            }
        };
    }
}
