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
from django.db.models import Sum, F, FloatField
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

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
from .models import Payment, ShopCart, Product  # Assuming these are your models
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY
# Logging configuration
logger = logging.getLogger(__name__)

# from rest_framework.response import Response
from django.contrib.auth.forms import PasswordChangeForm
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Payment, ShopCart
from django.conf import settings
# Views List
# -------------------


stripe.api_key = settings.STRIPE_SECRET_KEY



# Home page view
def my_orders(request):
    return render(request, 'my_orders.html')

# Groceries page view
def groceries(request):
    return render(request, 'groceries.html')

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


# 9. Store Locator View
def store_locator(request):
    return render(request, 'store-locator.html')


# 10. Shipping and Returns View
def shipping_and_returns(request):
    return render(request, 'shipping-and-returns.html')


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
    return render(request, 'account/account-address.html')




# 14. Account Wishlist View
def account_wishlist(request):
    return render(request, 'account/account-wishlist.html')


# 15. Error 404 Page
def error_404(request, exception=None):
    return render(request, '404.html')


# 16. Coming Soon View
def coming_soon(request):
    return render(request, 'coming-soon.html')


# Authentication Views
# -----------------------


class SignupFormView(View):
    def get(self, request):
        return render(request, 'signup.html')

    @transaction.atomic
    def post(self, request):
        try:
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            # Validate form inputs
            if password1 != password2:
                raise ValidationError("Passwords do not match.")

            if User.objects.filter(username=email).exists():
                raise IntegrityError("A user with that email already exists.")

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
            login(request, user)

            messages.success(request, 'Signup successful!')
            return redirect('index')

        except ValidationError as ve:
            messages.error(request, str(ve))
            return redirect('signup')

        except IntegrityError:
            messages.error(request, 'A user with that email already exists.')
            return redirect('signup')

        except Exception as e:
            logger.error(f"Signup failed: {e}")
            messages.error(request, 'An unexpected error occurred. Please try again later.')
            return redirect('signup')
        
        
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

        except Product.DoesNotExist:
            featured, latest, services, latest_products = [], [], [], []
            messages.error(request, 'Products could not be loaded.')

        context = {
            'featured': featured,
            'latest': latest,
            'services': services,
            'service_id': service_id,
            'latest_products': latest_products,  # Pass latest products to context
        }

        template = 'shop.html' if service_id else 'index.html'
        return render(request, template, context)


# 6. Categories Viewfrom .models import Product  # Ensure you import your Product modelfrom django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.shortcuts import render
from .models import Service  # Ensure you have the correct import

class ServiceDetailView(TemplateView):
    template_name = 'category_detail.html'

    def get(self, request, id):
        # Get the service using the provided ID
        service = get_object_or_404(Service, pk=id)

        # Retrieve all categories related to the service
        categories = service.services.all()  # Use 'services' since it's the related name

        categories_with_products = {}
        total_products = 0
        
        # Iterate through categories and get products
        for category in categories:
            products = category.products.filter(available=True)  # Correctly reference products through the category
            categories_with_products[category] = products
            total_products += products.count()

        # Now calculate the percentage for each category
        for category, products in categories_with_products.items():
            product_count = products.count()
            percentage = (product_count / total_products * 100) if total_products > 0 else 0
            categories_with_products[category] = {
                'products': products,
                'percentage': percentage,
            }

        return render(request, self.template_name, {
            'service': service,  # Pass the service object
            'categories_with_products': categories_with_products,
            'total_products': total_products,
        })



# 7. Shop View
class ShopView(TemplateView):
    template_name = 'shop.html'

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        categories = Service.objects.all()
        
        # Get the selected category ID from the request
        category_id = request.GET.get('category_id')

        # If a category is selected, filter products by that category
        if category_id:
            products = products.filter(category__id=category_id)

        # Retrieve the cart count from the session
        cart_count = request.session.get('cart_count', 0)

        context = {
            'products': products,
            'categories': categories,
            'cart_count': cart_count,
        }

        return render(request, self.template_name, context)


# 8. Product Detail View with DRF
class ProductDetailView(View):
    def get(self, request, id):
        # Use DRF's get_object_or_404 to fetch the product or raise a 404 error
        product = get_object_or_404(Product, pk=id)
        # Return a response with the context data
        return render(request, 'product.html', {'product': product})
    
    
    
# 9. Add to Wishlist
@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.add_product(product)

        return JsonResponse({'success': True, 'message': 'Product added to wishlist'})


# 11. Add to Cart

# ============================================================================

@login_required  # Optional: If you want to allow only logged-in users
# This view handles adding products to the cart for both logged-in and non-logged-in users
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Use session key for non-authenticated users
    session_key = request.session.session_key
    if not session_key:
        session_key = request.session.create()  # Create a session if not already present
    
    # Handle POST request for adding to cart
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        # Use get_or_create for efficiency
        cart, created = ShopCart.objects.get_or_create(
            user=request.user if request.user.is_authenticated else None,  # Handle both logged-in and guest users
            session_key=session_key,
            product=product,
            paid_order=False,  # Assuming `paid_order` means the order is not yet completed
            defaults={'quantity': quantity}
        )

        # Update or add product to the cart
        if created:
            message = 'Product added to cart successfully!'
        else:
            # If the product is already in the cart, update quantity if necessary
            if cart.quantity == quantity:
                message = 'Product was already added to the cart!'
            else:
                cart.quantity = quantity
                cart.save()
                message = 'Quantity updated successfully!'

        # Calculate the total number of unique products in the cart
        cart_count = ShopCart.objects.filter(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            paid_order=False
        ).values('product').distinct().count()

        # If the request was an AJAX request, return a JSON response
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': message,
                'cart_count': cart_count
            })

        # For normal form submissions, redirect to the cart page
        return redirect('cart')  # Replace 'cart' with the URL name of your cart page

    # Handle invalid request methods (e.g., if someone tried to use GET)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# 12. Cart View
class CartView(View):
    def get(self, request):
        # Query all items in the cart for the current user where the order is not paid
        cart = ShopCart.objects.filter(user=request.user, paid_order=False)
        # Annotate each item with its total price (product price * quantity)
        cart = cart.annotate(total_price=F('product__price') * F('quantity'))
        
        # Aggregate total quantity and subtotal (sum of all total prices)
        cart_summary = cart.aggregate(
            quantity_sum=Sum('quantity'),
            subtotal=Sum('total_price', output_field=FloatField())
        )
        
        # Extract values from the summary, with defaults in case of None
        cartreader = cart_summary.get('quantity_sum') or 0
        subtotal = cart_summary.get('subtotal') or 0.0
        
        # Calculate VAT and total price
        vat = 0.075 * subtotal
        total = subtotal + vat
        
        # Prepare the context for the template
        context = {
            'cart': cart,  
            'cartreader': cartreader,
            'subtotal': round(subtotal, 2),
            'vat': round(vat, 2),
            'total': round(total, 2),
        }
        
        return render(request, 'cart.html', context)

# ============================================================================
def increase_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(ShopCart, id=item_id, user=request.user)  # Ensure it belongs to the user
        cart_item.quantity += 1
        cart_item.save()
        
        # Calculate updated values
        subtotal, vat, total = calculate_cart_summary(request.user)
        
        return JsonResponse({
            'new_quantity': cart_item.quantity,
            'new_total_price': round(cart_item.calculate_total_price(), 2),
            'subtotal': round(float(subtotal), 2),
            'vat': round(float(vat), 2),
            'total': round(float(total), 2),
        })
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def decrease_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(ShopCart, id=item_id, user=request.user)  # Ensure it belongs to the user
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        
        # Calculate updated values
        subtotal, vat, total = calculate_cart_summary(request.user)
        
        return JsonResponse({
            'new_quantity': cart_item.quantity,
            'new_total_price': round(cart_item.calculate_total_price(), 2),
            'subtotal': round(float(subtotal), 2),
            'vat': round(float(vat), 2),
            'total': round(float(total), 2),
        })
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def calculate_cart_summary(user):
    """Calculate the cart summary for the given user."""
    cart_items = ShopCart.objects.filter(user=user, paid_order=False)

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
            cart_item = get_object_or_404(ShopCart, id=cart_item_id, user=request.user)
            cart_item.delete()

            # Check if it's an AJAX request
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                subtotal, vat, total = calculate_cart_summary(request.user)
                cart_empty = not ShopCart.objects.filter(user=request.user).exists()

                return JsonResponse({
                    'success': True,
                    'subtotal': subtotal,
                    'vat': vat,
                    'total': total,
                    'cart_empty': cart_empty  # Handle empty cart state
                })

            # Handle non-AJAX request
            return redirect(request.META.get('HTTP_REFERER', 'cart_view'))

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


class CheckoutView(TemplateView):
    
    def get(self, request):
        # Get cart items for the user
        cart = ShopCart.objects.filter(user=request.user, paid_order=False)
        customer = Customer.objects.filter(user=request.user).first()
        
        if not cart.exists():
            messages.error(request, 'No items in the cart.')
            return redirect('cart')  # Redirect user if no cart items
        
        context = {
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            'cart': cart,
            'customer': customer,
            'total_price': sum(item.calculate_total_price() for item in cart)  # Total price calculation for display
        }
        
        return render(request, 'checkout.html', context)
    

class PaymentPipelineView(View):
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

            # Create a payment record before attempting the checkout
            payment = Payment.objects.create(
                user=request.user,
                amount=total_price_with_shipping,
                basket_no=basket_no,
                pay_code='some_unique_code',  # Generate or assign a unique code
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                phone=request.user.profile.phone,  # Assuming you have user profile with phone
                address='User address here',  # Fetch or set the address
                city='User city',
                state='User state',
                postal_code='User postal code',
                country='User country',
                payment_method='credit_card'  # Set based on the payment method
            )

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

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,  
                metadata={"basket_no": basket_no},  
                mode='payment',
                success_url=f'{YOUR_DOMAIN}/successpayment/',  
                cancel_url=f'{YOUR_DOMAIN}/cancelpayment/',
            )
            
            # Here, you may want to update the Payment instance with the session ID
            payment.stripe_payment_intent_id = checkout_session.id
            payment.save()  # Save the payment record with the session ID

            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            print("Error creating checkout session:", str(e))
            return JsonResponse({'error': str(e)}, status=500)



class CompletedPaymentView(View):
    def get(self, request):
        try:
            # Mark cart items as paid
            ShopCart.objects.filter(paid_order=False).update(paid_order=True)
            messages.success(request, 'Payment Successful')
            return render(request, 'order_completed.html')
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('cart')


class OrderHistory(View):

    def get(self, request):
        user = request.user
        try:
            orders = Order.objects.filter()

            if not orders.exists():
                messages.info(request, "No order history found.")  # Using messages framework for user feedback
                return render(request, 'account/account-orders.html', {"orders": orders})  # Render even if empty

            return render(request, 'account/account-orders.html', {"orders": orders})

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")  # Using messages for error
            return render(request, 'account/account-orders.html', {"orders": []})  # Pass an empty list on error



class OrderDetail(View):

    def get(self, request, order_id):
        user = request.user
        try:
            order = get_object_or_404(Order, id=order_id)

            if not order:
                messages.info(request, "No order  found.")  # Using messages framework for user feedback
                return render(request, 'account/account-order-detail.html', {"order": order})  # Render even if empty

            return render(request, 'account/account-order-detail.html', {"order": order})

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")  # Using messages for error
            return render(request, 'account/account-order-detail.html', {"order": []})  # Pass an empty list on error



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






def search_products(request):
    query = request.GET.get('search', '')
    category = request.GET.get('category', 'All Categories')

    # Filter products based on the search term and category
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category and category != 'All Categories':
        products = products.filter(category=category)

    context = {
        'products': products,
        'query': query,
        'category': category,
    }
    return render(request, 'your_template.html', context)



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
