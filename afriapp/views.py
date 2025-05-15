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
from django.db import IntegrityError, transaction
from django.db.models import Sum, F, FloatField, Q, Count
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.utils import timezone
from django.urls import reverse

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

# Logging configuration
logger = logging.getLogger(__name__)

# Set Stripe API key with error handling
try:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if not stripe.api_key:
        logger.error("Stripe API key is not set or empty")
except Exception as e:
    logger.error(f"Error setting Stripe API key: {e}")

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
        return render(request, 'signup.html')

    def post(self, request):
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate form inputs
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        # Check if user already exists - handle this gracefully with a message
        if User.objects.filter(username=email).exists():
            messages.warning(request, 'An account with that email already exists. Please log in instead.')
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
            return redirect('index')

        except Exception as e:
            logger.error(f"Signup failed: {e}")
            messages.error(request, 'An unexpected error occurred during signup. Please try again later.')
            return render(request, 'signup.html')


# 18. Login View with Error Handling
class LoginPageView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # change email to password every other thing still remains the same
        user = authenticate(request, username=username, password=password)  # Email is treated as username

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('index')
        else:
            messages.error(request, 'Email/password incorrect')
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
        # Use DRF's get_object_or_404 to fetch the product or raise a 404 error
        product = get_object_or_404(Product, pk=id)
        # Return a response with the context data
        return render(request, 'product.html', {'product': product})



# Save guest email to session and database
def save_guest_email(request):
    """
    Save guest email to session and create a Customer record if needed.
    This function handles email collection for guest users and ensures
    they only need to provide their email once per session.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        subscribe = request.POST.get('subscribe') == 'true'

        if not email:
            return JsonResponse({'success': False, 'message': 'No email provided'})

        # Store email in session (this ensures it's available across the site)
        request.session['guest_email'] = email
        request.session['email_collected'] = True  # Flag to indicate email has been collected
        request.session.modified = True  # Ensure session is saved

        # Log the email collection
        logger.info(f"Email collected: {email}, Subscribe: {subscribe}")

        # Check if we need to create a guest customer
        try:
            # Try to get existing customer with this email
            guest_customer = Customer.objects.filter(email=email).first()

            if not guest_customer:
                # Extract name from email (if possible)
                email_name = email.split('@')[0]
                # Capitalize and split by common separators
                name_parts = email_name.replace('.', ' ').replace('_', ' ').replace('-', ' ').title().split()

                # Set default first and last name
                first_name = "Customer"
                last_name = ""

                # If we have name parts, use them
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                elif len(name_parts) == 1:
                    first_name = name_parts[0]

                try:
                    # Create a new guest customer with better naming
                    guest_customer = Customer.objects.create(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        is_guest=True,
                        phone_number="",  # Empty string as placeholder
                        date_joined=timezone.now()
                    )
                    logger.info(f"Created new guest customer with email: {email}")

                    # Store customer ID in session for future reference
                    request.session['guest_customer_id'] = guest_customer.id
                    request.session.modified = True

                except IntegrityError:
                    # Handle duplicate email error gracefully
                    logger.info(f"Email already exists: {email}")

                    # Get the existing customer
                    guest_customer = Customer.objects.filter(email=email).first()

                    if guest_customer:
                        # Store customer ID in session
                        request.session['guest_customer_id'] = guest_customer.id
                        request.session.modified = True

                        # Check if this is a registered user's email
                        if not guest_customer.is_guest and guest_customer.user:
                            return JsonResponse({
                                'success': True,
                                'message': 'This email is already registered. Would you like to log in?',
                                'registered': True,
                                'customer_id': str(guest_customer.id)
                            })
            elif guest_customer.is_guest:
                # Update last activity for existing guest customer
                guest_customer.date_joined = timezone.now()
                guest_customer.save()
                logger.info(f"Updated existing guest customer with email: {email}")

                # Store customer ID in session
                request.session['guest_customer_id'] = guest_customer.id
                request.session.modified = True
            else:
                # This is a registered user's email
                if guest_customer.user:
                    return JsonResponse({
                        'success': True,
                        'message': 'This email is already registered. Would you like to log in?',
                        'registered': True,
                        'customer_id': str(guest_customer.id)
                    })

            # If subscribe is checked, add to newsletter subscribers
            if subscribe:
                # Add to newsletter subscribers
                try:
                    newsletter, created = Newsletter.objects.get_or_create(
                        email=email,
                        defaults={'subscribed_at': timezone.now()}
                    )
                    if created:
                        logger.info(f"Added {email} to newsletter subscribers")
                    else:
                        logger.info(f"Email {email} already subscribed to newsletter")
                except Exception as newsletter_error:
                    logger.error(f"Error adding to newsletter: {str(newsletter_error)}")

            # Return success response with customer ID if available
            if guest_customer:
                return JsonResponse({
                    'success': True,
                    'message': 'Email saved successfully',
                    'customer_id': str(guest_customer.id)
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Email saved to session successfully'
                })
        except Exception as e:
            logger.error(f"Error processing guest email: {str(e)}")
            # Still return success since we saved the email to session
            return JsonResponse({
                'success': True,
                'message': 'Email saved to session successfully',
                'warning': 'There was an issue creating your customer profile, but you can continue shopping.'
            })
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# 9. Add to Wishlist
def add_to_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        # Get email if provided (for guest users)
        guest_email = request.POST.get('email')

        if request.user.is_authenticated:
            # For authenticated users
            try:
                wishlist, created = Wishlist.objects.get_or_create(user=request.user)
                wishlist.add_product(product)
                return JsonResponse({'success': True, 'message': 'Product added to wishlist'})
            except Exception as e:
                logger.error(f"Error adding to wishlist for authenticated user: {str(e)}")
                return JsonResponse({'success': False, 'message': 'Error adding to wishlist. Please try again.'})
        elif guest_email:
            # For guest users with email
            try:
                # Store email in session
                request.session['guest_email'] = guest_email

                # Check if we need to create a guest customer
                guest_customer = Customer.objects.filter(email=guest_email).first()

                if not guest_customer:
                    # Extract name from email (if possible)
                    email_name = guest_email.split('@')[0]
                    # Capitalize and split by common separators
                    name_parts = email_name.replace('.', ' ').replace('_', ' ').replace('-', ' ').title().split()

                    # Set default first and last name
                    first_name = "Customer"
                    last_name = ""

                    # If we have name parts, use them
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = ' '.join(name_parts[1:])
                    elif len(name_parts) == 1:
                        first_name = name_parts[0]

                    try:
                        # Create a new guest customer with better naming
                        guest_customer = Customer.objects.create(
                            email=guest_email,
                            first_name=first_name,
                            last_name=last_name,
                            is_guest=True,
                            phone_number="",  # Empty string as placeholder
                            date_joined=timezone.now()
                        )
                        logger.info(f"Created new guest customer with email: {guest_email}")
                    except IntegrityError:
                        # Handle duplicate email error gracefully
                        messages.warning(request, "This email is already registered in our system.")
                        # Try to get the customer again (it must exist if we got an integrity error)
                        guest_customer = Customer.objects.filter(email=guest_email).first()
                        logger.info(f"Attempted to create duplicate customer with email: {guest_email}")
                elif guest_customer.is_guest:
                    # Update last activity for existing guest customer
                    guest_customer.date_joined = timezone.now()
                    guest_customer.save()
                    logger.info(f"Updated existing guest customer with email: {guest_email}")

                # Create a wishlist entry for this guest
                try:
                    # Check if this product is already in the wishlist for this email
                    existing_wishlist = Wishlist.objects.filter(
                        guest_email=guest_email,
                        product=product
                    ).first()

                    if existing_wishlist:
                        return JsonResponse({'success': True, 'message': 'Product is already in your wishlist'})

                    # Create new wishlist entry
                    if guest_customer:
                        # If we have a customer record, associate the wishlist with it
                        Wishlist.objects.create(
                            customer=guest_customer,
                            product=product,
                            guest_email=guest_email
                        )
                    else:
                        # Fallback to just using the email
                        Wishlist.objects.create(
                            user=None,  # No user for guests
                            product=product,
                            guest_email=guest_email
                        )

                    return JsonResponse({'success': True, 'message': 'Product added to wishlist'})
                except Exception as wishlist_error:
                    logger.error(f"Error creating wishlist entry: {str(wishlist_error)}")
                    return JsonResponse({'success': False, 'message': 'Error adding to wishlist. Please try again.'})
            except Exception as e:
                logger.error(f"Error adding to wishlist for guest: {str(e)}")
                return JsonResponse({'success': False, 'message': 'Error adding to wishlist. Please try again.'})
        else:
            # No email provided and not logged in
            return JsonResponse({'success': False, 'message': 'Please provide an email or log in to add to wishlist'})


# 11. Add to Cart

# ============================================================================

# Get cart items for JavaScript to check which items are already in cart
def get_cart_items(request):
    # Use session key for non-authenticated users
    session_key = request.session.session_key
    if not session_key:
        request.session.save()  # Create a session if not already present
        session_key = request.session.session_key

    # Get cart items based on user authentication status
    if request.user.is_authenticated:
        cart_items = ShopCart.objects.filter(user=request.user, paid_order=False)
    else:
        cart_items = ShopCart.objects.filter(session_key=session_key, paid_order=False)

    # Format the response
    items = []
    for item in cart_items:
        items.append({
            'product_id': item.product.id,
            'quantity': item.quantity,
            'name': item.product.name,
            'price': float(item.product.price),
            'total': float(item.calculate_total_price())
        })

    return JsonResponse({
        'success': True,
        'cart_items': items,
        'cart_count': len(items)
    })

# This view handles adding products to the cart for both logged-in and non-logged-in users
def add_to_cart(request, product_id):
    """
    Add a product to the cart for both authenticated and guest users.
    This function handles the cart creation process and ensures proper
    association with either a User or a Customer record.
    """
    product = get_object_or_404(Product, id=product_id)

    # Use session key for non-authenticated users
    session_key = request.session.session_key
    if not session_key:
        request.session.save()  # Create a session if not already present
        session_key = request.session.session_key

    # Generate a unique basket number if not already in session
    if 'basket_no' not in request.session:
        request.session['basket_no'] = get_random_string(20)
    basket_no = request.session['basket_no']

    # Handle POST request for adding to cart
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))

            # Get email if provided (for guest users)
            guest_email = request.POST.get('email') or request.session.get('guest_email')

            # Store email in session if provided
            if guest_email and not request.user.is_authenticated:
                request.session['guest_email'] = guest_email
                request.session['email_collected'] = True
                request.session.modified = True

            # Get or create guest customer if email is provided
            guest_customer = None
            if guest_email and not request.user.is_authenticated:
                try:
                    # Try to get existing customer with this email
                    guest_customer = Customer.objects.filter(email=guest_email).first()

                    # If no customer exists, create one
                    if not guest_customer:
                        # Extract name from email (if possible)
                        email_name = guest_email.split('@')[0]
                        # Capitalize and split by common separators
                        name_parts = email_name.replace('.', ' ').replace('_', ' ').replace('-', ' ').title().split()

                        # Set default first and last name
                        first_name = "Customer"
                        last_name = ""

                        # If we have name parts, use them
                        if len(name_parts) >= 2:
                            first_name = name_parts[0]
                            last_name = ' '.join(name_parts[1:])
                        elif len(name_parts) == 1:
                            first_name = name_parts[0]

                        # Create the customer
                        guest_customer = Customer.objects.create(
                            email=guest_email,
                            first_name=first_name,
                            last_name=last_name,
                            is_guest=True,
                            date_joined=timezone.now()
                        )
                        logger.info(f"Created new guest customer with email: {guest_email}")

                        # Store customer ID in session
                        request.session['guest_customer_id'] = guest_customer.id
                        request.session.modified = True
                    elif guest_customer.is_guest:
                        # Update last activity for existing guest customer
                        guest_customer.date_joined = timezone.now()
                        guest_customer.save()

                        # Store customer ID in session
                        request.session['guest_customer_id'] = guest_customer.id
                        request.session.modified = True
                except Exception as e:
                    logger.error(f"Error processing guest customer: {str(e)}")
                    # Continue without a customer - we'll handle this in the cart creation

            # Check if the product is already in the cart
            cart_item = None
            if request.user.is_authenticated:
                cart_item = ShopCart.objects.filter(
                    user=request.user,
                    product=product,
                    paid_order=False
                ).first()
            else:
                # Try to find cart item by session key
                cart_item = ShopCart.objects.filter(
                    session_key=session_key,
                    product=product,
                    paid_order=False
                ).first()

                # If guest customer exists, also check by customer
                if not cart_item and guest_customer:
                    cart_item = ShopCart.objects.filter(
                        customer=guest_customer,
                        product=product,
                        paid_order=False
                    ).first()

            # Update or create the cart item
            if cart_item:
                # Update quantity if the product is already in the cart
                if cart_item.quantity == quantity:
                    message = 'Product was already added to the cart!'
                else:
                    cart_item.quantity = quantity
                    cart_item.save()
                    message = 'Quantity updated successfully!'
            else:
                # Create a new cart item
                if request.user.is_authenticated:
                    # For authenticated users
                    try:
                        ShopCart.objects.create(
                            user=request.user,
                            product=product,
                            quantity=quantity,
                            paid_order=False,
                            basket_no=basket_no
                        )
                        message = 'Product added to cart successfully!'
                    except Exception as auth_e:
                        logger.error(f"Error creating cart for authenticated user: {str(auth_e)}")
                        return JsonResponse({
                            'success': False,
                            'message': 'Unable to add item to cart. Please try again later.',
                            'error': 'Database error'
                        }, status=500)
                else:
                    # For guest users
                    success = False

                    # First try: Create cart with customer if available
                    if guest_customer:
                        try:
                            ShopCart.objects.create(
                                user=None,
                                customer=guest_customer,
                                session_key=session_key,
                                product=product,
                                quantity=quantity,
                                paid_order=False,
                                basket_no=basket_no
                            )
                            success = True
                            message = 'Product added to cart successfully!'
                            logger.info(f"Added product to cart with customer: {guest_customer.email}")
                        except Exception as e:
                            logger.error(f"Error creating cart with customer: {str(e)}")

                    # Second try: Create cart with session key only
                    if not success:
                        try:
                            ShopCart.objects.create(
                                user=None,
                                session_key=session_key,
                                product=product,
                                quantity=quantity,
                                paid_order=False,
                                basket_no=basket_no
                            )
                            success = True
                            message = 'Product added to cart successfully!'
                            logger.info("Added product to cart with session key only")
                        except Exception as e:
                            logger.error(f"Error creating cart with session key: {str(e)}")

                    # Last resort: Try with direct SQL
                    if not success:
                        try:
                            from django.db import connection
                            with connection.cursor() as cursor:
                                now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                                cursor.execute("""
                                    INSERT INTO afriapp_shopcart
                                    (product_id, session_key, quantity, paid_order, basket_no, date_added, last_updated)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, [product.id, session_key, quantity, False, basket_no, now, now])
                            success = True
                            message = 'Product added to cart successfully!'
                            logger.info("Added product to cart using direct SQL")
                        except Exception as e:
                            logger.error(f"Error creating cart with SQL: {str(e)}")

                    # If all approaches failed, return an error
                    if not success:
                        return JsonResponse({
                            'success': False,
                            'message': 'Unable to add item to cart. Please try again later.',
                            'error': 'All approaches failed'
                        }, status=500)

            # Calculate the total number of items in the cart
            try:
                if request.user.is_authenticated:
                    cart_count = ShopCart.objects.filter(
                        user=request.user,
                        paid_order=False
                    ).count()
                else:
                    # Count items by session key
                    cart_count = ShopCart.objects.filter(
                        session_key=session_key,
                        paid_order=False
                    ).count()

                    # If guest customer exists, also count items by customer
                    if guest_customer:
                        customer_cart_count = ShopCart.objects.filter(
                            customer=guest_customer,
                            paid_order=False
                        ).count()

                        # Use the larger count (to avoid missing items)
                        cart_count = max(cart_count, customer_cart_count)
            except Exception as count_error:
                logger.error(f"Error counting cart items: {str(count_error)}")
                cart_count = 0  # Default to 0 if there's an error

            # Store cart count in session for easy access
            request.session['cart_count'] = cart_count
            request.session.modified = True

            # If the request was an AJAX request, return a JSON response
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'cart_count': cart_count
                })

            # For normal form submissions, redirect to the cart page
            return redirect('cart')

        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error adding to cart: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while adding the product to cart. Please try again.',
                'error': str(e)
            }, status=500)

    # Handle invalid request methods (e.g., if someone tried to use GET)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# 12. Cart View
class CartView(View):
    def get(self, request):
        """
        Display the cart page with all items for both authenticated and guest users.
        For guest users, combines items from both session and customer record if available.
        """
        # Get cart items based on user authentication status
        if request.user.is_authenticated:
            # For authenticated users, get cart by user
            cart = ShopCart.objects.filter(user=request.user, paid_order=False)

            # Check if there are any guest items to merge
            session_key = request.session.session_key
            if session_key:
                # Find any items in the session that aren't associated with the user
                guest_items = ShopCart.objects.filter(
                    user=None,
                    session_key=session_key,
                    paid_order=False
                )

                # Transfer guest items to the user's account
                for item in guest_items:
                    # Check if this product is already in the user's cart
                    existing_item = cart.filter(product=item.product).first()

                    if existing_item:
                        # Update quantity if the product already exists
                        existing_item.quantity += item.quantity
                        existing_item.save()
                        # Delete the guest item
                        item.delete()
                    else:
                        # Transfer ownership to the user
                        item.user = request.user
                        item.customer = None  # Clear any guest customer association
                        item.save()

                # Refresh the cart queryset after merging
                cart = ShopCart.objects.filter(user=request.user, paid_order=False)
        else:
            # For guest users, we need to check both session and customer
            session_key = request.session.session_key
            if not session_key:
                session_key = request.session.create()

            # Start with session-based cart items
            cart = ShopCart.objects.filter(user=None, session_key=session_key, paid_order=False)

            # Check if we have a guest customer ID in the session
            guest_customer_id = request.session.get('guest_customer_id')
            if guest_customer_id:
                try:
                    # Get the customer
                    guest_customer = Customer.objects.get(id=guest_customer_id)

                    # Get customer-based cart items
                    customer_cart = ShopCart.objects.filter(
                        customer=guest_customer,
                        paid_order=False
                    )

                    # Merge the two querysets if needed
                    if customer_cart.exists():
                        # Use a set to track products we've already seen
                        seen_products = set(item.product_id for item in cart)

                        # Add customer items that aren't already in the session cart
                        for item in customer_cart:
                            if item.product_id not in seen_products:
                                cart = cart | ShopCart.objects.filter(id=item.id)
                            else:
                                # If the product is already in the cart, we should merge quantities
                                session_item = cart.get(product_id=item.product_id)
                                session_item.quantity += item.quantity
                                session_item.save()
                                # Delete the duplicate customer item
                                item.delete()
                except Customer.DoesNotExist:
                    # If the customer doesn't exist, remove the ID from session
                    del request.session['guest_customer_id']
                    request.session.modified = True
                except Exception as e:
                    logger.error(f"Error merging guest carts: {str(e)}")

        # Calculate total price for each cart item
        for item in cart:
            item.total_price = item.calculate_total_price()

        # Calculate cart summary
        cartreader = sum(item.quantity for item in cart)
        subtotal = sum(item.calculate_total_price() for item in cart)

        # Calculate VAT and total price - convert to Decimal to avoid type mismatch
        from decimal import Decimal
        # Convert subtotal to Decimal if it's not already
        if not isinstance(subtotal, Decimal):
            subtotal = Decimal(str(subtotal))

        vat = Decimal('0.075') * subtotal
        total = subtotal + vat

        # Update cart count in session
        request.session['cart_count'] = cart.count()
        request.session.modified = True

        # Prepare the context for the template
        context = {
            'cart': cart,
            'cartreader': cartreader,
            'subtotal': round(float(subtotal), 2),
            'vat': round(float(vat), 2),
            'total': round(float(total), 2),
        }

        return render(request, 'cart.html', context)

# ============================================================================
def increase_quantity(request, item_id):
    if request.method == 'POST':
        try:
            # Get cart item based on user authentication status
            if request.user.is_authenticated:
                cart_item = get_object_or_404(ShopCart, id=item_id, user=request.user)
            else:
                session_key = request.session.session_key
                cart_item = get_object_or_404(ShopCart, id=item_id, session_key=session_key, user=None)

            # Increase quantity by exactly 1
            cart_item.quantity += 1
            cart_item.save()

            # Calculate updated values
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
            return JsonResponse({
                'success': False,
                'message': 'Failed to increase quantity. Please try again.'
            }, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def decrease_quantity(request, item_id):
    if request.method == 'POST':
        try:
            # Get cart item based on user authentication status
            if request.user.is_authenticated:
                cart_item = get_object_or_404(ShopCart, id=item_id, user=request.user)
            else:
                session_key = request.session.session_key
                cart_item = get_object_or_404(ShopCart, id=item_id, session_key=session_key, user=None)

            # Only decrease if quantity is greater than 1
            if cart_item.quantity > 1:
                # Decrease quantity by exactly 1
                cart_item.quantity -= 1
                cart_item.save()
            else:
                # If quantity is already 1, don't decrease but don't return an error
                logger.info(f"Attempted to decrease quantity below 1 for cart item {item_id}")

            # Calculate updated values
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
            return JsonResponse({
                'success': False,
                'message': 'Failed to decrease quantity. Please try again.'
            }, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def calculate_cart_summary(request):
    """Calculate the cart summary for the given request (authenticated or guest)."""
    if request.user.is_authenticated:
        cart_items = ShopCart.objects.filter(user=request.user, paid_order=False)
    else:
        session_key = request.session.session_key
        if not session_key:
            session_key = request.session.create()
        cart_items = ShopCart.objects.filter(user=None, session_key=session_key, paid_order=False)

    # Calculate subtotal using aggregate, ensure it's handled as Decimal
    subtotal = cart_items.aggregate(
        subtotal=Sum(F('product__price') * F('quantity'))
    )['subtotal'] or Decimal('0.0')  # Ensure this is a Decimal

    # Calculate VAT and total
    vat = subtotal * Decimal('0.075')  # Assuming a 7.5% VAT
    total = subtotal + vat

    # Convert Decimal values to float before returning
    return float(subtotal), float(vat), float(total)



def remove_from_cart(request, cart_item_id):
    if request.method == 'POST':
        try:
            # Get cart item based on user authentication status
            if request.user.is_authenticated:
                cart_item = get_object_or_404(ShopCart, id=cart_item_id, user=request.user)
            else:
                session_key = request.session.session_key
                cart_item = get_object_or_404(ShopCart, id=cart_item_id, session_key=session_key, user=None)

            cart_item.delete()

            # Check if it's an AJAX request
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                subtotal, vat, total = calculate_cart_summary(request)

                # Check if cart is empty based on user authentication status
                if request.user.is_authenticated:
                    cart_empty = not ShopCart.objects.filter(user=request.user, paid_order=False).exists()
                else:
                    cart_empty = not ShopCart.objects.filter(session_key=session_key, user=None, paid_order=False).exists()

                return JsonResponse({
                    'success': True,
                    'subtotal': subtotal,
                    'vat': vat,
                    'total': total,
                    'cart_empty': cart_empty  # Handle empty cart state
                })

            # Handle non-AJAX request
            return redirect(request.META.get('HTTP_REFERER', 'cart'))

        except ShopCart.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Cart item not found. Please refresh the page and try again.'
            }, status=404)

    return JsonResponse({'success': False, 'message': 'Invalid request method. Please use POST.'}, status=400)







def remove_from_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        wishlist = Wishlist.objects.get(user=request.user)
        wishlist.remove_product(product)

        return JsonResponse({'success': True, 'message': 'Product removed from wishlist'})

# ============================================================================

from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings
from .models import ShopCart, Customer

class CheckoutView(TemplateView):
    def get(self, request):
        # Get cart items based on user authentication status
        if request.user.is_authenticated:
            # For authenticated users, get cart by user
            cart = ShopCart.objects.filter(user=request.user, paid_order=False)
            customer = Customer.objects.filter(user=request.user).first()

            # Check if there are guest cart items in the session to transfer
            session_key = request.session.session_key
            if session_key:
                guest_cart = ShopCart.objects.filter(user=None, session_key=session_key, paid_order=False)
                if guest_cart.exists():
                    # Transfer guest cart items to the user's cart
                    for item in guest_cart:
                        # Check if the user already has this product in their cart
                        user_cart_item = ShopCart.objects.filter(
                            user=request.user,
                            product=item.product,
                            paid_order=False
                        ).first()

                        if user_cart_item:
                            # Update quantity if the product already exists in the user's cart
                            user_cart_item.quantity += item.quantity
                            user_cart_item.save()
                            item.delete()
                        else:
                            # Transfer the item to the user's cart
                            item.user = request.user
                            item.session_key = None
                            item.save()

                    # Refresh the cart queryset
                    cart = ShopCart.objects.filter(user=request.user, paid_order=False)
        else:
            # For guest users, get cart by session key
            session_key = request.session.session_key
            if not session_key:
                session_key = request.session.create()

            cart = ShopCart.objects.filter(user=None, session_key=session_key, paid_order=False)
            customer = None  # No customer for guest users

        # Check if there are no items in the cart
        if not cart.exists():
            messages.error(request, 'No items in the cart.')
            return redirect('cart')  # Redirect user if no cart items

        # Calculate total price of items in the cart
        total_price = sum(item.calculate_total_price() for item in cart)

        # Get basket number from the first item in the cart (assuming all items share the same basket number)
        basket_no = cart.first().basket_no if cart.exists() else None

        # Prepare the context for rendering the checkout page
        context = {
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            'cart': cart,
            'customer': customer,
            'total_price': total_price,  # Total price calculation for display
            'basket_no': basket_no,  # Pass basket number to context
            'is_guest': not request.user.is_authenticated,  # Flag to indicate if user is a guest
        }

        return render(request, 'checkout.html', context)
# ================================================================================================================================================================================================================
from django.utils.crypto import get_random_string
class PaymentPipelineView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Extract form data
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
            payment_method = request.POST.get('payment_method', 'credit_card')

            # Get email for guest users
            email = request.POST.get('email')

            # Fetch cart items based on user authentication status
            if request.user.is_authenticated:
                cart_items = ShopCart.objects.filter(user=request.user, paid_order=False)
                user = request.user
            else:
                # For guest users, get cart by session key
                session_key = request.session.session_key
                if not session_key:
                    session_key = request.session.create()

                cart_items = ShopCart.objects.filter(user=None, session_key=session_key, paid_order=False)

                # For guest users, check if email is provided
                if not email:
                    return JsonResponse({'error': 'Email is required for guest checkout.'}, status=400)

                # Create a temporary user for the guest
                user = None

            if not cart_items.exists():
                return JsonResponse({'error': 'No items in cart.'}, status=404)

            # Calculate total amount
            total_price_with_shipping = sum(item.product.price * item.quantity for item in cart_items)
            total_amount = int(float(total_price_with_shipping) * 100)  # Convert to cents for Stripe

            # Debugging log
            print("Creating Stripe session...")
            # Generate unique pay_code and transaction_id
            pay_code = get_random_string(12)
            transaction_id = get_random_string(20)

            # Create payment info
            payment = PaymentInfo.objects.create(
                user=user,  # Can be None for guest users
                amount=total_amount,
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
                email=email if not user else user.email,  # Store email for guest users
            )

            print("Payment", payment)

            # Create Stripe Checkout session
            YOUR_DOMAIN = "http://127.0.0.1:8000"  # Update to your actual domain
            line_items = []

            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,  # Customize product name
                        },
                        'unit_amount': int(item.product.price * 100),  # Price in cents
                    },
                    'quantity': item.quantity,  # Use the quantity from the cart
                })

            # Store session key in metadata for guest users
            metadata = {"basket_no": basket_no}
            if not request.user.is_authenticated:
                metadata["session_key"] = session_key
                metadata["guest_email"] = email

            # Using f-strings for URL formatting
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                metadata=metadata,
                mode='payment',
                success_url=f'{YOUR_DOMAIN}/successpayment/',
                cancel_url=f'{YOUR_DOMAIN}/cancelpayment/',
            )

            # Update payment intent ID
            payment.stripe_payment_intent_id = checkout_session.payment_intent
            payment.save()

            # Redirect the user to Stripe Checkout
            return redirect(checkout_session.url)

        except Exception as e:
            print("Error creating checkout session:", str(e))
            # return redirect("cart")
            return JsonResponse({'error': str(e)}, status=500)
# ================================================================================================================================================================================================================


class WhatsappPaymentView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Extract form data
            basket_no = request.POST.get('basket_no')
            shipping_option = request.POST.get('shipping_option')

            # Fetch the user's cart
            cart_items = ShopCart.objects.filter(user=request.user, paid_order=False)

            if not cart_items.exists():
                return JsonResponse({'error': 'No items in cart.'}, status=404)

            # Calculate total amount
            total_price_with_shipping = sum(item.product.price * item.quantity for item in cart_items)
            total_amount = int(float(total_price_with_shipping) * 100)  # Convert to cents for Stripe

            # Debugging log
            print("Creating Stripe session...")


            # Create Stripe Checkout session
            YOUR_DOMAIN = "http://127.0.0.1:8000"  # Update to your actual domain
            line_items = []

            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,  # Customize product name
                        },
                        'unit_amount': int(item.product.price * 100),  # Price in cents
                    },
                    'quantity': item.quantity,  # Use the quantity from the cart
                })

            # Using f-strings for URL formatting
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,  # Add line items for each product in the cart
                metadata={"basket_no": basket_no},  # You can include basket_no in metadata
                mode='payment',
                success_url=f'{YOUR_DOMAIN}/successpayment/',  # Redirection after successful payment
                cancel_url=f'{YOUR_DOMAIN}/cancelpayment/',  # Redirection after cancellation
            )

            # Return the session ID as a JSON response
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            print("Error creating checkout session:", str(e))
            return JsonResponse({'error': str(e)}, status=500)


# ================================================================================================================================================================================================================
import uuid
class CompletedPaymentView(View):
    def get(self, request):
        try:
            # Check if user is authenticated
            if request.user.is_authenticated:
                # Get the latest payment info for the authenticated user
                payment = PaymentInfo.objects.filter(user=request.user, paid_order=False).order_by('-created_at').first()

                # Fetch cart items for authenticated user
                cart_items = ShopCart.objects.filter(user=request.user, paid_order=False)

                # Calculate cart summary
                subtotal, vat, total = calculate_cart_summary(request)

                # Create customer profile if it doesn't exist
                customer = Customer.objects.filter(user=request.user).first()

                # Create a new order and link it to the payment record
                order = Order.objects.create(
                    order_no=uuid.uuid4(),
                    customer=customer,
                    payment=payment,  # Associate the order with the payment
                    total_amount=total,
                    total_price=total,
                    stripe_payment_intent_id=request.GET.get("payment_intent"),
                    is_paid=True,
                    date_created=timezone.now(),
                    shipping_address=f"{payment.address}, {payment.city}, {payment.state}, {payment.postal_code}, {payment.country}",
                    status="Completed",
                    subtotal=subtotal,
                    vat=vat,
                )
            else:
                # For guest users, get the session key
                session_key = request.session.session_key
                if not session_key:
                    messages.error(request, "Session expired. Please try again.")
                    return redirect("cart")

                # Get the latest payment info for the guest user
                payment = PaymentInfo.objects.filter(user=None, paid_order=False).order_by('-created_at').first()

                # Fetch cart items for guest user
                cart_items = ShopCart.objects.filter(user=None, session_key=session_key, paid_order=False)

                # Calculate cart summary
                subtotal, vat, total = calculate_cart_summary(request)

                # Check if we already have a customer with this email
                guest_customer = Customer.objects.filter(email=payment.email).first()

                if not guest_customer:
                    # Create a guest customer profile
                    guest_customer = Customer.objects.create(
                        first_name=payment.first_name,
                        last_name=payment.last_name,
                        email=payment.email,
                        phone_number=payment.phone,
                        address=payment.address,
                        city=payment.city,
                        state=payment.state,
                        postal_code=payment.postal_code,
                        country=payment.country,
                        is_guest=True
                    )
                else:
                    # Update existing customer with payment info
                    guest_customer.first_name = payment.first_name
                    guest_customer.last_name = payment.last_name
                    guest_customer.phone_number = payment.phone
                    guest_customer.address = payment.address
                    guest_customer.city = payment.city
                    guest_customer.state = payment.state
                    guest_customer.postal_code = payment.postal_code
                    guest_customer.country = payment.country
                    guest_customer.save()

                # Create a new order and link it to the payment record
                order = Order.objects.create(
                    order_no=uuid.uuid4(),
                    customer=guest_customer,
                    payment=payment,  # Associate the order with the payment
                    total_amount=total,
                    total_price=total,
                    stripe_payment_intent_id=request.GET.get("payment_intent"),
                    is_paid=True,
                    date_created=timezone.now(),
                    shipping_address=f"{payment.address}, {payment.city}, {payment.state}, {payment.postal_code}, {payment.country}",
                    status="Completed",
                    subtotal=subtotal,
                    vat=vat,
                )

            if not payment:
                messages.error(request, "No payment record found.")
                return redirect("cart")

            if not cart_items.exists():
                messages.error(request, "No paid items found in cart.")
                return redirect("cart")

            # Add cart items to the order
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Mark the payment as associated with an order
            payment.paid_order = True
            payment.save()

            # Clear the cart after order creation
            cart_items.delete()

            messages.success(request, "Payment successful! Order has been created.")
            return render(request, "order_completed.html", {"order": order})

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("cart")

# ================================================================================================================================================================================================================
from django.core.paginator import Paginator

class OrderHistory(View):
    def get(self, request):
        user = request.user
        try:
            orders = Order.objects.filter(customer__user=user).order_by('-date_created')  # Filter by user and sort by latest orders

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


from django.db.models import Q

def search_products(request):
    """
    Search products by name or description.
    Handles both GET and POST requests for backward compatibility.
    """
    # Get search parameters from either GET or POST
    if request.method == "POST":
        search_term = request.POST.get("search", "")
        category_id = request.POST.get("category", None)
    else:
        search_term = request.GET.get("search", "")
        category_id = request.GET.get("category", None)

    # Use __icontains for case-insensitive search on product name and description
    searched_items = Q(name__icontains=search_term) | Q(description__icontains=search_term)

    # If a category is selected, filter by that category as well
    if category_id and category_id != "All Categories":
        try:
            # Try to convert to integer for ID-based lookup
            category_id = int(category_id)
            searched_goods = Product.objects.filter(searched_items, category__id=category_id)
        except (ValueError, TypeError):
            # If not an integer, try to match by name
            searched_goods = Product.objects.filter(searched_items, category__name=category_id)
    else:
        searched_goods = Product.objects.filter(searched_items)

    # Create context dictionary properly
    context = {
        "items": search_term,
        "searched_goods": searched_goods,
    }
    return render(request, "search.html", context)







def filter_products(request):
    category = request.GET.getlist('category')
    category = request.GET.getlist('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    color = request.GET.getlist('color')
    size = request.GET.getlist('size')

    products = Product.objects.all()

    if category:
        products = products.filter(category__in=category)
    if category:
        products = products.filter(category__in=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if color:
        products = products.filter(color__id__in=color)
    if size:
        products = products.filter(size__id__in=size)

    return render(request, 'includes/product_grid.html', {'products': products})

from django.http import HttpResponse
from django.utils.text import slugify
from .models import Service, Category, Product
import random

def populate_db(request):
    # Dummy data
    services_data = {
        "Groceries": [
            {"category": "Frozen", "products": [
                {"name": "Chicken", "price": 15.00, "description": "Fresh frozen chicken", "stock_quantity": 10},
                {"name": "Spinach", "price": 3.50, "description": "Fresh frozen spinach", "stock_quantity": 20},
            ]},
            {"category": "Grains and Flour", "products": [
                {"name": "Basmati Rice", "price": 12.00, "description": "Premium basmati rice", "stock_quantity": 50},
                {"name": "Kidney Beans", "price": 4.00, "description": "Organic kidney beans", "stock_quantity": 30},
            ]}
        ],
        "Restaurant": [
            {"category": "Fast Food", "products": [
                {"name": "Burger", "price": 8.00, "description": "Juicy beef burger", "stock_quantity": 15},
                {"name": "Pizza", "price": 12.00, "description": "Cheese pizza", "stock_quantity": 10},
            ]},
            {"category": "Beverages", "products": [
                {"name": "Coke", "price": 1.50, "description": "Refreshing coke", "stock_quantity": 100},
                {"name": "Orange Juice", "price": 3.00, "description": "Freshly squeezed orange juice", "stock_quantity": 50},
            ]}
        ]
    }

    for service_name, categories in services_data.items():
        # Create or get Service
        service_obj, created = Service.objects.get_or_create(
            name=service_name,
            slug=slugify(service_name),
            defaults={'description': f'{service_name} description', 'image': 'pix.jpg'}
        )

        for category_data in categories:
            category_name = category_data['category']
            # Create or get Category
            category_obj, created = Category.objects.get_or_create(
                name=category_name,
                service=service_obj,
                slug=slugify(category_name)
            )

            # Create Products for each category
            for product_data in category_data['products']:
                Product.objects.get_or_create(
                    name=product_data['name'],
                    category=category_obj,
                    defaults={
                        'price': product_data['price'],
                        'description': product_data['description'],
                        'stock_quantity': product_data['stock_quantity'],
                        'options': generate_random_options(),
                        'image': 'pix.jpg',
                        'featured': random.choice([True, False]),
                        'latest': random.choice([True, False]),
                        'available': True,
                        'min': 1,
                        'max': 20,
                        'rating': str(random.randint(1, 5)),
                    }
                )

    return HttpResponse("Database populated successfully!")


def generate_random_options():
    return {
        "sizes": random.choice([["S", "M", "L"], ["M", "L", "XL"]]),
        "colors": random.choice([["Red", "Blue"], ["Green", "Yellow"]]),
        "types": random.choice([["Cotton", "Polyester"], ["Wool", "Silk"]])
    }
