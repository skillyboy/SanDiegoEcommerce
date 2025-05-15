/**
 * Unified Product Card Handler
 * This script ensures consistent product card styling during filtering, searching, and AJAX loading
 */

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    UnifiedCardHandler.init();
});

const UnifiedCardHandler = {
    /**
     * Initialize the handler
     */
    init: function() {
        console.log('Initializing Unified Card Handler');

        // Apply initial styling to all cards
        this.applyCardStyling();

        // Override filter and search functions
        this.overrideFilterFunctions();

        // Listen for AJAX content loaded
        document.addEventListener('ajaxContentLoaded', this.handleAjaxContentLoaded.bind(this));

        // Listen for search and filter events
        document.addEventListener('productsFiltered', this.handleProductsFiltered.bind(this));
        document.addEventListener('productsSearched', this.handleProductsSearched.bind(this));

        // Add mutation observer to detect DOM changes
        this.setupMutationObserver();

        console.log('Unified Card Handler initialized');
    },

    /**
     * Apply consistent styling to all product cards
     */
    applyCardStyling: function() {
        // Get all product cards
        const productCards = document.querySelectorAll('.product-card-nigerian, .product-card-african, .featured-product-card');

        productCards.forEach(card => {
            // Ensure card has proper classes
            card.classList.add('unified-card');

            // Ensure card has proper data attributes
            const productId = card.getAttribute('data-product-id') ||
                             card.closest('[data-product-id]')?.getAttribute('data-product-id');

            if (productId && !card.hasAttribute('data-product-id')) {
                card.setAttribute('data-product-id', productId);
            }

            // Ensure add to cart button has proper styling and event
            const addToCartBtn = card.querySelector('.btn-add-to-cart-nigerian, .btn-add-to-cart');
            if (addToCartBtn && !addToCartBtn.classList.contains('unified-btn')) {
                addToCartBtn.classList.add('unified-btn');

                // Ensure button has proper onclick attribute
                if (!addToCartBtn.hasAttribute('onclick') && productId) {
                    addToCartBtn.setAttribute('onclick', `addToCartWithEmail(${productId})`);
                }
            }

            // Ensure card has consistent styling
            this.ensureCardStyling(card);

            // Apply animation classes
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';

            // Staggered animation
            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, Math.random() * 200); // Random delay for staggered effect
        });
    },

    /**
     * Ensure consistent styling for a card
     */
    ensureCardStyling: function(card) {
        // Make sure card has proper border and shadow
        card.style.border = 'none';
        card.style.borderRadius = '16px';
        card.style.overflow = 'hidden';
        card.style.boxShadow = '0 10px 25px rgba(0,0,0,0.08)';
        card.style.transition = 'all 0.4s ease';

        // Make sure card has proper hover effect
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 20px 30px rgba(0,0,0,0.12)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '0 10px 25px rgba(0,0,0,0.08)';
        });

        // Ensure product image has proper styling
        const productImg = card.querySelector('img');
        if (productImg) {
            productImg.style.width = '100%';
            productImg.style.height = '250px';
            productImg.style.objectFit = 'cover';
            productImg.style.transition = 'transform 0.6s ease';
        }

        // Ensure product title has proper styling
        const productTitle = card.querySelector('.product-title, h3');
        if (productTitle) {
            productTitle.style.fontFamily = "'Playfair Display', serif";
            productTitle.style.fontSize = '1.3rem';
            productTitle.style.marginBottom = '10px';
            productTitle.style.color = '#2E3A23';
        }

        // Ensure product price has proper styling
        const productPrice = card.querySelector('.price-current, .product-price');
        if (productPrice) {
            productPrice.style.fontSize = '1.2rem';
            productPrice.style.fontWeight = '700';
            productPrice.style.color = '#008751';
        }
    },

    /**
     * Handle AJAX content loaded event
     */
    handleAjaxContentLoaded: function() {
        console.log('AJAX content loaded, applying card styling');
        setTimeout(() => {
            this.applyCardStyling();
        }, 100);
    },

    /**
     * Handle products filtered event
     */
    handleProductsFiltered: function() {
        console.log('Products filtered, applying card styling');
        setTimeout(() => {
            this.applyCardStyling();
        }, 100);
    },

    /**
     * Handle products searched event
     */
    handleProductsSearched: function() {
        console.log('Products searched, applying card styling');
        setTimeout(() => {
            this.applyCardStyling();
        }, 100);
    },

    /**
     * Override filter and search functions
     */
    overrideFilterFunctions: function() {
        // Override jQuery AJAX if available
        if (typeof $ !== 'undefined') {
            const originalAjax = $.ajax;

            $.ajax = function() {
                const originalArguments = arguments;

                // Check if this is a product-related AJAX call
                if (originalArguments[0] &&
                    (originalArguments[0].url && (
                        originalArguments[0].url.includes('load_more_products') ||
                        originalArguments[0].url.includes('filter_products') ||
                        originalArguments[0].url.includes('search_products')
                    ))) {

                    // Override success callback
                    const originalSuccess = originalArguments[0].success;

                    originalArguments[0].success = function() {
                        // Call original callback
                        if (originalSuccess) {
                            originalSuccess.apply(this, arguments);
                        }

                        // Apply card styling
                        setTimeout(() => {
                            UnifiedCardHandler.applyCardStyling();

                            // Dispatch event for other handlers
                            document.dispatchEvent(new CustomEvent('ajaxContentLoaded'));
                        }, 100);
                    };
                }

                // Call original AJAX function
                return originalAjax.apply(this, originalArguments);
            };
        }

        // Override window.filterProducts if it exists
        if (typeof window.filterProducts === 'function') {
            const originalFilterFunction = window.filterProducts;

            window.filterProducts = function() {
                const result = originalFilterFunction.apply(this, arguments);

                // Apply card styling after filtering
                setTimeout(() => {
                    UnifiedCardHandler.applyCardStyling();

                    // Dispatch event for other handlers
                    document.dispatchEvent(new CustomEvent('productsFiltered'));
                }, 100);

                return result;
            };
        }
    },

    /**
     * Setup mutation observer to detect DOM changes
     */
    setupMutationObserver: function() {
        // Create observer
        const observer = new MutationObserver((mutations) => {
            let shouldUpdate = false;

            // Check if any mutations added product cards
            mutations.forEach(mutation => {
                if (mutation.type === 'childList' && mutation.addedNodes.length) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && (
                            node.classList?.contains('product-card-nigerian') ||
                            node.classList?.contains('product-card-african') ||
                            node.classList?.contains('featured-product-card') ||
                            node.querySelector?.('.product-card-nigerian, .product-card-african, .featured-product-card')
                        )) {
                            shouldUpdate = true;
                        }
                    });
                }
            });

            // Apply styling if needed
            if (shouldUpdate) {
                setTimeout(() => {
                    this.applyCardStyling();
                }, 100);
            }
        });

        // Start observing
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
};
