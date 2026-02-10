# Standard Library Imports
import uuid
import logging
import json
import os

# Third-Party Imports
import requests
from decimal import Decimal

# Django Imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Sum, F, FloatField, Q, Count
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.utils import timezone
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import quote

from .forms import AccountUpdateForm  # Ensure you create a form class for handling user input

# Local Application Imports
from .models import *
from .forms import *
from .serializers import *
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.http import require_POST
import stripe
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage

# Logging configuration
logger = logging.getLogger(__name__)

# Set Stripe API key with error handling
try:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if not stripe.api_key:
        logger.warning("Stripe API key is not set or empty")
except Exception as e:
    logger.warning(f"Error setting Stripe API key: {e}")

# from rest_framework.response import Response
from django.contrib.auth.forms import PasswordChangeForm
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Payment, ShopCart
from django.conf import settings
# Views List
# -------------------




# Home page view
def my_orders(request):
    return render(request, 'my_orders.html')

# African Groceries page view
def african_groceries(request):
    """
    View for the African Groceries page that showcases African grocery products
    """
    # Get featured products for the African Groceries page
    featured_products = Product.objects.filter(
        featured=True,
        category__name__icontains='grocery'
    )[:8]  # Limit to 8 featured products

    # Get categories related to groceries
    grocery_categories = Service.objects.filter(
        name__icontains='grocery'
    )

    context = {
        'featured_products': featured_products,
        'grocery_categories': grocery_categories,
        'page_title': 'African Groceries',
    }

    return render(request, 'african_groceries.html', context)

# Local delivery page view
def local_delivery(request):
    return render(request, 'local_delivery.html')

# Today's deals page view
def deals(request):
    return render(request, 'deals.html')

# Clearance page view
def clearance(request):
    return render(request, 'clearance.html')

# File a claim page view
def file_claim(request):
    return render(request, 'file_claim.html')

# Blog page view
def blog(request):
    return render(request, 'blog.html')

# Our stores page view
def stores(request):
    return render(request, 'stores.html')

# Account personal info (requires user to be logged in)



# 2. Home View

class HomeView(TemplateView):
    template_name = "home.html"
# use this template model for the rest right ones, except add_to_cart and the likes that i might want to use ninja for

# 3. Test View
def test(request):
    return render(request, 'test.html')


# 4. Custom 404 Error View
def custom_404(request, exception):
    return render(request, '404.html', status=404)


# 5. Payment View
def payment(request):
    return render(request, 'payment.html')


# 6. About View
def about(request):
    return render(request, 'about.html')


# 7. Contact Us Page View
def contact_us(request):
    return render(request, 'contact-us.html')


# 8. FAQ View
def faq(request):
    return render(request, 'faq.html')


# 8.1 Help & Documentation View
def help_page(request):
    return render(request, 'help.html')


# 9. Store Locator View
def store_locator(request):
    return render(request, 'store-locator.html')


# 10. Shipping View
def shipping(request):
    return render(request, 'shipping.html')

# 11. Returns View
def returns(request):
    return render(request, 'returns.html')

# Terms and Conditions page view
def terms(request):
    return render(request, 'terms.html')


# 11. Account Personal Info View
@login_required
def account_personal_info(request):
    return render(request, 'account/account-personal-info.html')


def account_update(request):
    if request.method == 'POST':
        form = AccountUpdateForm(request.POST)
        if form.is_valid():
            # Here you would typically save the form data to the database
            form.save()
            messages.success(request, 'Your account has been updated successfully!')
            return redirect('account-personal-info')  # Redirect to the personal info page
    else:
        # Initialize the form with the current user's data
        form = AccountUpdateForm(instance=request.user)  # Adjust this if your user model is different

    context = {
        'form': form,
    }

    return render(request, 'account/account_personal_info.html', context)
# 12. Account Address View
def account_address(request):
    user = request.user
    addresses = PaymentInfo.objects.filter(user=user)
    return render(request, 'account/account-address.html', {"addresses":addresses})

@login_required
def delete_address(request, address_id):
    """Delete an existing shipping address."""
    address = get_object_or_404(PaymentInfo, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Shipping address deleted successfully.')
    return redirect('account_address')  # Redirect back to the address page

@login_required
def edit_payment_info(request, payment_id):
    """Edit a PaymentInfo record using a custom HTML form."""
    payment = get_object_or_404(PaymentInfo, id=payment_id, user=request.user)

    if request.method == "POST":
        # Extract data from the form submission
        payment.first_name = request.POST.get("first_name", payment.first_name)
        payment.last_name = request.POST.get("last_name", payment.last_name)
        payment.phone = request.POST.get("phone", payment.phone)
        payment.address = request.POST.get("address", payment.address)
        payment.city = request.POST.get("city", payment.city)
        payment.state = request.POST.get("state", payment.state)
        payment.postal_code = request.POST.get("postal_code", payment.postal_code)
        payment.country = request.POST.get("country", payment.country)

        # Save the updated payment info
        payment.save()

        messages.success(request, "Payment information updated successfully!")
        return redirect("account_address")  # Redirect to the address page

    return render(request, "account/account-address-edit.html", {"payment": payment})

@login_required
def add_address(request):
    """Allow users to add a new address."""
    if request.method == "POST":
        # Create a new address entry
        new_address = PaymentInfo.objects.create(
            user=request.user,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            postal_code=request.POST.get("postal_code"),
            country=request.POST.get("country"),
        )

        messages.success(request, "Address added successfully!")
        return redirect("account_address")  # Redirect to the address page

    return render(request, "account/account-address-add.html")


# 14. Account Wishlist View
def account_wishlist(request):
    return render(request, 'account/account-wishlist.html')


# 15. Error 404 Page
def error_404(request, exception=None):
    return render(request, '404.html')


# 16. Coming Soon View
def coming_soon(request):
    return render(request, 'coming-soon.html')


# Sitemap View
def sitemap_view(request):
    """Generate a dynamic sitemap.xml file"""
    # Get the site URL
    site_url = f"{request.scheme}://{request.get_host()}"

    # Get all categories
    categories = Category.objects.all()

    # Get all products
    products = Product.objects.filter(available=True)

    # Get the last modified date (use the most recent product update)
    try:
        last_modified = products.latest('date_created').date_created.strftime('%Y-%m-%d')
    except:
        last_modified = timezone.now().strftime('%Y-%m-%d')

    context = {
        'site_url': site_url,
        'categories': categories,
        'products': products,
        'last_modified': last_modified,
    }

    # Return the sitemap with the correct content type
    return render(request, 'sitemap.xml', context, content_type='application/xml')


# Robots.txt View
def robots_txt_view(request):
    """Generate a dynamic robots.txt file"""
    site_url = f"{request.scheme}://{request.get_host()}"

    context = {
        'site_url': site_url,
    }

    return render(request, 'robots.txt', context, content_type='text/plain')


# Authentication Views
# -----------------------


class SignupFormView(View):
    def get(self, request):
        return render(request, 'signup.html', {'next': request.GET.get('next', '')})

    def post(self, request):
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Preserve redirect target as early as possible
        next_url = request.POST.get('next') or request.GET.get('next') or request.session.get('pending_cart_next') or ''

        # Validate form inputs
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html', {'next': next_url})

        # Check if user already exists - handle this gracefully with a message
        if User.objects.filter(username=email).exists():
            messages.warning(request, 'An account with that email already exists. Please log in instead.')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(f"{reverse('login')}?next={quote(next_url, safe='')}")
            return redirect('login')

        try:
            with transaction.atomic():
                # Create the user
                user = User.objects.create_user(
                    username=email,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password1
                )

                # Create the Customer profile
                Customer.objects.create(user=user, first_name=first_name, last_name=last_name, email=email)

            # Log the user in after successful creation
            login(request, user)
            messages.success(request, 'Signup successful! Welcome to African Food.')
            # Handle pending buy-now flow (priority over regular cart add)
            try:
                pending_buy_now = request.session.get('pending_buy_now')
                if pending_buy_now:
                    pid = pending_buy_now.get('product_id')
                    qty = pending_buy_now.get('quantity', 1)
                    if pid:
                        product = get_object_or_404(Product, id=pid)
                        cart_item, created = ShopCart.objects.get_or_create(
                            user=request.user,
                            product=product,
                            paid_order=False,
                            defaults={'quantity': 0}
                        )
                        # Normalize quantity with min/max/stock constraints
                        try:
                            qty = int(qty)
                        except (TypeError, ValueError):
                            qty = 1
                        if qty < product.min_purchase:
                            qty = product.min_purchase
                        if qty > product.max_purchase:
                            qty = product.max_purchase
                        if qty > product.stock_quantity:
                            qty = product.stock_quantity
                        cart_item.quantity = qty
                        cart_item.save()
                        request.session['buy_now_product_id'] = product.id
                        request.session['buy_now_quantity'] = qty
                    request.session.pop('pending_buy_now', None)
                    request.session.pop('pending_cart_add', None)
                    request.session.pop('pending_cart_next', None)
                    return redirect('checkout')
            except Exception as e:
                logger.warning(f"Buy-now after signup failed: {e}")
            # Attempt to auto-add pending cart item
            try:
                pending = request.session.get('pending_cart_add')
                if pending:
                    pid = pending.get('product_id')
                    qty = pending.get('quantity', 1)
                    if pid:
                        product = get_object_or_404(Product, id=pid)
                        cart_item, created = ShopCart.objects.get_or_create(
                            user=request.user,
                            product=product,
                            paid_order=False,
                            defaults={'quantity': 0}
                        )
                        new_quantity = cart_item.quantity + int(qty)
                        if new_quantity > product.max_purchase:
                            new_quantity = product.max_purchase
                        if new_quantity < product.min_purchase:
                            new_quantity = product.min_purchase
                        if new_quantity > product.stock_quantity:
                            messages.warning(request, f'Only {product.stock_quantity} items available in stock.')
                        else:
                            cart_item.quantity = new_quantity
                            cart_item.save()
                request.session.pop('pending_cart_add', None)
                request.session.pop('pending_cart_next', None)
            except Exception as e:
                logger.warning(f"Auto-add after signup failed: {e}")

            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('index')

        except Exception as e:
            logger.error(f"Signup failed: {e}")
            messages.error(request, 'An unexpected error occurred during signup. Please try again later.')
            return render(request, 'signup.html', {'next': next_url})


# 18. Login View with Error Handling
class LoginPageView(View):
    def get(self, request):
        return render(request, 'login.html', {'next': request.GET.get('next', '')})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next') or request.session.get('pending_cart_next') or ''
        # Avoid redirecting back to add-to-cart endpoints
        if next_url and ('/add_to_cart/' in next_url or '/add-to-cart/' in next_url):
            next_url = request.session.get('pending_cart_next') or ''

        # change email to password every other thing still remains the same
        user = authenticate(request, username=username, password=password)  # Email is treated as username

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            # Handle pending buy-now flow (priority over regular cart add)
            try:
                pending_buy_now = request.session.get('pending_buy_now')
                if pending_buy_now:
                    pid = pending_buy_now.get('product_id')
                    qty = pending_buy_now.get('quantity', 1)
                    if pid:
                        product = get_object_or_404(Product, id=pid)
                        cart_item, created = ShopCart.objects.get_or_create(
                            user=request.user,
                            product=product,
                            paid_order=False,
                            defaults={'quantity': 0}
                        )
                        # Normalize quantity with min/max/stock constraints
                        try:
                            qty = int(qty)
                        except (TypeError, ValueError):
                            qty = 1
                        if qty < product.min_purchase:
                            qty = product.min_purchase
                        if qty > product.max_purchase:
                            qty = product.max_purchase
                        if qty > product.stock_quantity:
                            qty = product.stock_quantity
                        cart_item.quantity = qty
                        cart_item.save()
                        request.session['buy_now_product_id'] = product.id
                        request.session['buy_now_quantity'] = qty
                    request.session.pop('pending_buy_now', None)
                    request.session.pop('pending_cart_add', None)
                    request.session.pop('pending_cart_next', None)
                    return redirect('checkout')
            except Exception as e:
                logger.warning(f"Buy-now after login failed: {e}")
            # Attempt to auto-add pending cart item
            try:
                pending = request.session.get('pending_cart_add')
                if pending:
                    pid = pending.get('product_id')
                    qty = pending.get('quantity', 1)
                    if pid:
                        product = get_object_or_404(Product, id=pid)
                        cart_item, created = ShopCart.objects.get_or_create(
                            user=request.user,
                            product=product,
                            paid_order=False,
                            defaults={'quantity': 0}
                        )
                        new_quantity = cart_item.quantity + int(qty)
                        if new_quantity > product.max_purchase:
                            new_quantity = product.max_purchase
                        if new_quantity < product.min_purchase:
                            new_quantity = product.min_purchase
                        if new_quantity > product.stock_quantity:
                            messages.warning(request, f'Only {product.stock_quantity} items available in stock.')
                        else:
                            cart_item.quantity = new_quantity
                            cart_item.save()
                request.session.pop('pending_cart_add', None)
                request.session.pop('pending_cart_next', None)
            except Exception as e:
                logger.warning(f"Auto-add after login failed: {e}")

            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('index')
        else:
            messages.error(request, 'Email/password incorrect')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(f"{reverse('login')}?next={quote(next_url, safe='')}")
            return redirect('login')


# 19. Logout View
class LogoutFuncView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Logged out successfully')
        return redirect('login')


# 20. Password Change View with Error Handling
class PasswordChangeView(View):
    @login_required(login_url='/login')
    def get(self, request):
        update = PasswordChangeForm(request.user)
        context = {'update': update}
        return render(request, 'password.html', context)

    @login_required(login_url='/login')
    def post(self, request):
        update = PasswordChangeForm(request.user, request.POST)

        if update.is_valid():
            user = update.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully!')
            return redirect('index')
        else:
            for error in update.errors.values():
                messages.error(request, error)
            return redirect('password')

# API endpoint for JavaScript search
def api_search_products(request):
    """
    API endpoint for JavaScript-based search.
    Returns JSON response with search results.
    """
    search_term = request.GET.get("search", "")
    category_id = request.GET.get("category", None)

    # Skip search if term is too short
    if len(search_term) < 2:
        return JsonResponse({"products": []})

    # Use __icontains for case-insensitive search on product name and description
    searched_items = Q(name__icontains=search_term) | Q(description__icontains=search_term)

    # If a category is selected, filter by that category as well
    if category_id and category_id != "All Categories":
        try:
            # Try to convert to integer for ID-based lookup
            category_id = int(category_id)
            products = Product.objects.filter(searched_items, category__id=category_id)
        except (ValueError, TypeError):
            # If not an integer, try to match by name
            products = Product.objects.filter(searched_items, category__name=category_id)
    else:
        products = Product.objects.filter(searched_items)

    # Limit results to improve performance
    products = products[:12]

    # Prepare product data for JSON response
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'image_url': product.image.url if product.image else '',
            'category': product.category.name if product.category else '',
            'url': reverse('product', args=[product.id]),
        })

    return JsonResponse({"products": product_data})

def search_products(request):
    """Compatibility wrapper for `search_products` URL that delegates to `api_search_products`.
    Kept for backwards compatibility with routes expecting a view named `search_products`.
    """
    return api_search_products(request)

# End


# 5. Index View with Error Handling

class IndexView(TemplateView):
    def get(self, request, service_id=None):
        try:
            featured = Product.objects.filter(featured=True)
            latest = Product.objects.filter(latest=True)
            services = Service.objects.all()

            # Fetch the last 10 products based on date_created
            latest_products = Product.objects.order_by('-date_created')[:10]

        except (Product.DoesNotExist, Exception) as e:
            # Handle any database-related errors, including missing tables
            logger.error(f"Error loading products: {str(e)}")
            featured, latest, services, latest_products = [], [], [], []
            messages.error(request, 'Products could not be loaded. The site is still being set up.')

        context = {
            'featured': featured if 'featured' in locals() else [],
            'latest': latest if 'latest' in locals() else [],
            'services': services if 'services' in locals() else [],
            'service_id': service_id,
            'latest_products': latest_products if 'latest_products' in locals() else [],  # Pass latest products to context
        }

        template = 'shop.html' if service_id else 'index.html'
        return render(request, template, context)

class ServiceDetailView(TemplateView):
    template_name = 'category_detail.html'

    def get(self, request, id=None, service_type=None):
        # Handle the new URL patterns (groceries and restaurant)
        if service_type:
            if service_type == 'groceries':
                # For /groceries/ URL, use service ID 1
                id = 1
            elif service_type == 'restaurant':
                # For /restaurant/ URL, use service ID 2
                id = 2

        # Get the service using the provided ID
        service = get_object_or_404(Service, pk=id)

        # Set the category_id based on your logic
        # If the service ID correlates directly with category IDs, use that directly
        category_id = service.id  # Adjust this logic if necessary

        # Retrieve all categories related to the service
        categories = service.services.all()  # Use 'services' since it's the related name

        categories_with_products = {}
        total_products = 0

        # Iterate through categories and get products
        for category in categories:
            products = category.products.filter(available=True)
            product_count = products.count()
            categories_with_products[category] = {
                'products': products,
                'product_count': product_count
            }
            total_products += product_count

        # Calculate the percentage for each category
        for category, data in categories_with_products.items():
            product_count = data['product_count']
            percentage = (product_count / total_products * 100) if total_products > 0 else 0
            categories_with_products[category]['percentage'] = percentage

        # Define service-specific content
        service_content = {}
        if category_id == 1:  # Groceries
            service_content = {
                'title': 'African Grocery Marketplace',
                'description': 'Discover authentic Nigerian ingredients and food products imported directly from West Africa.',
                'subtitle': 'Premium Selection',
                'detail': 'Our grocery selection features premium quality ingredients essential for preparing traditional Nigerian dishes. From spices and seasonings to grains and snacks, we offer everything you need to bring the taste of Nigeria to your kitchen.'
            }
        elif category_id == 2:  # Restaurant
            service_content = {
                'title': 'Nigerian Restaurant Experience',
                'description': 'Experience authentic Nigerian cuisine with our delicious dishes prepared with traditional recipes.',
                'subtitle': 'Authentic Cuisine',
                'detail': 'Our restaurant offers a variety of traditional Nigerian dishes made with authentic recipes and fresh ingredients. From Jollof Rice to Egusi Soup, we bring the rich flavors of Nigeria to your table.'
            }

        # Get featured products for this service
        featured_products = []
        # Collect all products from all categories of this service
        all_service_products = []
        for category, data in categories_with_products.items():
            all_service_products.extend(data['products'])

        # Get featured products (up to 3)
        featured_products = [p for p in all_service_products if p.featured][:3]

        # If we don't have enough featured products, add some regular products
        if len(featured_products) < 3:
            regular_products = [p for p in all_service_products if p not in featured_products]
            featured_products.extend(regular_products[:3-len(featured_products)])

        return render(request, self.template_name, {
            'service': service,
            'categories_with_products': categories_with_products,
            'total_products': total_products,
            'category_id': category_id,  # Pass category_id to the template
            'service_type': service_type,  # Pass service_type to the template
            'service_content': service_content,  # Pass service-specific content
            'featured_products': featured_products,  # Pass featured products from this service
        })



# 7. Shop View
class ShopView(TemplateView):
    template_name = 'shop.html'

    def get(self, request, *args, **kwargs):
        # Get the selected category ID from the request
        category_id = request.GET.get('category_id')
        search_query = request.GET.get('search')

        # Start with all products
        products_query = Product.objects.filter(available=True)

        # Apply category filter if provided
        if category_id:
            try:
                category_id = int(category_id)
                products_query = products_query.filter(category__id=category_id)
            except (ValueError, TypeError):
                # If not a valid integer, try to match by slug
                products_query = products_query.filter(category__slug=category_id)

        # Apply search filter if provided
        if search_query:
            products_query = products_query.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Get all services (main categories)
        services = Service.objects.all().prefetch_related('services')

        # Get all categories with their products count
        categories = Category.objects.all().annotate(
            product_count=Count('products')
        )

        # Organize categories by service
        service_categories = {}
        for service in services:
            service_categories[service] = categories.filter(service=service)

        # Only load a limited number of products initially for better performance
        products = products_query.order_by('-date_created')[:12]

        # Retrieve the cart count from the session
        cart_count = request.session.get('cart_count', 0)

        context = {
            'products': products,
            'services': services,
            'service_categories': service_categories,
            'categories': categories,
            'selected_category_id': category_id,
            'cart_count': cart_count,
            'search_query': search_query,
            'is_ajax': False,  # Flag to indicate this is not an AJAX request
        }

        return render(request, self.template_name, context)

# AJAX Product Loading View
def load_more_products(request):
    """
    AJAX view to load more products dynamically
    """
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 12))
    category_id = request.GET.get('category_id')
    search_query = request.GET.get('search')

    # Calculate offset
    offset = (page - 1) * per_page

    # Query products with pagination
    products_query = Product.objects.filter(available=True)

    # Apply category filter if provided
    if category_id and category_id != 'all':
        try:
            category_id = int(category_id)
            products_query = products_query.filter(category__id=category_id)
        except (ValueError, TypeError):
            # If not a valid integer, try to match by slug
            products_query = products_query.filter(category__slug=category_id)

    # Apply search filter if provided
    if search_query:
        products_query = products_query.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Get total count for pagination info
    total_count = products_query.count()

    # Apply pagination
    products = products_query.order_by('-date_created')[offset:offset + per_page]

    # Check if there are more products
    has_more = (offset + per_page) < total_count

    # Prepare product data for JSON response
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'image_url': product.image.url if product.image else '',
            'category': product.category.name if product.category else '',
            'category_id': product.category.id if product.category else None,
            'is_on_sale': product.is_on_sale(),
            'regular_price': float(product.price) if product.is_on_sale() else None,
            'sale_price': float(product.sale_price) if product.is_on_sale() else None,
            'url': reverse('product', args=[product.id]),
            'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
        })

    # Return JSON response
    return JsonResponse({
        'products': product_data,
        'has_more': has_more,
        'total_count': total_count,
        'current_page': page,
    })


# 8. Product Detail View with DRF
class ProductDetailView(View):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        return render(request, 'product.html', {'product': product})

# 9. Add to Wishlist
@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        try:
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            wishlist.add_product(product)
            return JsonResponse({'success': True, 'message': 'Product added to wishlist'})
        except Exception as e:
            logger.error(f"Error adding to wishlist: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Error adding to wishlist. Please try again.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# 11. Add to Cart
@require_POST
@transaction.atomic
def add_to_cart(request, id=None, product_id=None):
    # Normalize parameter name: some URL patterns pass `id`, others `product_id`
    pid = product_id or id or request.POST.get('product_id')
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid product identifier'}, status=400)

    # If user is not authenticated, handle AJAX and normal requests differently
    if not request.user.is_authenticated:
        # Store pending cart add for post-login auto-add
        try:
            pending_qty = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            pending_qty = 1
        request.session['pending_cart_add'] = {'product_id': pid, 'quantity': pending_qty}

        # Prefer referrer for next so we return to the product/listing page
        referrer = request.META.get('HTTP_REFERER')
        next_url = referrer if (referrer and url_has_allowed_host_and_scheme(referrer, allowed_hosts={request.get_host()})) else request.get_full_path()
        if '/add_to_cart/' in next_url or '/add-to-cart/' in next_url:
            next_url = '/'
        request.session['pending_cart_next'] = next_url

        login_url = f"{reverse('login')}?next={quote(next_url, safe='')}"
        # AJAX requests should get a JSON 401 so client doesn't receive HTML login page
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Authentication required', 'login_url': login_url}, status=401)
        # Non-AJAX: redirect to login as before
        return redirect(login_url)

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            return JsonResponse({'success': False, 'error': 'Invalid quantity'})
        product = get_object_or_404(Product, id=pid)
        # Some Product models may not have `is_active`; treat missing attribute as active
        if not getattr(product, 'is_active', True):
            return JsonResponse({'success': False, 'error': 'This product is currently unavailable'})
        cart_item, created = ShopCart.objects.get_or_create(
            user=request.user,
            product=product,
            paid_order=False,
            defaults={'quantity': 0}
        )
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.max_purchase:
            return JsonResponse({'success': False, 'error': f'Maximum {product.max_purchase} items allowed per order'})
        if new_quantity < product.min_purchase:
            new_quantity = product.min_purchase
        if new_quantity > product.stock_quantity:
            return JsonResponse({'success': False, 'error': f'Sorry, only {product.stock_quantity} items available in stock'})
        cart_item.quantity = new_quantity
        cart_item.save()
        cart_count = ShopCart.objects.filter(user=request.user, paid_order=False).aggregate(
            total_items=Sum('quantity'),
            total_amount=Sum(F('quantity') * F('product__price'), output_field=FloatField())
        )
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart successfully',
            'cart_count': cart_count['total_items'] or 0,
            'cart_total': "{:.2f}".format(cart_count['total_amount'] or 0),
            'item_count': new_quantity
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid quantity specified'})
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An error occurred while adding to cart'})

# Buy Now (single item checkout)
@require_POST
@transaction.atomic
def buy_now(request, product_id=None, id=None):
    pid = product_id or id or request.POST.get('product_id')
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid product identifier.')
        return redirect('shop')

    # Quantity from form
    try:
        qty = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        qty = 1

    if not request.user.is_authenticated:
        request.session['pending_buy_now'] = {'product_id': pid, 'quantity': qty}
        login_url = f"{reverse('login')}?next={quote(reverse('checkout'), safe='')}"
        return redirect(login_url)

    try:
        product = get_object_or_404(Product, id=pid)

        # Normalize quantity with product constraints
        if qty < product.min_purchase:
            qty = product.min_purchase
        if qty > product.max_purchase:
            qty = product.max_purchase
        if qty > product.stock_quantity:
            qty = product.stock_quantity

        cart_item, created = ShopCart.objects.get_or_create(
            user=request.user,
            product=product,
            paid_order=False,
            defaults={'quantity': 0}
        )
        cart_item.quantity = qty
        cart_item.save()

        request.session['buy_now_product_id'] = product.id
        request.session['buy_now_quantity'] = qty

        return redirect('checkout')
    except Exception as e:
        logger.error(f"Buy now failed: {e}")
        messages.error(request, 'Unable to process Buy Now. Please try again.')
        return redirect('product', pid)

# 12. Cart View
@method_decorator(login_required, name='dispatch')
class CartView(View):
    def get(self, request):
        # Ensure the session has a session_key
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key

        # If user is authenticated, merge any session-based cart items into the user's cart
        try:
            with transaction.atomic():
                if request.user.is_authenticated:
                    session_items = ShopCart.objects.filter(session_key=session_key, paid_order=False)
                    for s_item in session_items:
                        # try find existing cart item for this user & product
                        existing = ShopCart.objects.filter(user=request.user, product=s_item.product, paid_order=False).first()
                        if existing:
                            existing.quantity = min(existing.quantity + s_item.quantity, s_item.product.max_purchase)
                            existing.save()
                            s_item.delete()
                        else:
                            s_item.user = request.user
                            s_item.session_key = None
                            s_item.save()

            # After any merge, fetch cart items for display
            if request.user.is_authenticated:
                cart = ShopCart.objects.filter(user=request.user, paid_order=False)
            else:
                cart = ShopCart.objects.filter(session_key=session_key, paid_order=False)

            # Calculate totals for display
            for item in cart:
                try:
                    item.total_price = item.calculate_total_price()
                except Exception:
                    # fallback if method missing
                    item.total_price = (getattr(item.product, 'price', 0) or 0) * (item.quantity or 0)

            cartreader = sum(item.quantity for item in cart)
            subtotal = sum(getattr(item, 'total_price', 0) for item in cart)
            from decimal import Decimal
            if not isinstance(subtotal, Decimal):
                subtotal = Decimal(str(subtotal))
            vat = Decimal('0.075') * subtotal
            total = subtotal + vat
            request.session['cart_count'] = cartreader
            request.session.modified = True
            context = {
                'cart': cart,
                'cartreader': cartreader,
                'subtotal': round(float(subtotal), 2),
                'vat': round(float(vat), 2),
                'total': round(float(total), 2),
            }
            return render(request, 'cart.html', context)
        except Exception as e:
            logger.error(f"Error loading cart view: {e}")
            messages.error(request, 'There was an error loading your cart. Please try again.')
            return render(request, 'cart.html', {})

# Increase/Decrease/Remove Cart Items (user only)
@login_required
def increase_quantity(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(ShopCart, id=item_id, user=request.user)
            cart_item.quantity += 1
            cart_item.save()
            subtotal, vat, total = calculate_cart_summary(request)
            return JsonResponse({
                'success': True,
                'new_quantity': cart_item.quantity,
                'new_total_price': round(cart_item.calculate_total_price(), 2),
                'subtotal': round(float(subtotal), 2),
                'vat': round(float(vat), 2),
                'total': round(float(total), 2),
            })
        except Exception as e:
            logger.error(f"Error increasing quantity: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Failed to increase quantity. Please try again.'}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def decrease_quantity(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(ShopCart, id=item_id, user=request.user)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            subtotal, vat, total = calculate_cart_summary(request)
            return JsonResponse({
                'success': True,
                'new_quantity': cart_item.quantity,
                'new_total_price': round(cart_item.calculate_total_price(), 2),
                'subtotal': round(float(subtotal), 2),
                'vat': round(float(vat), 2),
                'total': round(float(total), 2),
            })
        except Exception as e:
            logger.error(f"Error decreasing quantity: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Failed to decrease quantity. Please try again.'}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def remove_from_cart(request, cart_item_id):
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(ShopCart, id=cart_item_id, user=request.user)
            cart_item.delete()
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                subtotal, vat, total = calculate_cart_summary(request)
                cart_empty = not ShopCart.objects.filter(user=request.user, paid_order=False).exists()
                return JsonResponse({
                    'success': True,
                    'subtotal': subtotal,
                    'vat': vat,
                    'total': total,
                    'cart_empty': cart_empty
                })
            return redirect(request.META.get('HTTP_REFERER', 'cart'))
        except ShopCart.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cart item not found. Please refresh the page and try again.'}, status=404)
    return JsonResponse({'success': False, 'message': 'Invalid request method. Please use POST.'}, status=400)

@login_required
def remove_from_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist.remove_product(product)
        return JsonResponse({'success': True, 'message': 'Product removed from wishlist'})

# Cart summary for authenticated user only
def calculate_cart_summary(request):
    cart_items = ShopCart.objects.filter(user=request.user, paid_order=False)
    subtotal = cart_items.aggregate(subtotal=Sum(F('product__price') * F('quantity')))['subtotal'] or Decimal('0.0')
    vat = subtotal * Decimal('0.075')
    total = subtotal + vat
    return float(subtotal), float(vat), float(total)

# Checkout view (user only)
@method_decorator(login_required, name='dispatch')
class CheckoutView(TemplateView):
    def get(self, request):
        buy_now_product_id = request.session.get('buy_now_product_id')
        if buy_now_product_id:
            cart = ShopCart.objects.filter(user=request.user, paid_order=False, product_id=buy_now_product_id)
        else:
            cart = ShopCart.objects.filter(user=request.user, paid_order=False)
        customer = Customer.objects.filter(user=request.user).first()
        if not cart.exists():
            messages.error(request, 'No items in the cart.')
            return redirect('cart')
        total_price = sum(item.calculate_total_price() for item in cart)
        basket_no = cart.first().basket_no if cart.exists() else None
        context = {
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            'cart': cart,
            'customer': customer,
            'total_price': total_price,
            'basket_no': basket_no,
            'is_guest': False,
            'buy_now_only': bool(buy_now_product_id),
        }
        return render(request, 'checkout.html', context)

# Payment pipeline (user only)
@method_decorator(login_required, name='dispatch')
class PaymentPipelineView(View):
    def post(self, request, *args, **kwargs):
        try:
            stripe_secret = getattr(settings, 'STRIPE_SECRET_KEY', None)
            if not stripe_secret or 'your_key_here' in str(stripe_secret):
                messages.error(request, 'Stripe is not configured. Please set STRIPE_SECRET_KEY in your environment.')
                return redirect('checkout')

            # Ensure Stripe is initialized for this request
            stripe.api_key = stripe_secret
            # Temporary debug log to confirm Stripe key is loaded in runtime
            logger.info("Stripe key prefix: %s", stripe_secret[:8])

            basket_no = request.POST.get('basket_no')
            shipping_option = request.POST.get('shipping_option')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            postal_code = request.POST.get('postal_code')
            country = request.POST.get('country')
            payment_method = 'credit_card'
            user = request.user

            buy_now_product_id = request.session.get('buy_now_product_id')
            if buy_now_product_id:
                cart_items = ShopCart.objects.filter(user=user, paid_order=False, product_id=buy_now_product_id)
            else:
                cart_items = ShopCart.objects.filter(user=user, paid_order=False)
            if not cart_items.exists():
                messages.error(request, 'No items in the cart.')
                return redirect('cart')

            # Calculate total amount in cents
            total_price_with_shipping = sum(item.product.price * item.quantity for item in cart_items)
            total_amount = int(float(total_price_with_shipping) * 100)

            from django.utils.crypto import get_random_string
            pay_code = get_random_string(12)
            transaction_id = get_random_string(20)

            # Create a PaymentInfo record to track this attempt
            payment = PaymentInfo.objects.create(
                user=user,
                amount=total_amount,
                stripe_payment_intent_id=None,
                basket_no=basket_no,
                pay_code=pay_code,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                payment_method=payment_method,
                transaction_id=transaction_id,
                created_at=timezone.now(),
                email=user.email if user and user.email else (request.POST.get('email') or ''),
            )

            # Build Stripe line items from cart
            YOUR_DOMAIN = request.build_absolute_uri('/')[:-1]  # e.g. http://localhost:8000
            line_items = []
            for item in cart_items:
                try:
                    unit_amount = int(float(item.product.price) * 100)
                except Exception:
                    unit_amount = 0
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                        },
                        'unit_amount': unit_amount,
                    },
                    'quantity': int(item.quantity),
                })

            # Pass customer name and email to Stripe so the Checkout form is prefilled
            customer_email = payment.email if payment.email else None
            customer_name = ' '.join(filter(None, [payment.first_name, payment.last_name])) or None

            # Create a Stripe Checkout Session and redirect the browser to it
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                metadata={"payment_id": str(payment.id), "basket_no": basket_no},
                mode='payment',
                success_url=f'{YOUR_DOMAIN}/successpayment/',
                cancel_url=f'{YOUR_DOMAIN}/cancelpayment/',
                customer_email=customer_email,
            )

            # Associate the session id with our payment record for later verification
            try:
                payment.stripe_payment_intent_id = checkout_session.id
                payment.save()
            except Exception:
                logger.exception("Failed to save stripe_session_id on payment record")

            # Redirect the browser to the Stripe Checkout URL (hosted by Stripe)
            return redirect(checkout_session.url)

        except Exception as e:
            logger.error(f"Payment pipeline error: {str(e)}")
            messages.error(request, 'Payment initiation failed. Please try again.')
            return redirect('cart')

# Update CompletedPaymentView to return early if PaymentInfo already processed
class CompletedPaymentView(View):
    def get(self, request):
        try:
            # Only authenticated users supported now
            payment = PaymentInfo.objects.filter(user=request.user, paid_order=False).order_by('-created_at').first()

            if not payment:
                messages.error(request, "No payment record found.")
                return redirect("cart")

            # If already processed by webhook, redirect to order history
            if payment.paid_order:
                messages.info(request, "Payment already processed.")
                return redirect('order_history')

            buy_now_product_id = request.session.get('buy_now_product_id')
            if buy_now_product_id:
                cart_items = ShopCart.objects.filter(user=request.user, paid_order=False, product_id=buy_now_product_id)
            else:
                cart_items = ShopCart.objects.filter(user=request.user, paid_order=False)

            if not cart_items.exists():
                messages.error(request, "No paid items found in cart.")
                return redirect("cart")

            # Calculate cart summary
            subtotal, vat, total = calculate_cart_summary(request)

            # Create customer profile if it doesn't exist
            customer = Customer.objects.filter(user=request.user).first()

            # Create a new order and link it to the payment record
            order = Order.objects.create(
                order_no=uuid.uuid4(),
                customer=customer,
                payment=payment,
                subtotal=subtotal,
                tax=vat,
                total=total,
                stripe_payment_intent_id=request.GET.get("payment_intent"),
                is_paid=True,
                paid_at=timezone.now(),
                shipping_address=f"{payment.address}, {payment.city}, {payment.state}, {payment.postal_code}, {payment.country}",
                status="processing",
            )

            # Add cart items to the order
            try:
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
            except Exception as e:
                logger.error(f"Error creating order items: {str(e)}")

            # Mark the payment as associated with an order
            payment.paid_order = True
            payment.save()

            # Clear the cart after order creation
            cart_items.delete()
            request.session.pop('buy_now_product_id', None)
            request.session.pop('buy_now_quantity', None)

            messages.success(request, "Payment successful! Order has been created.")
            return render(request, "order_completed.html", {"order": order})

        except Exception as e:
            logger.error(f"CompletedPaymentView error: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("cart")

from django.core.paginator import Paginator

class OrderHistory(View):
    def get(self, request):
        user = request.user
        try:
            orders = Order.objects.filter(customer__user=user).order_by('-created_at')  # Filter by user and sort by latest orders

            paginator = Paginator(orders, 3)  # Show 3 orders per page
            page_number = request.GET.get('page')  # Get the current page number from query parameters
            page_obj = paginator.get_page(page_number)  # Get the paginated objects

            if not orders.exists():
                messages.info(request, "No order history found.")

            return render(request, 'account/account-orders.html', {"page_obj": page_obj})

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'account/account-orders.html', {"page_obj": None})

class OrderDetail(View):
    def get(self, request, order_id):
        user = request.user
        try:
            order = get_object_or_404(Order, id=order_id)
            order_items = order.order_items.all()  # Fetch related OrderItems

            if not order:
                messages.info(request, "No order found.")
                return render(request, 'account/account-order-detail.html', {"order": order, "order_items": []})

            return render(request, 'account/account-order-detail.html', {"order": order, "order_items": order_items})

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'account/account-order-detail.html', {"order": None, "order_items": []})



class UpdateProfile(View):
    def put(self, request):
        try:
            user = request.user

            # Update user's first name, last name, and email if provided in the request data
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            email = request.data.get('email', user.email)

            # Validate email format here if necessary
            user.email = email

            # Save the updated user information
            user.save()

            # Return a success response
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Guest email collection endpoint (disabled)
@require_POST
def collect_email(request):
    """Guest email collection disabled. Site requires authenticated users for shopping."""
    logger.info("collect_email called but guest flow is disabled; enforce login.")
    return JsonResponse({
        'success': False,
        'error': 'Guest checkout is disabled. Please sign up or log in to continue.',
        'requires_login': True,
        'redirect_url': reverse('login')
    }, status=403)

def save_guest_email(request):
    """Guest email saving disabled. Require authentication."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
    return JsonResponse({
        'success': False,
        'error': 'Guest checkout is disabled. Please sign up or log in to continue.',
        'requires_login': True,
        'redirect_url': reverse('login')
    }, status=403)


def check_email_status(request):
    """Email status endpoint for backward compatibility; always requires login now."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
    return JsonResponse({
        'success': False,
        'error': 'Guest email flow disabled. Please authenticate to proceed.',
        'requires_login': True,
        'redirect_url': reverse('login')
    }, status=403)


@login_required
def check_stock_availability(request, product_id):
    """Return JSON indicating whether the requested quantity of a product is available.

    - Requires authenticated users (login_required decorator).
    - Accepts optional `quantity` GET param (defaults to 1).
    - Returns stock_quantity, min/max purchase limits and a message.
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        # parse quantity from query params, default to 1
        try:
            qty = int(request.GET.get('quantity', 1))
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)

        if qty < 1:
            qty = 1

        stock_qty = getattr(product, 'stock_quantity', None)
        max_purchase = getattr(product, 'max_purchase', None)
        min_purchase = getattr(product, 'min_purchase', None)

        available = True
        reasons = []
        if stock_qty is not None and qty > stock_qty:
            available = False
            reasons.append(f'Only {stock_qty} items left in stock')
        if max_purchase is not None and qty > max_purchase:
            available = False
            reasons.append(f'Maximum {max_purchase} items allowed per order')
        if min_purchase is not None and qty < min_purchase:
            available = False
            reasons.append(f'Minimum {min_purchase} items required')

        message = 'Available' if available else '; '.join(reasons) or 'Unavailable'

        return JsonResponse({
            'success': True,
            'available': available,
            'requested_quantity': qty,
            'stock_quantity': stock_qty,
            'max_purchase': max_purchase,
            'min_purchase': min_purchase,
            'message': message,
        })

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
    except Exception as e:
        logger.error(f"check_stock_availability error: {e}")
        return JsonResponse({'success': False, 'error': 'Error checking stock'}, status=500)

@login_required
def populate_db(request):
    """
    Safe populate DB endpoint used during development.
    Only accessible to staff users. To execute, visit ?run=1
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied. Staff only.'}, status=403)

    if request.GET.get('run') != '1':
        return JsonResponse({'success': True, 'message': "populate_db available. Append ?run=1 to create sample records."})

    try:
        # create minimal sample records if they don't exist
        svc, _ = Service.objects.get_or_create(name='Default Service', defaults={'slug': 'default-service'})
        cat, _ = Category.objects.get_or_create(name='Default Category', defaults={'slug': 'default-category', 'service': svc})
        Product.objects.get_or_create(name='Sample Product', defaults={
            'price': Decimal('9.99'),
            'available': True,
            'category': cat,
        })
        return JsonResponse({'success': True, 'message': 'Sample data created.'})
    except Exception as e:
        logger.error(f"populate_db error: {e}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def get_cart_items(request):
    """Return JSON list of current user's cart items and cart summary."""
    try:
        cart_items = ShopCart.objects.filter(user=request.user, paid_order=False, quantity__gt=0)
        items = []
        for ci in cart_items.select_related('product'):
            product = ci.product
            items.append({
                'cart_item_id': ci.id,
                'product_id': product.id if product else None,
                'name': product.name if product else '',
                'quantity': ci.quantity,
                'unit_price': float(product.price) if product and product.price is not None else 0.0,
                'total_price': float((product.price * ci.quantity) if product and product.price is not None else 0.0),
                'image_url': product.image.url if product and getattr(product, 'image', None) else '',
                'url': reverse('product', args=[product.id]) if product else '',
            })

        subtotal = sum((ci.product.price * ci.quantity) for ci in cart_items) if cart_items.exists() else Decimal('0.0')
        if not isinstance(subtotal, Decimal):
            subtotal = Decimal(str(subtotal))
        vat = subtotal * Decimal('0.075')
        total = subtotal + vat
        count = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

        return JsonResponse({
            'success': True,
            'items': items,
            'subtotal': round(float(subtotal), 2),
            'vat': round(float(vat), 2),
            'total': round(float(total), 2),
            'count': count,
        })
    except Exception as e:
        logger.error(f"get_cart_items error: {e}")
        return JsonResponse({'success': False, 'message': 'Failed to retrieve cart items.'}, status=500)

@csrf_exempt
def stripe_webhook(request):
    """Receive Stripe webhooks, verify signature, and process important events.
    Expects STRIPE_WEBHOOK_SECRET in settings for signature verification.
    This handler is idempotent: it will skip processing if payment record already marked paid.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    # Verify webhook signature if secret is configured
    try:
        if getattr(settings, 'STRIPE_WEBHOOK_SECRET', None):
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        else:
            # If webhook secret not configured, parse without verification (not recommended for production)
            event = stripe.Event.construct_from(json.loads(payload.decode('utf-8')), stripe.api_key)
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid Stripe payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Stripe signature verification failed: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.exception(f"Unexpected error verifying Stripe webhook: {e}")
        return HttpResponse(status=400)

    try:
        event_type = event['type']
        data = event['data']['object']

        # Helper to send receipt email
        def send_receipt_email(payment, order=None):
            try:
                subject = f"Your order {payment.basket_no} receipt"
                context = {'payment': payment, 'order': order}
                message = render_to_string('emails/payment_receipt.txt', context)
                html_message = render_to_string('emails/payment_receipt.html', context) if True else None
                # send_mail returns number of emails sent
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [payment.email or (payment.user.email if payment.user else None)], html_message=html_message, fail_silently=True)
            except Exception:
                logger.exception('Failed to send receipt email')

        # Handle checkout.session.completed
        if event_type == 'checkout.session.completed':
            session = data
            metadata = session.get('metadata') or {}
            payment_id = metadata.get('payment_id')
            session_id = session.get('id')
            payment_intent = session.get('payment_intent')

            payment = None
            if payment_id:
                try:
                    payment = PaymentInfo.objects.filter(id=payment_id).first()
                except Exception:
                    payment = None

            # Fallback: try by stripe_session_id
            if not payment and session_id:
                payment = PaymentInfo.objects.filter(stripe_payment_intent_id=session_id).first()

            # If still not found, try by basket_no metadata
            if not payment and metadata.get('basket_no'):
                payment = PaymentInfo.objects.filter(basket_no=metadata.get('basket_no')).order_by('-created_at').first()

            if not payment:
                logger.warning('Stripe webhook: payment record not found for session %s', session_id)
                return HttpResponse(status=200)

            # Idempotency: if already processed, skip
            if payment.paid_order:
                logger.info('Stripe webhook: payment already processed for PaymentInfo id=%s', payment.id)
                return HttpResponse(status=200)

            # Update payment with intent/session ids
            try:
                payment.stripe_payment_intent_id = payment_intent or session_id
                payment.save()
            except Exception:
                logger.exception('Failed to save stripe ids on payment')

            # Create Order if not exists
            try:
                existing_order = Order.objects.filter(payment=payment).first()
                if existing_order:
                    order = existing_order
                else:
                    # Build customer
                    customer = None
                    if payment.user:
                        customer = Customer.objects.filter(user=payment.user).first()
                    else:
                        customer, _ = Customer.objects.get_or_create(email=payment.email, defaults={'first_name': payment.first_name or '', 'last_name': payment.last_name or '', 'is_guest': True})

                    # Create order
                    order = Order.objects.create(
                        customer=customer,
                        payment=payment,
                        subtotal=0,
                        shipping_cost=0,
                        tax=0,
                        discount=0,
                        total=payment.amount or 0,
                        stripe_payment_intent_id=payment.stripe_payment_intent_id,
                        is_paid=True,
                        paid_at=timezone.now(),
                        status='processing',
                    )

                    # Move cart items into order items
                    cart_items = ShopCart.objects.filter(user=payment.user, paid_order=False)
                    for item in cart_items:
                        try:
                            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
                        except Exception:
                            logger.exception('Failed to create order item')

                    # Mark carts as paid and delete them
                    cart_items.delete()

            except Exception:
                logger.exception('Failed to create order from payment')

            # Mark payment as paid
            try:
                payment.paid_order = True
                payment.save()
            except Exception:
                logger.exception('Failed to mark payment as paid')

            # Send receipt email (best effort)
            try:
                send_receipt_email(payment, order)
            except Exception:
                logger.exception('Failed sending receipt')

            return HttpResponse(status=200)

        # Handle payment_intent.succeeded
        if event_type == 'payment_intent.succeeded':
            intent = data
            intent_id = intent.get('id')
            # Find matching payment by stripe_payment_intent_id
            payment = PaymentInfo.objects.filter(stripe_payment_intent_id=intent_id).first()
            if payment and not payment.paid_order:
                try:
                    payment.paid_order = True
                    payment.save()
                    # create order if needed (similar to above)
                    existing_order = Order.objects.filter(payment=payment).first()
                    if not existing_order:
                        customer = Customer.objects.filter(user=payment.user).first() if payment.user else Customer.objects.filter(email=payment.email).first()
                        order = Order.objects.create(
                            customer=customer,
                            payment=payment,
                            total=payment.amount or 0,
                            stripe_payment_intent_id=intent_id,
                            is_paid=True,
                            paid_at=timezone.now(),
                            status='processing'
                        )
                        cart_items = ShopCart.objects.filter(user=payment.user, paid_order=False)
                        for item in cart_items:
                            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
                        cart_items.delete()
                    send_receipt_email(payment, existing_order if existing_order else order)
                except Exception:
                    logger.exception('Error processing payment_intent.succeeded')
            return HttpResponse(status=200)

        # Handle failed payments
        if event_type == 'payment_intent.payment_failed':
            intent = data
            intent_id = intent.get('id')
            payment = PaymentInfo.objects.filter(stripe_payment_intent_id=intent_id).first()
            if payment:
                try:
                    payment.paid_order = False
                    payment.save()
                    # Optionally notify user by email
                except Exception:
                    logger.exception('Error marking payment failed')
            return HttpResponse(status=200)

    except Exception as e:
        logger.exception(f"Error processing Stripe webhook: {e}")
        return HttpResponse(status=500)

    return HttpResponse(status=200)
