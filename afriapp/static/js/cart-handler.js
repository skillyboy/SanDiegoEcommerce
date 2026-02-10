/**
 * Enhanced Cart Handler
 * This script handles adding products to cart
 * and provides smooth animations and error handling
 */

// Global variables
let isAddingToCart = false;
let emailCollected = false;

// Disable add-to-cart sound: intercept Audio.play for elements marked as cart sound
(function() {
    try {
        const _origPlay = HTMLAudioElement.prototype.play;
        HTMLAudioElement.prototype.play = function() {
            try {
                const el = this;
                const id = (el.id || '').toLowerCase();
                const cls = (el.className || '').toLowerCase();
                const ds = (el.dataset && el.dataset.sound) ? el.dataset.sound : '';
                if (id.includes('cart') || cls.indexOf('cart') !== -1 || ds === 'add-to-cart') {
                    // skip playing sound for cart-related audio elements
                    return Promise.resolve();
                }
            } catch (e) {
                // ignore and fall through to original play
            }
            return _origPlay.apply(this, arguments);
        };
    } catch (e) {
        // environment may not support HTMLAudioElement - ignore
    }
})();

/**
 * Add to cart with email collection
 * @param {number} productId - The ID of the product to add
 * @param {number} quantity - The quantity to add (default: 1)
 */
function addToCartWithEmail(productId, quantity = 1) {
    // Prevent multiple clicks
    if (isAddingToCart) {
        showToast('Please wait while we process your request...', 'info');
        return;
    }

    // Set flag to prevent multiple clicks
    isAddingToCart = true;

    // Directly add to cart without showing any modal
    try {
        const qty = Number(quantity) || 1;
        addToCart(productId, qty);
    } catch (err) {
        console.error('Error adding to cart:', err);
        showToast('An error occurred. Please try again.', 'error');
        isAddingToCart = false;
    }
}

/**
 * Save email to session
 * @param {string} email - The email to save
 * @param {boolean} subscribeToNewsletter - Whether to subscribe to newsletter
 * @returns {Promise} - Promise that resolves with the response
 */
function saveEmailToSession(email, subscribeToNewsletter) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '/save_guest_email/',
            type: 'POST',
            data: {
                'email': email,
                'subscribe': subscribeToNewsletter,
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            success: function(response) {
                resolve(response);
            },
            error: function(xhr, status, error) {
                reject(error);
            }
        });
    });
}

/**
 * Check stock availability for a product.
 * Falls back to "available" if the check fails to avoid blocking add-to-cart.
 */
function checkStockAvailability(productId, quantity = 1) {
    return new Promise((resolve) => {
        if (!productId) {
            resolve({ available: true });
            return;
        }

        const qty = Number(quantity) || 1;
        const url = `/check-stock/${productId}/?quantity=${encodeURIComponent(qty)}`;
        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json,text/*'
            },
            credentials: 'same-origin'
        })
        .then(async (resp) => {
            // If auth is required or redirected, allow add-to-cart to handle login
            if (resp.status === 401 || resp.status === 302) {
                resolve({ available: true });
                return;
            }
            const text = await resp.text();
            let data = {};
            try {
                data = text ? JSON.parse(text) : {};
            } catch (e) {
                resolve({ available: true });
                return;
            }
            if (!resp.ok || data.success === false) {
                resolve({ available: true, message: data.error || data.message });
                return;
            }
            resolve({
                available: typeof data.available === 'boolean' ? data.available : true,
                message: data.message || ''
            });
        })
        .catch(() => {
            resolve({ available: true });
        });
    });
}

/**
 * Add to cart
 * @param {number} productId - The ID of the product to add
 * @param {number} quantity - The quantity to add
 */
function addToCart(productId, quantity) {
    // Validate inputs
    if (!productId || quantity < 1) {
        showToast('Invalid product or quantity', 'error');
        return;
    }

    // Show loading toast
    showToast('Adding to cart...', 'loading');

    // Check stock availability first
    checkStockAvailability(productId, quantity).then(response => {
        if (!response.available) {
            showToast(response.message || 'Product is out of stock', 'error');
            return;
        }

        // Add flying animation
        addToCartAnimation(productId);

        // Use fetch instead of jQuery.ajax to avoid other scripts' global handlers
        (async function() {
            const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : getCookie('csrftoken'));
            try {
                const resp = await fetch(`/add_to_cart/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json,text/*'
                    },
                    body: new URLSearchParams({ quantity: String(quantity) }),
                    credentials: 'same-origin'
                });

                isAddingToCart = false;

                const text = await resp.text();

                // Handle explicit authentication failure (401) by redirecting to login
                if (resp.status === 401) {
                    // ensure flag cleared
                    isAddingToCart = false;
                    try {
                        const maybeJson = text ? JSON.parse(text) : null;
                        const loginUrl = (maybeJson && maybeJson.login_url) ? maybeJson.login_url : null;
                        const next = encodeURIComponent(window.location.pathname + window.location.search);
                        window.location.href = loginUrl || (`/accounts/login/?next=${next}`);
                    } catch (e) {
                        const next = encodeURIComponent(window.location.pathname + window.location.search);
                        window.location.href = `/accounts/login/?next=${next}`;
                    }
                    return;
                }

                // Try parse JSON first
                let json;
                try {
                    json = text ? JSON.parse(text) : {};
                } catch (e) {
                    console.error('Expected JSON but received:', text);
                    if (typeof text === 'string' && text.indexOf('<!DOCTYPE') !== -1) {
                        showToast('Session expired or not authenticated. Please sign in and try again.', 'error');
                        return;
                    }
                    showToast('Unexpected server response. Check console for details.', 'error');
                    return;
                }

                if (!resp.ok) {
                    // server returned a non-2xx status
                    showToast((json && json.message) ? json.message : 'Failed to add product to cart', 'error');
                    return;
                }

                if (json.success) {
                    updateCartCount(json.cart_count);
                    showToast(json.message || 'Product added to cart successfully!', 'success');
                    document.dispatchEvent(new CustomEvent('cartUpdated', {
                        detail: { productId: productId, quantity: quantity, cartCount: json.cart_count }
                    }));

                    
                    // Helper: open the cart offcanvas and refresh its contents from the server
                    function refreshCartSidebarAndOpen() {
                        try {
                            // Try to open Bootstrap offcanvas if available (support multiple IDs)
                            const cartSidebar = document.getElementById('modalShoppingCart') || document.getElementById('modalSidebar') || document.getElementById('modalShoppingCart');
                            if (cartSidebar) {
                                if (typeof bootstrap !== 'undefined' && bootstrap.Offcanvas) {
                                    try { new bootstrap.Offcanvas(cartSidebar).show(); } catch (e) { /* ignore */ }
                                } else {
                                    // Fallback: add a visible class
                                    cartSidebar.classList && cartSidebar.classList.add('show');
                                }

                                // Update offcanvas header count if present
                                try {
                                    const headerStrong = cartSidebar.querySelector('.offcanvas-header strong') || cartSidebar.querySelector('.offcanvas-header .mx-auto');
                                    if (headerStrong) {
                                        // will update after fetching items
                                    }
                                } catch (e) {}
                            }
                        } catch (e) {
                            console.error('Error showing cart sidebar:', e);
                        }

                        // Refresh cart items in the sidebar by calling the server endpoint
                        try {
                            fetch('/get-cart-items/', {
                                method: 'GET',
                                headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' },
                                credentials: 'same-origin'
                            })
                            .then(r => r.ok ? r.json() : null)
                            .then(data => {
                                if (!data) return;

                                // Normalize shapes: server returns { items, count } while some code expects cart_items/cart_count
                                const items = data.items || data.cart_items || data.cartItems || data.cart_items_list || [];
                                const count = data.count || data.cart_count || data.cartCount || (Array.isArray(items) ? items.reduce((s,i)=> s + (i.quantity||i.qty||0), 0) : 0);
                                const total = data.total || data.cart_total || data.cartTotal || undefined;

                                // Update readers
                                try { updateAllCartReaders(count, total); } catch (e) {}

                                // Update sidebar header count if possible
                                try {
                                    const cartSidebar = document.getElementById('modalShoppingCart') || document.getElementById('modalSidebar');
                                    if (cartSidebar) {
                                        const headerStrong = cartSidebar.querySelector('.offcanvas-header strong') || cartSidebar.querySelector('.offcanvas-header .mx-auto');
                                        if (headerStrong) {
                                            headerStrong.textContent = `Your Cart (${count})`;
                                        }
                                    }
                                } catch (e) {}

                                // Find list container
                                const cartItemsList = document.getElementById('cartItemsList') || document.getElementById('cart-items') || document.getElementById('cart-items-list') || document.querySelector('#modalShoppingCart .list-group') || document.querySelector('#modalSidebar .list-group');
                                if (!cartItemsList) return;

                                // Render items
                                if (!Array.isArray(items) || items.length === 0) {
                                    cartItemsList.innerHTML = `\n                                        <div class="px-4 py-6 text-center">\n                                            <h6 class="mb-2">Your cart is empty 😞</h6>\n                                            <p class="text-muted">Add products to your cart and they will appear here.</p>\n                                        </div>`;
                                    return;
                                }

                                // Build HTML for each item
                                const fragment = document.createDocumentFragment();
                                items.forEach(item => {
                                    try {
                                        const li = document.createElement('li');
                                        li.className = 'list-group-item p-4 cart-item';
                                        const cid = item.cart_item_id || item.id || item.cartItemId || '';
                                        li.id = `cart-item-${cid}`;

                                        const productUrl = item.url || item.product_url || item.productUrl || ('/product/' + (item.product_id || item.product || ''));
                                        const img = item.image_url || item.image || item.product_image || '/static/img/placeholder.png';
                                        const name = item.name || item.product_name || item.title || '';
                                        const unitPrice = (typeof item.unit_price !== 'undefined') ? item.unit_price : (item.price || item.unitPrice || 0);
                                        const quantity = item.quantity || item.qty || 1;
                                        const totalPrice = (typeof item.total_price !== 'undefined') ? item.total_price : (item.total || unitPrice * quantity || 0);

                                        li.innerHTML = `
                                            <div class="row align-items-center">
                                                <div class="col-4 col-md-3 col-xl-2">
                                                    <a href="${productUrl}"><img src="${img}" class="img-fluid rounded shadow-sm" /></a>
                                                </div>
                                                <div class="col">
                                                    <p class="mb-2 fs-md fw-bold"><a class="text-body" href="${productUrl}">${escapeHtml(name)}</a> <br><span class="text-muted">$${Number(unitPrice).toFixed(2)} x ${quantity}</span></p>
                                                    <div class="d-flex">
                                                        <span class="fs-sm fw-bold ms-auto">$${Number(totalPrice).toFixed(2)}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        `;

                                        fragment.appendChild(li);
                                    } catch (e) {
                                        console.error('Error rendering cart item in sidebar:', e);
                                    }
                                });

                                // Replace contents
                                cartItemsList.innerHTML = '';
                                cartItemsList.appendChild(fragment);
                            })
                            .catch(err => console.error('Error refreshing cart items:', err));
                        } catch (e) {
                            console.error('Error initiating refreshCartSidebarAndOpen:', e);
                        }
                    }

                    // small utility to escape HTML in names
                    function escapeHtml(str) {
                        if (!str) return '';
                        return String(str).replace(/[&<>\"']/g, function(s) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[s]; });
                    }

                    // Refresh cart sidebar to show latest items
                    refreshCartSidebarAndOpen();
                } else {
                    showToast(json.message || 'Failed to add product to cart', 'error');
                }
            } catch (err) {
                isAddingToCart = false;
                console.error('Error adding to cart (fetch):', err);
                showToast('An error occurred. Please try again.', 'error');
            }
        })();

        // Ensure global helper names call the direct implementation (prevents other scripts from opening modals)
        try {
            window.addToCartWithEmail = function(pid, qty) { try { addToCart(pid, qty || 1); } catch(e){ console.error(e); } };
            window.add_to_cart = window.addToCartWithEmail;
        } catch(e) {
            // ignore
        }
    }); // close checkStockAvailability.then
} // close addToCart function

/**
 * Add to cart animation
 * @param {number} productId - The ID of the product
 */
function addToCartAnimation(productId) {
    const productCard = document.querySelector(`[data-product-id="${productId}"]`);
    if (!productCard) return;

    const cartIcon = document.querySelector('.cart-button-count');
    if (!cartIcon) return;

    // Get product image
    const imgElement = productCard.querySelector('img') || document.querySelector(`#modalProduct${productId} img`);
    if (!imgElement) return;

    const imgRect = imgElement.getBoundingClientRect();
    const cartRect = cartIcon.getBoundingClientRect();

    // Create flying element
    const flyingImg = document.createElement('div');
    flyingImg.className = 'flying-cart-item';
    flyingImg.style.backgroundImage = `url(${imgElement.src})`;
    flyingImg.style.width = '50px';
    flyingImg.style.height = '50px';
    flyingImg.style.position = 'fixed';
    flyingImg.style.top = `${imgRect.top}px`;
    flyingImg.style.left = `${imgRect.left}px`;
    flyingImg.style.borderRadius = '50%';
    flyingImg.style.backgroundSize = 'cover';
    flyingImg.style.backgroundPosition = 'center';
    flyingImg.style.zIndex = '9999';
    flyingImg.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
    flyingImg.style.transition = 'all 0.8s cubic-bezier(0.18, 0.89, 0.32, 1.28)';

    // Add to body
    document.body.appendChild(flyingImg);

    // Animate
    setTimeout(() => {
        flyingImg.style.top = `${cartRect.top}px`;
        flyingImg.style.left = `${cartRect.left}px`;
        flyingImg.style.width = '20px';
        flyingImg.style.height = '20px';
        flyingImg.style.opacity = '0';

        // Shake cart icon
        cartIcon.style.animation = 'shake 0.5s ease-in-out';

        // Remove flying element after animation
        setTimeout(() => {
            document.body.removeChild(flyingImg);
            cartIcon.style.animation = '';
        }, 800);
    }, 10);
}

/**
 * Update cart count
 * @param {number} count - The new cart count
 */
function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart-button-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
        cartCountElement.classList.add('cart-count-updated');
        setTimeout(() => {
            cartCountElement.classList.remove('cart-count-updated');
        }, 1000);
    }
    updateAllCartReaders(count);
}

// Update all cart reader UI elements asynchronously when cart changes
function updateAllCartReaders(count, total) {
    // Normalize
    const cnt = Number(count) || 0;

    // Update common cart count targets
    const selectors = [
        '#cart-button-count',
        '#navbar-cart-count',
        '.cart-counter',
        '.cart-reader',
        '[data-cart-count]'
    ];

    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
            // prefer textContent, but allow inputs
            if ('value' in el) {
                el.value = cnt;
            } else {
                el.textContent = cnt;
            }
            el.classList && el.classList.add('cart-count-updated');
            setTimeout(() => el.classList && el.classList.remove('cart-count-updated'), 1000);
        });
    });

    // Update any elements showing cart total
    if (typeof total !== 'undefined') {
        document.querySelectorAll('[data-cart-total]').forEach(el => {
            const t = Number(total) || 0;
            el.textContent = `$${t.toFixed(2)}`;
            el.classList && el.classList.add('price-updated');
            setTimeout(() => el.classList && el.classList.remove('price-updated'), 800);
        });
    }
}

// Listen for cartUpdated events to refresh readers (use capture for early handling)
document.addEventListener('cartUpdated', function(e) {
    try {
        const detail = (e && e.detail) || {};
        updateAllCartReaders(detail.cartCount || detail.cart_count || 0, detail.cartTotal || detail.cart_total || detail.cartTotal);
    } catch (err) {
        console.error('Error updating cart readers:', err);
    }
}, true);

/**
 * Increase cart item quantity
 * @param {number} itemId - The cart item ID
 */
function increaseCartQuantity(itemId) {
    // Show loading state
    const quantityElement = document.getElementById(`quantity-${itemId}`);
    if (quantityElement) {
        quantityElement.classList.add('quantity-updating');
    }

    // Make AJAX request
    $.ajax({
        url: `/increase_quantity/${itemId}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            // Remove loading state
            if (quantityElement) {
                quantityElement.classList.remove('quantity-updating');
            }

            if (response.success) {
                // Update quantity display
                if (quantityElement) {
                    quantityElement.textContent = response.new_quantity;

                    // Add animation
                    quantityElement.classList.add('quantity-changed');
                    setTimeout(() => {
                        quantityElement.classList.remove('quantity-changed');
                    }, 500);
                }

                // Update item total price
                const totalElement = document.getElementById(`total-${itemId}`);
                if (totalElement) {
                    totalElement.textContent = `$${response.new_total_price.toFixed(2)}`;
                    totalElement.classList.add('price-updated');
                    setTimeout(() => {
                        totalElement.classList.remove('price-updated');
                    }, 500);
                }

                // Update cart summary
                updateCartSummary(response.subtotal, response.vat, response.total);
            } else {
                // Show error toast
                showToast(response.message || 'Failed to increase quantity', 'error');
            }
        },
        error: function() {
            // Remove loading state
            if (quantityElement) {
                quantityElement.classList.remove('quantity-updating');
            }

            // Show error toast
            showToast('Failed to increase quantity. Please try again.', 'error');
        }
    });
}

/**
 * Decrease cart item quantity
 * @param {number} itemId - The cart item ID
 */
function decreaseCartQuantity(itemId) {
    // Get current quantity
    const quantityElement = document.getElementById(`quantity-${itemId}`);
    if (!quantityElement) return;

    const currentQuantity = parseInt(quantityElement.textContent);
    if (currentQuantity <= 1) {
        // Show warning toast
        showToast('Quantity cannot be less than 1', 'info');
        return;
    }

    // Show loading state
    quantityElement.classList.add('quantity-updating');

    // Make AJAX request
    $.ajax({
        url: `/decrease_quantity/${itemId}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            // Remove loading state
            quantityElement.classList.remove('quantity-updating');

            if (response.success) {
                // Update quantity display
                quantityElement.textContent = response.new_quantity;

                // Add animation
                quantityElement.classList.add('quantity-changed');
                setTimeout(() => {
                    quantityElement.classList.remove('quantity-changed');
                }, 500);

                // Update item total price
                const totalElement = document.getElementById(`total-${itemId}`);
                if (totalElement) {
                    totalElement.textContent = `$${response.new_total_price.toFixed(2)}`;
                    totalElement.classList.add('price-updated');
                    setTimeout(() => {
                        totalElement.classList.remove('price-updated');
                    }, 500);
                }

                // Update cart summary
                updateCartSummary(response.subtotal, response.vat, response.total);
            } else {
                // Show error toast
                showToast(response.message || 'Failed to decrease quantity', 'error');
            }
        },
        error: function() {
            // Remove loading state
            quantityElement.classList.remove('quantity-updating');

            // Show error toast
            showToast('Failed to decrease quantity. Please try again.', 'error');
        }
    });
}

/**
 * Update cart summary
 * @param {number} subtotal - The cart subtotal
 * @param {number} vat - The VAT amount
 * @param {number} total - The total amount
 */
function updateCartSummary(subtotal, vat, total) {
    // Update subtotal
    const subtotalElement = document.getElementById('cart-subtotal');
    if (subtotalElement) {
        subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
        subtotalElement.classList.add('price-updated');
        setTimeout(() => {
            subtotalElement.classList.remove('price-updated');
        }, 500);
    }

    // Update VAT
    const vatElement = document.getElementById('cart-vat');
    if (vatElement) {
        vatElement.textContent = `$${vat.toFixed(2)}`;
        vatElement.classList.add('price-updated');
        setTimeout(() => {
            vatElement.classList.remove('price-updated');
        }, 500);
    }

    // Update total
    const totalElement = document.getElementById('cart-total');
    if (totalElement) {
        totalElement.textContent = `$${total.toFixed(2)}`;
        totalElement.classList.add('price-updated');
        setTimeout(() => {
            totalElement.classList.remove('price-updated');
        }, 500);
    }
}

/**
 * Show toast notification
 * @param {string} message - The message to show
 * @param {string} type - The type of toast (success, error, info, loading)
 */
function showToast(message, type) {
    if (type === 'loading') {
        // Avoid multiple add-to-cart notifications (skip loading toast)
        return;
    }
    if (window.toast && typeof window.toast[type] === 'function') {
        const titleMap = { success: 'Success', error: 'Error', info: 'Info' };
        window.toast[type](message, { title: titleMap[type] || 'Notification' });
        return;
    }
    // Check if Toastify is available
    if (typeof Toastify === 'function') {
        Toastify({
            text: message,
            duration: type === 'error' ? 5000 : 3000,
            close: true,
            gravity: 'top',
            position: 'right',
            backgroundColor: getToastColor(type),
            stopOnFocus: true
        }).showToast();
    } else {
        // Fallback to alert
        if (type === 'error') {
            alert(`Error: ${message}`);
        } else if (type !== 'loading') {
            alert(message);
        }
    }
}

/**
 * Get toast color based on type
 * @param {string} type - The type of toast
 * @returns {string} - The color
 */
function getToastColor(type) {
    switch (type) {
        case 'success':
            return '#28a745';
        case 'error':
            return '#dc3545';
        case 'info':
            return '#17a2b8';
        case 'loading':
            return '#6c757d';
        default:
            return '#343a40';
    }
}

/**
 * Validate email
 * @param {string} email - The email to validate
 * @returns {boolean} - Whether the email is valid
 */
function isValidEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

// Helper to read CSRF token from cookies (used when a CSRF input isn't on the page)
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Ensure globals point to safe functions as last resort
try {
    window.addToCartWithEmail = function(pid, qty) { try { addToCart(pid, qty || 1); } catch(e){ console.error(e); } };
    window.add_to_cart = function(pid, qty) { try { addToCart(pid, qty || 1); } catch(e){ console.error(e); } };
} catch (e) {}

// Ensure wishlist calls don't rely on removed email modal scripts
try {
    if (typeof window.addToWishlistWithEmail !== 'function') {
        window.addToWishlistWithEmail = function(pid) {
            try {
                if (typeof addToWishlist === 'function') {
                    addToWishlist(pid);
                    return;
                }
            } catch (e) {
                console.error('addToWishlist error:', e);
            }
            // Fallback to login page if wishlist handler isn't available
            const next = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.href = `/accounts/login/?next=${next}`;
        };
    }
} catch (e) {
    // ignore
}

// Initialize on document ready
$(document).ready(function() {
    // Add animation keyframes if not already added
    if (!document.getElementById('cart-animation-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'cart-animation-styles';
        styleElement.textContent = `
            @keyframes shake {
                0% { transform: rotate(0deg); }
                25% { transform: rotate(10deg); }
                50% { transform: rotate(0deg); }
                75% { transform: rotate(-10deg); }
                100% { transform: rotate(0deg); }
            }

            .cart-count-updated {
                animation: pulse 0.5s ease;
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.2); }
                100% { transform: scale(1); }
            }

            .quantity-changed {
                animation: quantityPulse 0.5s ease;
                background-color: rgba(0, 135, 81, 0.1);
            }

            @keyframes quantityPulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }

            .quantity-updating {
                opacity: 0.7;
                position: relative;
            }

            .quantity-updating::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 10px;
                height: 10px;
                margin-top: -5px;
                margin-left: -5px;
                border-radius: 50%;
                border: 2px solid rgba(0, 135, 81, 0.5);
                border-top-color: #008751;
                animation: spin 0.8s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .price-updated {
                animation: priceUpdate 0.5s ease;
                color: #008751;
            }

            @keyframes priceUpdate {
                0% { opacity: 0.5; }
                50% { opacity: 1; }
                100% { opacity: 0.5; }
            }
        `;
        document.head.appendChild(styleElement);
    }

    // Attach event handlers to quantity buttons in cart
    $('.btn-quantity-increase').on('click', function() {
        const itemId = $(this).data('item-id');
        if (itemId) {
            increaseCartQuantity(itemId);
        }
    });

    $('.btn-quantity-decrease').on('click', function() {
        const itemId = $(this).data('item-id');
        if (itemId) {
            decreaseCartQuantity(itemId);
        }
    });
});
