/**
 * Product Filter Handler
 * This script ensures product cards maintain their styling during filtering
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the handler
    ProductFilterHandler.init();
});

const ProductFilterHandler = {
    /**
     * Initialize the handler
     */
    init: function() {
        // Listen for the productsFiltered event
        document.addEventListener('productsFiltered', this.handleProductsFiltered.bind(this));
        
        // Override any existing filter functions
        this.overrideFilterFunctions();
    },
    
    /**
     * Handle the productsFiltered event
     */
    handleProductsFiltered: function() {
        // Refresh all visible product cards
        this.refreshProductCards();
    },
    
    /**
     * Refresh all visible product cards
     */
    refreshProductCards: function() {
        // Get all visible product cards
        const visibleCards = document.querySelectorAll('.product-card-nigerian:not([style*="display: none"])');
        
        // Apply any necessary styling or animations
        visibleCards.forEach(card => {
            // Ensure proper styling is maintained
            card.style.opacity = '0';
            
            // Use setTimeout to create a staggered animation effect
            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 50);
        });
    },
    
    /**
     * Override any existing filter functions
     */
    overrideFilterFunctions: function() {
        // Check if jQuery AJAX is being used for filtering
        if (typeof $ !== 'undefined') {
            // Store the original jQuery AJAX function
            const originalAjax = $.ajax;
            
            // Override the function
            $.ajax = function() {
                // Get the original arguments
                const originalArguments = arguments;
                
                // Check if this is a product loading AJAX call
                if (originalArguments[0] && 
                    (originalArguments[0].url && originalArguments[0].url.includes('load_more_products') || 
                     originalArguments[0].url && originalArguments[0].url.includes('filter_products'))) {
                    
                    // Get the original success callback
                    const originalSuccess = originalArguments[0].success;
                    
                    // Override the success callback
                    originalArguments[0].success = function() {
                        // Call the original success callback
                        if (originalSuccess) {
                            originalSuccess.apply(this, arguments);
                        }
                        
                        // Refresh product cards after AJAX completes
                        setTimeout(() => {
                            ProductFilterHandler.refreshProductCards();
                        }, 100);
                    };
                }
                
                // Call the original AJAX function
                return originalAjax.apply(this, originalArguments);
            };
        }
    }
};
