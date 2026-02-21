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
    // Initial fetch so sidebar has content on first open
    refreshCartItems();
});

/**
 * Initialize cart sidebar functionality
 */
function initCartSidebar() {
    const cartSidebarEl = document.getElementById('modalShoppingCart');
    if (cartSidebarEl) {
        cartSidebarEl.addEventListener('shown.bs.offcanvas', function() {
            refreshCartItems();
        });
    }

    // Listen for the custom 'cartUpdated' event
    document.addEventListener('cartUpdated', function(event) {
        showCartSidebar();
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
    fetch('/get-cart-items/', { credentials: 'same-origin', headers: { 'X-Requested-With': 'XMLHttpRequest' } })
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
    const navbarCount = document.getElementById('navbar-cart-count');
    const cartButtonCount = document.getElementById('cart-button-count');
    const headerStrong = document.querySelector('#modalShoppingCart .offcanvas-header strong');
    const subtotalEl = document.getElementById('cartSidebarSubtotalValue') || document.querySelector('#modalShoppingCart .offcanvas-footer strong.ms-auto');
    const subtotalInline = document.getElementById('cartSidebarSubtotal');

    const items = data.items || data.cart_items || data.cartItems || [];
    const count = data.count || data.cart_count || data.cartCount || (Array.isArray(items) ? items.reduce((s, i) => s + (i.quantity || i.qty || 0), 0) : 0);
    const subtotal = typeof data.subtotal !== 'undefined' ? data.subtotal : data.cart_subtotal;

    // Update cart counters
    if (navbarCount) navbarCount.textContent = count;
    if (cartButtonCount) cartButtonCount.textContent = count;
    if (headerStrong) headerStrong.textContent = `Your Cart (${count})`;
    if (subtotalEl && typeof subtotal !== 'undefined') {
        subtotalEl.textContent = `$${Number(subtotal).toFixed(2)}`;
    }
    if (subtotalInline && typeof subtotal !== 'undefined') {
        subtotalInline.textContent = `$${Number(subtotal).toFixed(2)}`;
    }

    if (!cartItemsList) {
        return;
    }

    // Empty state
    if (!Array.isArray(items) || items.length === 0) {
        cartItemsList.innerHTML = `
            <div class="px-4 py-6 text-center">
                <h6 class="mb-2">Your cart is empty 😞</h6>
                <p class="text-muted">Add products to your cart and they will appear here.</p>
            </div>`;
        return;
    }

    // Render items
    const fragment = document.createDocumentFragment();
    items.forEach(item => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        const cid = item.cart_item_id || item.id || '';
        if (cid) {
            li.id = `cart-item-${cid}`;
        }
        const productUrl = item.url || item.product_url || `/product/${item.product_id || ''}/`;
        const img = item.image_url || item.image || '/static/img/placeholder.png';
        const name = item.name || item.product_name || '';
        const unitPrice = (typeof item.unit_price !== 'undefined') ? item.unit_price : (item.price || 0);
        const quantity = item.quantity || item.qty || 1;
        const totalPrice = (typeof item.total_price !== 'undefined') ? item.total_price : (unitPrice * quantity);

        li.innerHTML = `
            <div class="row align-items-center">
                <div class="col-4">
                    <a href="${productUrl}" class="position-relative">
                        <img class="img-fluid rounded shadow-sm" src="${img}" alt="${name}">
                    </a>
                </div>
                <div class="col-8">
                    <p class="fs-sm fw-bold mb-1">
                        <a class="text-body" href="${productUrl}">${name}</a>
                    </p>
                    <span class="text-muted d-block mb-3">$${Number(totalPrice).toFixed(2)} (${quantity} x $${Number(unitPrice).toFixed(2)})</span>
                    <div class="d-flex align-items-center">
                        <button class="fs-xs text-danger ms-auto remove-item" data-id="${cid}">
                            <i class="fe fe-x"></i> Remove
                        </button>
                    </div>
                </div>
            </div>
        `;
        fragment.appendChild(li);
    });

    cartItemsList.innerHTML = '';
    cartItemsList.appendChild(fragment);
}

// Expose refresh/update for inline modal scripts
window.refreshCartSidebar = refreshCartItems;
window.updateCartSidebar = updateCartSidebar;
