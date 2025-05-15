/**
 * Main JavaScript file for African Food San Diego
 * This file contains all the custom JavaScript functionality for the site
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all Flickity sliders
    initSliders();

    // Initialize lazy loading
    initLazyLoading();

    // Initialize smooth scrolling
    initSmoothScroll();

    // Initialize mobile menu
    initMobileMenu();
});

/**
 * Initialize all Flickity sliders
 */
function initSliders() {
    // Hero slider
    const heroSlider = document.querySelector('.hero-slider');
    if (heroSlider) {
        new Flickity(heroSlider, {
            pageDots: true,
            prevNextButtons: true,
            wrapAround: true,
            autoPlay: 5000,
            fade: true
        });
    }

    // Testimonial slider
    const testimonialSlider = document.querySelector('.testimonial-slider');
    if (testimonialSlider) {
        new Flickity(testimonialSlider, {
            pageDots: true,
            prevNextButtons: true,
            wrapAround: true,
            autoPlay: 4000,
            cellAlign: 'center',
            contain: true
        });
    }
}

/**
 * Initialize lazy loading for images
 */
function initLazyLoading() {
    const lazyImages = document.querySelectorAll('img.lazyload');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazyload');
                    observer.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazyload');
        });
    }
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            if (href !== '#') {
                e.preventDefault();

                const targetElement = document.querySelector(href);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
}

/**
 * Initialize mobile menu functionality with enhanced UX
 */
function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.navbar-toggler');
    const mobileMenu = document.querySelector('.navbar-collapse');
    const navbarDropdowns = document.querySelectorAll('.navbar-nav .dropdown');

    if (mobileMenuToggle && mobileMenu) {
        // Toggle mobile menu and body class
        mobileMenuToggle.addEventListener('click', function() {
            document.body.classList.toggle('mobile-menu-open');

            // Add animation class when opening
            if (mobileMenu.classList.contains('show')) {
                mobileMenu.classList.add('menu-animating');
                setTimeout(() => {
                    mobileMenu.classList.remove('menu-animating');
                }, 300);
            }
        });

        // Handle mobile dropdowns with slide animation
        navbarDropdowns.forEach(dropdown => {
            const dropdownToggle = dropdown.querySelector('.dropdown-toggle');
            const dropdownMenu = dropdown.querySelector('.dropdown-menu');

            // For mobile view, prevent default Bootstrap dropdown behavior
            if (window.innerWidth < 992) {
                dropdownToggle.addEventListener('click', function(e) {
                    if (window.innerWidth < 992) {
                        e.preventDefault();
                        e.stopPropagation();

                        // Toggle custom active class
                        dropdown.classList.toggle('dropdown-active');

                        // Animate height
                        if (dropdown.classList.contains('dropdown-active')) {
                            dropdownMenu.style.maxHeight = dropdownMenu.scrollHeight + 'px';
                        } else {
                            dropdownMenu.style.maxHeight = '0';
                        }
                    }
                });
            }
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (mobileMenu.classList.contains('show') &&
                !mobileMenu.contains(e.target) &&
                !mobileMenuToggle.contains(e.target)) {

                // Use Bootstrap's collapse API to hide the menu
                const bsCollapse = bootstrap.Collapse.getInstance(mobileMenu);
                if (bsCollapse) {
                    bsCollapse.hide();
                    document.body.classList.remove('mobile-menu-open');
                }
            }
        });

        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 992) {
                // Reset mobile-specific styles on larger screens
                navbarDropdowns.forEach(dropdown => {
                    dropdown.classList.remove('dropdown-active');
                    const dropdownMenu = dropdown.querySelector('.dropdown-menu');
                    if (dropdownMenu) {
                        dropdownMenu.style.maxHeight = '';
                    }
                });

                // Remove mobile menu open class
                document.body.classList.remove('mobile-menu-open');
            }
        });
    }
}

/**
 * Update cart count with animation
 * This function updates the cart count in the navbar with a nice animation
 */
function updateCartCountWithAnimation(count) {
    // Find all cart count elements
    const cartCountElements = document.querySelectorAll('.cart-counter');

    if (cartCountElements.length === 0) {
        console.warn('Cart count elements not found');
        return;
    }

    // Update each cart count element with animation
    cartCountElements.forEach(element => {
        // Add animation class
        element.classList.add('cart-count-updated');

        // Update the count
        element.textContent = count;

        // Remove animation class after animation completes
        setTimeout(() => {
            element.classList.remove('cart-count-updated');
        }, 500);
    });

    // Store the cart count in localStorage for persistence
    localStorage.setItem('cartCount', count);
}

/**
 * Enhanced Add to Cart with Modern Animation and Feedback
 * This function handles both the animation and the actual cart addition
 * with improved UX and error handling
 */
function addToCartWithAnimation(productId, quantity = 1) {
    // Prevent double clicks with improved feedback
    if (window.isAddingToCart) {
        toast.info('Please wait while we process your request...', {
            title: 'Processing',
            duration: 2000
        });
        return;
    }

    // Set a flag to prevent multiple clicks
    window.isAddingToCart = true;
    setTimeout(() => { window.isAddingToCart = false; }, 2000); // Reset after 2 seconds

    // Get quantity from input if available with better validation
    const quantityInput = document.getElementById(`quantity-${productId}`);
    if (quantityInput) {
        const parsedQuantity = parseInt(quantityInput.value);
        if (!isNaN(parsedQuantity) && parsedQuantity > 0) {
            quantity = parsedQuantity;
        }
    }

    // Get the product element with improved selector strategy
    let productElement = document.querySelector(`.product-card-nigerian[data-product-id="${productId}"]`);

    // Try alternative selectors if the first one fails
    if (!productElement) {
        productElement = document.querySelector(`[data-product-id="${productId}"]`);
    }

    if (!productElement) {
        productElement = document.getElementById(`product-${productId}`);
    }

    if (!productElement) {
        // If we still can't find the product element, try to get details from the modal
        const modalProduct = document.querySelector(`#modalProduct${productId}`);
        if (modalProduct) {
            productElement = modalProduct;
        } else {
            console.error('Product element not found');
            window.isAddingToCart = false;

            // Show user-friendly error
            toast.error('Could not identify the product. Please try again or refresh the page.', {
                title: 'Error Adding to Cart'
            });
            return;
        }
    }

    // Get the cart icon with improved selector strategy
    let cartIcon;

    // Try multiple selectors to find the cart icon
    const cartIconSelectors = [
        '.navbar-cart-icon', // Custom class if added
        '.d-lg-none .fa-shopping-cart, .d-lg-none .fe-shopping-cart', // Mobile
        '.d-none.d-lg-flex .fa-shopping-cart, .d-none.d-lg-flex .fe-shopping-cart', // Desktop
        '.navbar .fa-shopping-cart, .navbar .fe-shopping-cart', // General
        '[class*="fa-shopping-cart"], [class*="fe-shopping-cart"]' // Any cart icon
    ];

    // Try each selector until we find a cart icon
    for (const selector of cartIconSelectors) {
        cartIcon = document.querySelector(selector);
        if (cartIcon) break;
    }

    if (!cartIcon) {
        console.error('Cart icon not found');
        window.isAddingToCart = false;

        // Make AJAX call anyway, but without animation
        addToCartWithoutAnimation(productId, quantity);
        return;
    }

    // Get product details for the toast notification with improved selectors
    let productName = '';
    let productPrice = '';
    let productImage = '';

    // Try multiple selectors for product name
    const nameSelectors = [
        '.product-title a',
        '.product-title',
        '.product-name',
        '.toast-product-name',
        'h1.product-name',
        '.product-modal-title'
    ];

    // Try each selector until we find the product name
    for (const selector of nameSelectors) {
        const element = productElement.querySelector(selector);
        if (element) {
            productName = element.textContent.trim();
            break;
        }
    }

    // If we still don't have a name, try document-level selectors
    if (!productName) {
        for (const selector of nameSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                productName = element.textContent.trim();
                break;
            }
        }
    }

    // Default name if all else fails
    if (!productName) {
        productName = 'Product';
    }

    // Try multiple selectors for product price
    const priceSelectors = [
        '.price-current',
        '.price-amount',
        '.product-price .price',
        '.product-price',
        '.price'
    ];

    // Try each selector until we find the product price
    for (const selector of priceSelectors) {
        const element = productElement.querySelector(selector);
        if (element) {
            productPrice = element.textContent.trim();
            break;
        }
    }

    // If we still don't have a price, try document-level selectors
    if (!productPrice) {
        for (const selector of priceSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                productPrice = element.textContent.trim();
                break;
            }
        }
    }

    // Default price if all else fails
    if (!productPrice) {
        productPrice = '$0.00';
    }

    // Try multiple selectors for product image
    const imageSelectors = [
        '.product-img',
        'img',
        '.product-image',
        '.product-modal-image'
    ];

    // Try each selector until we find the product image
    let productImg;
    for (const selector of imageSelectors) {
        productImg = productElement.querySelector(selector);
        if (productImg) {
            productImage = productImg.src;
            break;
        }
    }

    // If we still don't have an image, try document-level selectors
    if (!productImage) {
        for (const selector of imageSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                productImage = element.src;
                break;
            }
        }
    }

    // Default image if all else fails
    if (!productImage) {
        productImage = '/static/img/placeholder.png';
        productImg = { src: productImage };
    }

    // Show enhanced loading animation
    const loadingToast = toast.loading('Adding to cart...');

    // Create a flying element with enhanced styling
    const flyingElement = document.createElement('div');
    flyingElement.className = 'flying-item';

    // Add a subtle shadow and border
    flyingElement.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
    flyingElement.style.border = '2px solid #008751';

    // Set the flying element's position and style with improved positioning
    flyingElement.style.backgroundImage = `url(${productImg.src})`;

    // Get the center of the product element for better animation starting point
    const productRect = productElement.getBoundingClientRect();
    const startX = productRect.left + (productRect.width / 2) - 25; // Center X - half of flying item width
    const startY = productRect.top + (productRect.height / 2) - 25; // Center Y - half of flying item height

    flyingElement.style.left = `${startX}px`;
    flyingElement.style.top = `${startY}px`;

    // Add the flying element to the body
    document.body.appendChild(flyingElement);

    // Animate the flying element with enhanced path
    requestAnimationFrame(() => {
        // Get the cart icon position for animation end point
        const cartRect = cartIcon.getBoundingClientRect();
        const endX = cartRect.left + (cartRect.width / 2) - 15; // Center X of cart icon
        const endY = cartRect.top + (cartRect.height / 2) - 15; // Center Y of cart icon

        // Set a curved path for more natural animation
        // We'll use CSS custom properties for this
        flyingElement.style.setProperty('--start-x', `${startX}px`);
        flyingElement.style.setProperty('--start-y', `${startY}px`);
        flyingElement.style.setProperty('--end-x', `${endX}px`);
        flyingElement.style.setProperty('--end-y', `${endY}px`);

        // Add a class for the curved animation
        flyingElement.classList.add('flying-animation');

        // Set final position
        flyingElement.style.left = `${endX}px`;
        flyingElement.style.top = `${endY}px`;
        flyingElement.style.opacity = '0';
        flyingElement.style.transform = 'scale(0.3) rotate(360deg)';

        // Remove the flying element after animation and make AJAX call
        setTimeout(() => {
            if (document.body.contains(flyingElement)) {
                document.body.removeChild(flyingElement);
            }

            // Add enhanced bounce animation to cart icon
            cartIcon.parentElement.classList.add('cart-bounce');
            setTimeout(() => {
                cartIcon.parentElement.classList.remove('cart-bounce');
            }, 500);

            // Make the actual AJAX call to add to cart with improved error handling
            $.ajax({
                url: `/add_to_cart/${productId}/`,
                type: "POST",
                data: {
                    'quantity': quantity,
                    'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                success: function(response) {
                    // Close loading toast
                    toast.close(loadingToast);
                    window.isAddingToCart = false;

                    if (response.success) {
                        // Update cart count in navbar with enhanced animation
                        updateCartCountWithAnimation(response.cart_count);

                        // Show enhanced success toast with product details and clickable link
                        toast.cart({
                            name: productName,
                            image: productImage,
                            price: productPrice,
                            link: '/cart/' // Make the toast clickable to go to cart
                        }, response.message || 'Product added to cart successfully!');

                        // Trigger a custom event that other components can listen for
                        document.dispatchEvent(new CustomEvent('cartUpdated', {
                            detail: {
                                productId: productId,
                                quantity: quantity,
                                cartCount: response.cart_count
                            }
                        }));
                    } else {
                        // Show enhanced error toast with more helpful message
                        let errorMessage = response.message || 'Failed to add product to cart';

                        // Check for common error patterns and provide more helpful messages
                        if (errorMessage.includes('login') || errorMessage.includes('authentication')) {
                            toast.loginRequired(errorMessage);
                        } else {
                            toast.cartError(errorMessage, {
                                title: 'Error Adding to Cart',
                                retryCallback: () => addToCartWithAnimation(productId, quantity)
                            });
                        }
                    }
                },
                error: function(xhr) {
                    // Close loading toast
                    toast.close(loadingToast);
                    window.isAddingToCart = false;

                    // Try to parse the error response
                    let errorMessage = 'Failed to add product to cart. Please try again.';
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.message) {
                            errorMessage = response.message;
                        }
                    } catch (e) {
                        // If parsing fails, use the default message
                        console.error('Error parsing response:', e);
                    }

                    // Show enhanced error toast
                    toast.cartError(errorMessage, {
                        title: 'Error Adding to Cart',
                        retryCallback: () => addToCartWithAnimation(productId, quantity)
                    });
                }
            });
        }, 800); // Slightly longer animation for better visual effect
    });
}

/**
 * Fallback function to add to cart without animation
 * Used when we can't find the necessary elements for animation
 */
function addToCartWithoutAnimation(productId, quantity = 1) {
    // Show loading toast
    const loadingToast = toast.loading('Adding to cart...');

    // Make AJAX call directly
    $.ajax({
        url: `/add_to_cart/${productId}/`,
        type: "POST",
        data: {
            'quantity': quantity,
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            toast.close(loadingToast);
            window.isAddingToCart = false;

            if (response.success) {
                // Update cart count
                updateCartCountWithAnimation(response.cart_count);

                // Show success message
                toast.success(response.message || 'Product added to cart successfully!', {
                    title: 'Added to Cart',
                    actions: [
                        {
                            id: 'view-cart',
                            text: 'View Cart',
                            class: 'toast-btn-primary',
                            callback: () => {
                                window.location.href = '/cart/';
                            }
                        }
                    ]
                });
            } else {
                // Show error message
                toast.error(response.message || 'Failed to add product to cart', {
                    title: 'Error Adding to Cart'
                });
            }
        },
        error: function() {
            toast.close(loadingToast);
            window.isAddingToCart = false;

            toast.error('Failed to add product to cart. Please try again.', {
                title: 'Error Adding to Cart'
            });
        }
    });
}

/**
 * Enhanced function to update cart count with animation
 */
function updateCartCountWithAnimation(newCount) {
    // Get all cart counters
    const cartCounters = document.querySelectorAll('.cart-counter');

    cartCounters.forEach(counter => {
        // Get current count for animation effect
        const currentCount = parseInt(counter.textContent.trim()) || 0;
        const isIncreasing = newCount > currentCount;

        // Add appropriate animation class
        if (isIncreasing) {
            counter.classList.add('cart-counter-increase');
        } else if (newCount < currentCount) {
            counter.classList.add('cart-counter-decrease');
        }

        // Update the count after a small delay for better animation
        setTimeout(() => {
            counter.textContent = newCount;

            // Remove animation classes after animation completes
            setTimeout(() => {
                counter.classList.remove('cart-counter-increase', 'cart-counter-decrease');
            }, 500);
        }, 100);
    });

    // Also update any other elements that might show cart count
    const cartButtonCount = document.getElementById('cart-button-count');
    if (cartButtonCount) {
        cartButtonCount.textContent = newCount;
    }
}

/**
 * Update cart count in the navbar with animation
 */
function updateCartCount(increment = 1) {
    // Get all cart counters
    const cartCounters = document.querySelectorAll('.cart-counter');

    cartCounters.forEach(counter => {
        // Update the count
        let count = parseInt(counter.textContent.trim()) || 0;
        count += increment;
        counter.textContent = count;

        // Add animation class
        counter.classList.add('cart-counter-animate');

        // Remove animation class after animation completes
        setTimeout(() => {
            counter.classList.remove('cart-counter-animate');
        }, 500);
    });

    // Also update any other elements that might show cart count
    const cartButtonCount = document.getElementById('cart-button-count');
    if (cartButtonCount) {
        let count = parseInt(cartButtonCount.textContent.trim()) || 0;
        count += increment;
        cartButtonCount.textContent = count;
    }
}

/**
 * Add to wishlist with animation and feedback
 */
function addToWishlist(productId) {
    // Check if user is logged in
    const isLoggedIn = document.body.classList.contains('user-logged-in');

    if (!isLoggedIn) {
        // Show login required toast
        toast.info('Please log in to add items to your wishlist', {
            title: 'Login Required',
            actions: [
                {
                    id: 'login',
                    text: 'Login',
                    class: 'toast-btn-primary',
                    callback: () => {
                        window.location.href = '/login/?next=' + window.location.pathname;
                    }
                },
                {
                    id: 'cancel',
                    text: 'Cancel',
                    callback: () => {}
                }
            ]
        });
        return;
    }

    // Show loading animation
    const loadingToast = toast.loading('Adding to wishlist...');

    // Get the heart icon and add pulse animation
    const heartIcon = document.querySelector(`.btn-add-to-wishlist[onclick*="${productId}"] i`);
    if (heartIcon) {
        heartIcon.classList.add('heart-pulse');
    }

    // Make AJAX request to add to wishlist
    $.ajax({
        url: '/add_to_wishlist/',
        type: 'POST',
        data: {
            'product_id': productId,
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            // Close loading toast
            toast.close(loadingToast);

            if (response.success) {
                // Show success toast
                toast.success(response.message || 'Product added to wishlist', {
                    title: 'Added to Wishlist',
                    actions: [
                        {
                            id: 'view-wishlist',
                            text: 'View Wishlist',
                            class: 'toast-btn-primary',
                            callback: () => {
                                window.location.href = '/account/wishlist/';
                            }
                        },
                        {
                            id: 'continue-shopping',
                            text: 'Continue Shopping',
                            callback: () => {}
                        }
                    ]
                });

                // Update heart icon to filled
                if (heartIcon) {
                    heartIcon.classList.remove('fa-heart-o', 'far', 'fa-heart');
                    heartIcon.classList.add('fas', 'fa-heart', 'text-danger');
                    heartIcon.classList.remove('heart-pulse');
                }
            } else {
                // Show error toast
                toast.error(response.message || 'Failed to add to wishlist', {
                    title: 'Error',
                    actions: [
                        {
                            id: 'try-again',
                            text: 'Try Again',
                            class: 'toast-btn-primary',
                            callback: () => addToWishlist(productId)
                        }
                    ]
                });

                // Remove animation from heart icon
                if (heartIcon) {
                    heartIcon.classList.remove('heart-pulse');
                }
            }
        },
        error: function() {
            // Close loading toast
            toast.close(loadingToast);

            // Show error toast
            toast.error('Failed to add to wishlist. Please try again.', {
                title: 'Error',
                actions: [
                    {
                        id: 'try-again',
                        text: 'Try Again',
                        class: 'toast-btn-primary',
                        callback: () => addToWishlist(productId)
                    }
                ]
            });

            // Remove animation from heart icon
            if (heartIcon) {
                heartIcon.classList.remove('heart-pulse');
            }
        }
    });
}

/**
 * Show a toast notification
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast show toast-${type}`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    // Set toast content
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${type === 'success' ? 'Success' : 'Notification'}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    // Add toast to container
    toastContainer.appendChild(toast);

    // Auto-remove toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 300);
    }, 3000);

    // Add click event to close button
    const closeButton = toast.querySelector('.btn-close');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => {
                toastContainer.removeChild(toast);
            }, 300);
        });
    }
}

// Add CSS for enhanced animations and modern UI elements
const style = document.createElement('style');
style.textContent = `
/* Enhanced Flying Item Animation */
.flying-item {
    position: fixed;
    width: 50px;
    height: 50px;
    background-size: cover;
    background-position: center;
    border-radius: 50%;
    z-index: 9999;
    transition: all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    will-change: transform, opacity, left, top;
    pointer-events: none;
}

/* Curved animation path using CSS custom properties */
.flying-animation {
    animation: flyToCart 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes flyToCart {
    0% {
        transform: scale(1) rotate(0deg);
        opacity: 1;
    }
    50% {
        transform: scale(1.2) rotate(180deg);
        opacity: 0.8;
    }
    100% {
        transform: scale(0.3) rotate(360deg);
        opacity: 0;
    }
}

/* Enhanced Cart Counter Animations */
.cart-counter {
    position: relative;
    transition: all 0.3s ease;
}

.cart-counter-animate {
    animation: counterPulse 0.5s ease;
}

.cart-counter-increase {
    animation: counterIncrease 0.5s ease;
}

.cart-counter-decrease {
    animation: counterDecrease 0.5s ease;
}

@keyframes counterPulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.5);
        color: #008751;
    }
}

@keyframes counterIncrease {
    0% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(1.5) translateY(-5px);
        color: #008751;
        opacity: 0.8;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

@keyframes counterDecrease {
    0% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(0.8) translateY(5px);
        color: #dc3545;
        opacity: 0.8;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

/* Enhanced Cart Bounce Animation */
@keyframes cartBounce {
    0%, 20%, 50%, 80%, 100% {
        transform: translateY(0);
    }
    40% {
        transform: translateY(-10px) scale(1.2);
        color: #008751;
    }
    60% {
        transform: translateY(-5px) scale(1.1);
        color: #008751;
    }
}

.cart-bounce {
    animation: cartBounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Mobile Menu Styles */
.mobile-menu-open {
    overflow: hidden;
}

/* Enhanced Mobile Menu Animations */
.navbar-collapse.menu-animating {
    animation: menuFadeIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes menuFadeIn {
    from {
        opacity: 0;
        transform: translateY(-15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Enhanced Mobile Dropdown Animations */
.navbar-nav .dropdown .dropdown-menu {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    margin: 0;
    padding: 0;
    opacity: 0;
}

.navbar-nav .dropdown.dropdown-active .dropdown-menu {
    padding: 0.75rem 0;
    opacity: 1;
    max-height: 500px; /* Large enough to accommodate any dropdown content */
}

/* Enhanced Dropdown Item Animation */
.navbar-nav .dropdown-menu .dropdown-item {
    transform: translateX(-10px);
    opacity: 0;
    transition: all 0.3s ease;
    transition-delay: calc(var(--item-index, 0) * 0.05s);
}

.navbar-nav .dropdown.dropdown-active .dropdown-menu .dropdown-item {
    transform: translateX(0);
    opacity: 1;
}

/* Heart Animation for Wishlist */
@keyframes heartPulse {
    0% {
        transform: scale(1);
        color: #dc3545;
    }
    50% {
        transform: scale(1.5);
        color: #ff0033;
    }
    100% {
        transform: scale(1);
        color: #dc3545;
    }
}

.heart-pulse {
    animation: heartPulse 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}

/* Modern Toast Notifications (Fallback for older browsers) */
.toast-container {
    z-index: 9999;
    position: fixed;
    top: 20px;
    right: 20px;
    max-width: 350px;
    width: 100%;
}

.toast {
    min-width: 280px;
    border: none;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    opacity: 0;
    transform: translateX(50px);
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    overflow: hidden;
    margin-bottom: 10px;
    backdrop-filter: blur(10px);
    background-color: rgba(255, 255, 255, 0.95);
}

.toast.show {
    opacity: 1;
    transform: translateX(0);
}

/* Toast Types with Modern Styling */
.toast-success {
    border-top: 3px solid #008751;
}

.toast-info {
    border-top: 3px solid #0dcaf0;
}

.toast-warning {
    border-top: 3px solid #ffc107;
}

.toast-error {
    border-top: 3px solid #dc3545;
}

/* Modern Toast Header */
.toast-header {
    background-color: transparent;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    padding: 12px 15px 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* Modern Toast Body */
.toast-body {
    padding: 15px;
    color: #444;
    font-size: 14px;
    line-height: 1.5;
}
`;
document.head.appendChild(style);
