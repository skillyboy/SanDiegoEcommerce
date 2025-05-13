/**
 * Product Card Updater
 * This script updates all product cards to use the new improved template
 * and removes Nigerian flags from product cards
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the product card updater
    ProductCardUpdater.init();
});

const ProductCardUpdater = {
    // Initialize the product card updater
    init: function() {
        console.log('Initializing Product Card Updater');
        
        // Update product cards on initial page load
        this.updateProductCards();
        
        // Add event listener for AJAX loaded content
        document.addEventListener('ajaxContentLoaded', function() {
            ProductCardUpdater.updateProductCards();
        });
        
        // Override the original filter function to maintain styling
        this.overrideFilterFunction();
        
        console.log('Product Card Updater initialized');
    },
    
    // Update all product cards to use the new improved template
    updateProductCards: function() {
        // Find all product cards
        const productCards = document.querySelectorAll('.product-card, .product-item');
        
        productCards.forEach(card => {
            // Skip if already processed
            if (card.classList.contains('product-card-african')) return;
            
            // Get product data
            const productId = card.getAttribute('data-product-id');
            const productName = card.querySelector('.product-title a')?.textContent || '';
            const productPrice = card.querySelector('.price-current')?.textContent || '';
            const productImage = card.querySelector('img')?.src || '';
            const productLink = card.querySelector('.product-title a')?.href || '';
            const productDescription = card.querySelector('.product-description')?.textContent || '';
            
            // Create new card with improved template
            this.createImprovedCard(card, {
                id: productId,
                name: productName,
                price: productPrice,
                image: productImage,
                link: productLink,
                description: productDescription
            });
            
            // Remove Nigerian flags if present
            this.removeNigerianFlags(card);
        });
    },
    
    // Create improved card with the new template
    createImprovedCard: function(originalCard, productData) {
        // Skip if no product ID
        if (!productData.id) return;
        
        // Add African-inspired styling class
        originalCard.classList.add('product-card-african');
        
        // Ensure the card has the necessary structure
        if (!originalCard.querySelector('.product-img-container')) {
            // Get the original image element
            const originalImg = originalCard.querySelector('img');
            
            if (originalImg) {
                // Create image container
                const imgContainer = document.createElement('div');
                imgContainer.className = 'product-img-container';
                
                // Move the image into the container
                originalImg.parentNode.insertBefore(imgContainer, originalImg);
                imgContainer.appendChild(originalImg);
                
                // Add class to image
                originalImg.classList.add('product-img');
                
                // Add quick actions overlay
                const actionsOverlay = document.createElement('div');
                actionsOverlay.className = 'product-actions-overlay';
                actionsOverlay.innerHTML = `
                    <div class="action-buttons">
                        <button class="action-btn quick-view" data-bs-toggle="modal" data-bs-target="#modalProduct${productData.id}" title="Quick View">
                            <i class="fe fe-eye"></i>
                        </button>
                        <button class="action-btn add-cart" onclick="addToCartWithEmail(${productData.id})" title="Add to Cart">
                            <i class="fe fe-shopping-cart"></i>
                        </button>
                        <button class="action-btn wishlist" onclick="addToWishlistWithEmail(${productData.id})" title="Add to Wishlist">
                            <i class="fe fe-heart"></i>
                        </button>
                    </div>
                `;
                imgContainer.appendChild(actionsOverlay);
                
                // Add product link overlay
                const linkOverlay = document.createElement('a');
                linkOverlay.className = 'product-link-overlay';
                linkOverlay.href = productData.link;
                linkOverlay.setAttribute('aria-label', `View ${productData.name} details`);
                imgContainer.appendChild(linkOverlay);
            }
        }
        
        // Ensure the card has the product info section
        if (!originalCard.querySelector('.product-info')) {
            // Create product info container
            const infoContainer = document.createElement('div');
            infoContainer.className = 'product-info';
            
            // Move product title, price, etc. into the container
            const productTitle = originalCard.querySelector('.product-title');
            const productPrice = originalCard.querySelector('.product-price');
            const productDescription = originalCard.querySelector('.product-description');
            
            if (productTitle) infoContainer.appendChild(productTitle.cloneNode(true));
            if (productDescription) {
                const shortDesc = document.createElement('div');
                shortDesc.className = 'cultural-significance-short';
                shortDesc.textContent = productDescription.textContent.length > 60 ? 
                    productDescription.textContent.substring(0, 60) + '...' : 
                    productDescription.textContent;
                infoContainer.appendChild(shortDesc);
            }
            if (productPrice) infoContainer.appendChild(productPrice.cloneNode(true));
            
            // Add "Add to Cart" button
            const addToCartBtn = document.createElement('button');
            addToCartBtn.className = 'btn-add-to-cart-african';
            addToCartBtn.setAttribute('onclick', `addToCartWithEmail(${productData.id})`);
            addToCartBtn.setAttribute('data-product-id', productData.id);
            addToCartBtn.innerHTML = '<i class="fas fa-shopping-cart me-2"></i>Add to Cart';
            infoContainer.appendChild(addToCartBtn);
            
            // Append the info container to the card
            originalCard.appendChild(infoContainer);
            
            // Remove original elements to avoid duplication
            if (productTitle) productTitle.remove();
            if (productPrice) productPrice.remove();
            if (productDescription) productDescription.remove();
        }
    },
    
    // Remove Nigerian flags from product cards
    removeNigerianFlags: function(card) {
        // Find and remove any flag images
        const flagImages = card.querySelectorAll('img[src*="flag"], img[alt*="flag"], img[src*="nigeria"], img[alt*="nigeria"]');
        flagImages.forEach(img => img.remove());
        
        // Remove flag classes
        card.querySelectorAll('.flag, .country-flag').forEach(el => {
            el.classList.remove('flag', 'country-flag');
        });
    },
    
    // Override the original filter function to maintain styling
    overrideFilterFunction: function() {
        // Check if the original filter function exists
        if (typeof window.filterProducts === 'function') {
            // Store the original function
            const originalFilterFunction = window.filterProducts;
            
            // Override the function
            window.filterProducts = function() {
                // Call the original function
                const result = originalFilterFunction.apply(this, arguments);
                
                // Update product cards after filtering
                setTimeout(() => {
                    ProductCardUpdater.updateProductCards();
                }, 100);
                
                return result;
            };
        }
        
        // Also override any AJAX success handlers that might load products
        if (typeof $ !== 'undefined') {
            // Store the original jQuery AJAX function
            const originalAjax = $.ajax;
            
            // Override the function
            $.ajax = function() {
                const originalOptions = arguments[0];
                
                // If this is a product loading AJAX request
                if (originalOptions.url && 
                    (originalOptions.url.includes('/load_more_products') || 
                     originalOptions.url.includes('/filter_products'))) {
                    
                    // Store the original success handler
                    const originalSuccess = originalOptions.success;
                    
                    // Override the success handler
                    originalOptions.success = function() {
                        // Call the original success handler
                        if (originalSuccess) {
                            originalSuccess.apply(this, arguments);
                        }
                        
                        // Update product cards after loading
                        setTimeout(() => {
                            ProductCardUpdater.updateProductCards();
                            
                            // Trigger custom event for other scripts
                            document.dispatchEvent(new CustomEvent('ajaxContentLoaded'));
                        }, 100);
                    };
                    
                    // Update the arguments
                    arguments[0] = originalOptions;
                }
                
                // Call the original AJAX function
                return originalAjax.apply(this, arguments);
            };
        }
    }
};
