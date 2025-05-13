/**
 * Lazy Loading Implementation for African Food San Diego
 * This script handles lazy loading of images and dynamic content loading
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize lazy loading for images
    initLazyLoading();
    
    // Initialize dynamic product loading if on shop page
    if (document.getElementById('product-list')) {
        initDynamicProductLoading();
    }
});

/**
 * Initialize lazy loading for images
 */
function initLazyLoading() {
    // Get all images with the 'lazyload' class
    const lazyImages = document.querySelectorAll('img.lazyload');
    
    // Create an intersection observer
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            // If the image is in the viewport
            if (entry.isIntersecting) {
                const img = entry.target;
                // Replace the src with the data-src
                img.src = img.dataset.src;
                // Remove the lazyload class
                img.classList.remove('lazyload');
                // Stop observing this image
                observer.unobserve(img);
            }
        });
    });
    
    // Observe each lazy image
    lazyImages.forEach(img => {
        imageObserver.observe(img);
    });
}

/**
 * Initialize dynamic product loading
 */
function initDynamicProductLoading() {
    // Variables for pagination
    let page = 1;
    const productsPerPage = 12;
    let loading = false;
    let allLoaded = false;
    
    // Get the product list container
    const productList = document.getElementById('product-list');
    
    // Create a loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'text-center py-4 loading-indicator';
    loadingIndicator.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    loadingIndicator.style.display = 'none';
    
    // Add the loading indicator after the product list
    productList.parentNode.insertBefore(loadingIndicator, productList.nextSibling);
    
    // Function to load more products
    function loadMoreProducts() {
        if (loading || allLoaded) return;
        
        loading = true;
        loadingIndicator.style.display = 'block';
        
        // Simulate AJAX request (replace with actual AJAX call to your backend)
        setTimeout(() => {
            // This is where you would make an AJAX call to fetch more products
            // For now, we'll just simulate it
            
            // Example AJAX call:
            /*
            fetch(`/api/products?page=${page}&limit=${productsPerPage}`)
                .then(response => response.json())
                .then(data => {
                    if (data.products.length === 0) {
                        allLoaded = true;
                    } else {
                        // Append products to the list
                        data.products.forEach(product => {
                            // Create product card and append to list
                        });
                        page++;
                    }
                    loading = false;
                    loadingIndicator.style.display = 'none';
                })
                .catch(error => {
                    console.error('Error loading products:', error);
                    loading = false;
                    loadingIndicator.style.display = 'none';
                });
            */
            
            // For demo purposes, let's simulate reaching the end after 3 pages
            if (page >= 3) {
                allLoaded = true;
                loadingIndicator.innerHTML = '<p class="text-muted">No more products to load</p>';
            } else {
                page++;
            }
            
            loading = false;
            loadingIndicator.style.display = allLoaded ? 'block' : 'none';
        }, 1000);
    }
    
    // Detect when user scrolls near the bottom of the page
    window.addEventListener('scroll', () => {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        
        // If user has scrolled to the bottom (with a 200px threshold)
        if (scrollTop + clientHeight >= scrollHeight - 200) {
            loadMoreProducts();
        }
    });
}

/**
 * Add to cart with animation
 */
function addToCartWithAnimation(productId, quantity = 1) {
    // Get the product element
    const productElement = document.querySelector(`.product-card-african[data-product-id="${productId}"]`);
    if (!productElement) return;
    
    // Get the cart icon position
    const cartIcon = document.querySelector('.navbar .fa-shopping-cart');
    if (!cartIcon) return;
    
    // Create a flying element
    const flyingElement = document.createElement('div');
    flyingElement.className = 'flying-item';
    
    // Get product image
    const productImg = productElement.querySelector('.product-img');
    
    // Set the flying element's position and style
    flyingElement.style.backgroundImage = `url(${productImg.src})`;
    flyingElement.style.left = `${productElement.getBoundingClientRect().left}px`;
    flyingElement.style.top = `${productElement.getBoundingClientRect().top}px`;
    
    // Add the flying element to the body
    document.body.appendChild(flyingElement);
    
    // Animate the flying element
    setTimeout(() => {
        flyingElement.style.left = `${cartIcon.getBoundingClientRect().left}px`;
        flyingElement.style.top = `${cartIcon.getBoundingClientRect().top}px`;
        flyingElement.style.opacity = '0';
        flyingElement.style.transform = 'scale(0.3)';
        
        // Remove the flying element after animation
        setTimeout(() => {
            document.body.removeChild(flyingElement);
            
            // Update cart count
            updateCartCount(1);
            
            // Call the original add_to_cart function
            add_to_cart(productId, quantity);
        }, 500);
    }, 10);
}

/**
 * Update cart count
 */
function updateCartCount(increment) {
    const cartCountElement = document.getElementById('navbar-cart-count');
    if (cartCountElement) {
        let currentCount = parseInt(cartCountElement.textContent) || 0;
        cartCountElement.textContent = currentCount + increment;
    }
}

// Add CSS for flying animation
const style = document.createElement('style');
style.textContent = `
.flying-item {
    position: fixed;
    width: 50px;
    height: 50px;
    background-size: cover;
    background-position: center;
    border-radius: 50%;
    z-index: 9999;
    transition: all 0.5s cubic-bezier(0.18, 0.89, 0.32, 1.28);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
`;
document.head.appendChild(style);
