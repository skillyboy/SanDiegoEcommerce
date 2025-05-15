/**
 * Navbar Search Functionality
 * This script handles the search functionality in the navbar
 */

$(document).ready(function() {
    // Get elements
    const searchInput = $('#navbar-search-input');
    const searchButton = $('#navbar-search-button');
    const searchSuggestions = $('#navbar-search-suggestions');
    
    // Debounce function to limit API calls during typing
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    // Function to get search suggestions
    const getSuggestions = debounce(function(query) {
        if (query.length < 2) {
            searchSuggestions.addClass('d-none').empty();
            return;
        }
        
        $.ajax({
            url: "/load_more_products/",
            type: "GET",
            data: {
                'page': 1,
                'per_page': 5,
                'search': query
            },
            success: function(response) {
                if (response.products && response.products.length > 0) {
                    searchSuggestions.empty().removeClass('d-none');
                    
                    response.products.forEach(product => {
                        const suggestion = $(`
                            <div class="suggestion-item">
                                <img src="${product.image_url}" alt="${product.name}" class="suggestion-img">
                                <div>
                                    <div class="suggestion-name">${product.name}</div>
                                    <div class="suggestion-price">$${product.price}</div>
                                </div>
                            </div>
                        `);
                        
                        suggestion.on('click', function() {
                            window.location.href = product.url;
                        });
                        
                        searchSuggestions.append(suggestion);
                    });
                    
                    // Add "See all results" link
                    searchSuggestions.append(`
                        <div class="p-2 text-center">
                            <a href="#" id="see-all-results" class="text-primary">See all results</a>
                        </div>
                    `);
                    
                    // Handle "See all results" click
                    $('#see-all-results').on('click', function(e) {
                        e.preventDefault();
                        performSearch(query);
                        searchSuggestions.addClass('d-none');
                    });
                } else {
                    searchSuggestions.addClass('d-none').empty();
                }
            },
            error: function() {
                searchSuggestions.addClass('d-none').empty();
            }
        });
    }, 300);
    
    // Handle search input
    searchInput.on('input', function() {
        const query = $(this).val().trim();
        getSuggestions(query);
    });
    
    // Handle search button click
    searchButton.on('click', function() {
        const query = searchInput.val().trim();
        if (query.length > 0) {
            performSearch(query);
            searchSuggestions.addClass('d-none');
        }
    });
    
    // Handle Enter key in search input
    searchInput.on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            const query = $(this).val().trim();
            if (query.length > 0) {
                performSearch(query);
                searchSuggestions.addClass('d-none');
            }
        }
    });
    
    // Close suggestions when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.search-container').length) {
            searchSuggestions.addClass('d-none');
        }
    });
    
    // Function to perform search
    function performSearch(query) {
        // Redirect to shop page with search query
        window.location.href = `/shop/?search=${encodeURIComponent(query)}`;
    }
});
