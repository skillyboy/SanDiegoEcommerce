/**
 * Live Search Functionality
 *
 * This script provides real-time search functionality for products
 * without requiring a page reload.
 */

const LiveSearch = {
    // Configuration
    config: {
        searchInputSelector: '#searchInput',
        categorySelectSelector: '#modalSearchCategories',
        resultsContainerSelector: '#searchResults',
        searchEndpoint: '/api/search/',
        debounceTime: 300, // milliseconds
        minSearchLength: 2,
    },

    // State
    state: {
        lastSearchTerm: '',
        lastCategory: '',
        debounceTimer: null,
        isLoading: false,
    },

    // Initialize the live search functionality
    init: function() {
        // Cache DOM elements
        this.searchInput = document.querySelector(this.config.searchInputSelector);
        this.categorySelect = document.querySelector(this.config.categorySelectSelector);
        this.resultsContainer = document.querySelector(this.config.resultsContainerSelector);

        // If elements don't exist, exit
        if (!this.searchInput || !this.resultsContainer) {
            console.error('Live search elements not found');
            return;
        }

        // Bind events
        this.bindEvents();

        console.log('Live search initialized');
    },

    // Bind event listeners
    bindEvents: function() {
        // Search input event
        this.searchInput.addEventListener('input', this.handleSearchInput.bind(this));

        // Category select event
        if (this.categorySelect) {
            this.categorySelect.addEventListener('change', this.handleCategoryChange.bind(this));
        }

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.resultsContainer.contains(e.target) && e.target !== this.searchInput) {
                this.hideResults();
            }
        });
    },

    // Handle search input changes
    handleSearchInput: function(e) {
        const searchTerm = e.target.value.trim();

        // Clear previous timer
        clearTimeout(this.state.debounceTimer);

        // If search term is too short, clear results
        if (searchTerm.length < this.config.minSearchLength) {
            this.clearResults();
            return;
        }

        // Set a debounce timer to avoid too many requests
        this.state.debounceTimer = setTimeout(() => {
            // If search term hasn't changed, don't search again
            if (searchTerm === this.state.lastSearchTerm &&
                (!this.categorySelect || this.categorySelect.value === this.state.lastCategory)) {
                return;
            }

            // Update last search term
            this.state.lastSearchTerm = searchTerm;
            if (this.categorySelect) {
                this.state.lastCategory = this.categorySelect.value;
            }

            // Perform search
            this.performSearch(searchTerm);
        }, this.config.debounceTime);
    },

    // Handle category changes
    handleCategoryChange: function() {
        // If there's a search term, perform search with new category
        if (this.state.lastSearchTerm.length >= this.config.minSearchLength) {
            this.performSearch(this.state.lastSearchTerm);
        }
    },

    // Perform the search
    performSearch: function(searchTerm) {
        // Show loading indicator
        this.showLoading();

        // Build query parameters
        const params = new URLSearchParams();
        params.append('search', searchTerm);

        if (this.categorySelect && this.categorySelect.value !== 'All Categories') {
            params.append('category', this.categorySelect.value);
        }

        // Fetch search results
        fetch(`${this.config.searchEndpoint}?${params.toString()}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Search request failed');
                }
                return response.json();
            })
            .then(data => {
                this.displayResults(data.products);
            })
            .catch(error => {
                console.error('Search error:', error);
                this.displayError('An error occurred while searching. Please try again.');
            })
            .finally(() => {
                this.hideLoading();
            });
    },

    // Display search results
    displayResults: function(products) {
        // Clear previous results
        this.clearResults();

        // If no products found
        if (!products || products.length === 0) {
            this.displayNoResults();
            return;
        }

        // Create results HTML
        const resultsHTML = products.map(product => this.createProductCard(product)).join('');

        // Update results container
        this.resultsContainer.innerHTML = resultsHTML;

        // Show results container
        this.showResults();
    },

    // Create HTML for a product card
    createProductCard: function(product) {
        return `
            <div class="search-result-item">
                <div class="row align-items-center position-relative mb-3">
                    <div class="col-4 col-md-3">
                        <img class="img-fluid" src="${product.image_url}" alt="${product.name}">
                    </div>
                    <div class="col position-static">
                        <p class="mb-0 fw-bold">
                            <a class="stretched-link text-body" href="/product/${product.id}/">${product.name}</a> <br>
                            <span class="text-muted">$${product.price.toFixed(2)}</span>
                        </p>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col">
                        <button class="btn btn-sm btn-outline-success w-100"
                                onclick="event.preventDefault(); event.stopPropagation(); addToCartWithAnimation(${product.id}); return false;">
                            <i class="fas fa-cart-plus me-1"></i> Add to Cart
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    // Display "no results" message
    displayNoResults: function() {
        this.resultsContainer.innerHTML = `
            <div class="row align-items-center position-relative mb-5">
                <div class="col">
                    <p class="mb-3 fs-sm text-center">Nothing matches your search</p>
                    <p class="mb-0 fs-sm text-center">😞</p>
                </div>
            </div>
        `;
        this.showResults();
    },

    // Display error message
    displayError: function(message) {
        this.resultsContainer.innerHTML = `
            <div class="row align-items-center position-relative mb-5">
                <div class="col">
                    <p class="mb-0 fs-sm text-center text-danger">${message}</p>
                </div>
            </div>
        `;
        this.showResults();
    },

    // Show loading indicator
    showLoading: function() {
        this.state.isLoading = true;
        this.resultsContainer.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        this.showResults();
    },

    // Hide loading indicator
    hideLoading: function() {
        this.state.isLoading = false;
    },

    // Clear search results
    clearResults: function() {
        this.resultsContainer.innerHTML = '';
    },

    // Show results container
    showResults: function() {
        this.resultsContainer.classList.remove('d-none');
    },

    // Hide results container
    hideResults: function() {
        this.resultsContainer.classList.add('d-none');
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    LiveSearch.init();
});
