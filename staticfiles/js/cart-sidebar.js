/**
 * Cart Sidebar Functionality
 * This script handles the cart sidebar functionality, including:
 * - Automatically showing the cart sidebar when items are added to cart
 * - Updating cart items in real-time
 * - Handling cart item removal
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize cart sidebar functionality
    initCartSidebar();
});

/**
 * Initialize cart sidebar functionality
 */
function initCartSidebar() {
    // Listen for the custom 'cartUpdated' event
    document.addEventListener('cartUpdated', function(event) {
        // Show the cart sidebar
        showCartSidebar();
        
        // Refresh cart items
        refreshCartItems();
    });
    
    // Add event listener to the add_to_cart function
    // This is a fallback in case the cartUpdated event is not triggered
    const originalAddToCart = window.add_to_cart;
    if (originalAddToCart) {
        window.add_to_cart = function(productId, quantity = 1) {
            // Call the original function
            originalAddToCart(productId, quantity);
            
            // Show the cart sidebar after a short delay to allow the AJAX request to complete
            setTimeout(function() {
                showCartSidebar();
                refreshCartItems();
            }, 1000);
        };
    }
}

/**
 * Show the cart sidebar
 */
function showCartSidebar() {
    const cartSidebar = document.getElementById('modalShoppingCart');
    if (cartSidebar) {
        // Use Bootstrap's offcanvas API to show the sidebar
        const offcanvas = new bootstrap.Offcanvas(cartSidebar);
        offcanvas.show();
    }
}

/**
 * Refresh cart items in the sidebar
 */
function refreshCartItems() {
    // Make an AJAX request to get the latest cart items
    fetch('/get-cart-items/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartSidebar(data);
            }
        })
        .catch(error => {
            console.error('Error refreshing cart items:', error);
        });
}

/**
 * Update the cart sidebar with the latest cart data
 * @param {Object} data - The cart data from the server
 */
function updateCartSidebar(data) {
    const cartItemsList = document.getElementById('cartItemsList');
    const cartCount = document.getElementById('navbar-cart-count');
    const cartButtonCount = document.getElementById('cart-button-count');
    
    // Update cart count in the navbar
    if (cartCount) {
        cartCount.textContent = data.cart_count;
    }
    
    // Update cart count in the button
    if (cartButtonCount) {
        cartButtonCount.textContent = data.cart_count;
    }
    
    // If there are no items in the cart, reload the page to show the empty cart state
    if (data.cart_items.length === 0) {
        location.reload();
        return;
    }
    
    // If the cart items list doesn't exist, reload the page
    if (!cartItemsList) {
        location.reload();
        return;
    }
    
    // Update the cart items list
    // This is a simple implementation - in a real application, you would want to
    // update only the changed items rather than replacing the entire list
    // For now, we'll just reload the page to show the updated cart
    location.reload();
}
