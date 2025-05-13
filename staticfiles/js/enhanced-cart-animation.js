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
    // Get the product element
    const productElement = document.querySelector(`[data-product-id="${productId}"]`);
    if (!productElement) {
        // If product element not found, just proceed with adding to cart
        addToCartWithEmailProvided(productId, quantity, email);
        return;
    }
    
    // Get product image
    const productImg = productElement.querySelector('.product-img');
    if (!productImg) {
        // If product image not found, just proceed with adding to cart
        addToCartWithEmailProvided(productId, quantity, email);
        return;
    }
    
    // Get cart icon position
    const cartIcon = document.querySelector('.navbar .fa-shopping-cart');
    if (!cartIcon) {
        // If cart icon not found, just proceed with adding to cart
        addToCartWithEmailProvided(productId, quantity, email);
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
    bucket.style.width = '40px';
    bucket.style.height = '40px';
    bucket.style.borderRadius = '50% 50% 0 0';
    bucket.style.border = '3px solid #D2691E';
    bucket.style.borderBottom = 'none';
    bucket.style.left = `${cartIcon.getBoundingClientRect().left}px`;
    bucket.style.top = `${cartIcon.getBoundingClientRect().top + 20}px`;
    bucket.style.opacity = '0';
    bucket.style.transform = 'scale(0)';
    bucket.style.transition = 'all 0.4s ease-out';
    
    // Add bucket to DOM
    document.body.appendChild(bucket);
    
    // Show bucket with delay
    setTimeout(() => {
        bucket.style.opacity = '1';
        bucket.style.transform = 'scale(1)';
    }, 300);
    
    // Start animation after a small delay
    setTimeout(() => {
        // Show loading toast
        window.currentLoadingToast = toast.loading('Adding to cart...');
        
        // Animate flying element to cart
        const cartRect = cartIcon.getBoundingClientRect();
        flyingElement.style.left = `${cartRect.left}px`;
        flyingElement.style.top = `${cartRect.top}px`;
        flyingElement.style.opacity = '0.7';
        flyingElement.style.transform = 'scale(0.3)';
        
        // Shake cart icon when product reaches it
        setTimeout(() => {
            cartIcon.classList.add('cart-shake');
            
            // Make AJAX request to add to cart
            addToCartWithEmailProvided(productId, quantity, email);
            
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
        }, 800);
    }, 100);
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
        25% { transform: rotate(10deg); }
        50% { transform: rotate(-10deg); }
        75% { transform: rotate(5deg); }
        100% { transform: rotate(0); }
    }
    
    .cart-shake {
        animation: cartShake 0.5s ease-in-out;
    }
    
    @keyframes cartCountPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.5); }
        100% { transform: scale(1); }
    }
    
    .cart-count-pulse {
        animation: cartCountPulse 0.5s ease-in-out;
    }
    
    @keyframes cartIconBounce {
        0% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0); }
    }
    
    .cart-icon-bounce {
        animation: cartIconBounce 0.5s ease-in-out;
    }
    
    .flying-product {
        pointer-events: none;
    }
    
    .cart-bucket {
        pointer-events: none;
    }
`;
document.head.appendChild(style);

// Override the original addToCartWithEmailProvided function
const originalAddToCartWithEmailProvided = window.addToCartWithEmailProvided;
window.addToCartWithEmailProvided = function(productId, quantity = 1, email) {
    // Use enhanced animation
    enhancedCartAnimation(productId, quantity, email);
};

// Override the original updateCartCountWithAnimation function
const originalUpdateCartCountWithAnimation = window.updateCartCountWithAnimation;
window.updateCartCountWithAnimation = function(count) {
    // Use enhanced animation
    updateCartCountWithEnhancedAnimation(count);
};
