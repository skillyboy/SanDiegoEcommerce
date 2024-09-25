# Standard Library Imports
import uuid
import logging

# Third-Party Imports
import requests

# Django Imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from django.db.models import Sum, F, FloatField
from django.http import JsonResponse
from django.db import transaction
# Django REST Framework Imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

# Local Application Imports
from .models import Product  # Assuming only Product is needed
from .forms import *
from .serializers import *

def custom_404(request, exception):
    return render(request, '404.html', status=404)

# 1. Index View
def about(request):
    return render(request, 'about.html')

def overview(request):
    return render(request, 'overview.html')












def context_pro(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    cart_items_count = request.user.cart.items.count() if request.user.is_authenticated else 0
    return render(request, 'template_name.html', {
        'categories': categories,
        'subcategories': subcategories,
        'cart_items_count': cart_items_count,
    })




# 8. Signup View

class SignupFormView(View):
    def get(self, request):
        return render(request, 'signup.html')  # Render the signup form template
    def post(self, request):
        # Get the form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Check if the passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')  # Redirect back to signup form
        
        # Concatenate first and last name to create a username
        username = email
        
        # Check if a user with that username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'A user with that username already exists.')
            return redirect('signup')  # Redirect back to signup form

        # Create the user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password1
        )
        
        # Redirect to the index page after successful signup
        return redirect('index')  # Use the name of the URL pattern for index



class LoginPageView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # You need to customize the authentication method to use email instead of username
        user = authenticate(request, username=email, password=password)  # Using 'username' here for email

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('index')  # Replace 'index' with your actual homepage route
        else:
            messages.error(request, 'Email/password incorrect')
            return redirect('login')

# 7. Logout View
class LogoutFuncView(View):
    def get(self, request):
        logout(request)
        return redirect('login')








# 9. Password Change View
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
            messages.success(request, 'Password update successful!')
            return redirect('index')
        else:
            messages.error(request, update.errors)
            return redirect('password')



def addcats(request):
    categories_data = {
        "Groceries": {
            "Frozen": {
                "subcategories": ["Meat", "Vegetables", "Seafood", "Starch"],
                "products": {
                    "Meat": ["Chicken", "Beef", "Pork"],
                    "Vegetables": ["Spinach", "Broccoli", "Carrot"],
                    "Seafood": ["Shrimp", "Fish", "Crab"],
                    "Starch": ["Potatoes", "Yams"]
                }
            },
            "Grains and Flour": {
                "subcategories": ["Rice", "Beans"],
                "products": {
                    "Rice": ["Basmati Rice", "Brown Rice"],
                    "Beans": ["Black Beans", "Kidney Beans"]
                }
            },
            "Oils": {
                "subcategories": ["Vegetable Oils", "Palm Oil"],
                "products": {
                    "Vegetable Oils": ["Canola Oil", "Sunflower Oil"],
                    "Palm Oil": ["Red Palm Oil"]
                }
            },
            "Baby": {
                "subcategories": ["Baby Foods", "Milo", "Milk"],
                "products": {
                    "Baby Foods": ["Baby Cereal", "Fruit Puree"],
                    "Milo": ["Milo Sachet", "Milo Tin"],
                    "Milk": ["Baby Formula", "Whole Milk"]
                }
            },
            "Snacks": {
                "subcategories": [],
                "products": {
                    "Snacks": ["Chips", "Cookies", "Granola Bars"]
                }
            },
            # Add other categories following the same structure
        }
    }

    for main_category, subcategories_info in categories_data.items():
        main_cat_obj, created = Category.objects.get_or_create(name=main_category, slug=slugify(main_category))

        for sub_cat_name, details in subcategories_info.items():
            # Create subcategories
            sub_cat_obj, created = SubCategory.objects.get_or_create(name=sub_cat_name, category=main_cat_obj, slug=slugify(sub_cat_name))

            # Create products for subcategories
            for sub_sub_cat_name in details.get('subcategories', []):
                sub_sub_cat_obj, created = SubCategory.objects.get_or_create(name=sub_sub_cat_name, category=main_cat_obj, slug=slugify(sub_sub_cat_name))
                
                # Add products to the sub-sub-category
                products = details.get('products', {}).get(sub_sub_cat_name, [])
                for product_name in products:
                    Product.objects.get_or_create(
                        name=product_name,
                        subcategory=sub_sub_cat_obj,
                        defaults={'description': f'{product_name} description', 'price': 9.99}  # Example product details
                    )

            # If the subcategory doesn't have nested subcategories, add products directly
            if not details.get('subcategories'):
                products = details.get('products', {}).get(sub_cat_name, [])
                for product_name in products:
                    Product.objects.get_or_create(
                        name=product_name,
                        subcategory=sub_cat_obj,
                        defaults={'description': f'{product_name} description', 'price': 9.99}  # Example product details
                    )

    return render(request, 'about.html')  # Ensure the template path is correct

# About Us page
def about(request):
    return render(request, 'about.html')

# Contact Us page
def contact_us(request):
    return render(request, 'contact-us.html')

# FAQ page
def faq(request):
    return render(request, 'faq.html')

# Store Locator page
def store_locator(request):
    return render(request, 'store-locator.html')

# Shipping and Returns page
def shipping_and_returns(request):
    return render(request, 'shipping-and-returns.html')

# Account Personal Info page
def account_personal_info(request):
    return render(request, 'account-personal-info.html')

# Account Address page
def account_address(request):
    return render(request, 'account-address.html')

# Account Orders page
def account_orders(request):
    return render(request, 'account-orders.html')

# Account Wishlist page
def account_wishlist(request):
    return render(request, 'account-wishlist.html')

# 404 Error page
def error_404(request, exception=None):
    return render(request, '404.html')

# Coming Soon page
def coming_soon(request):
    return render(request, 'coming-soon.html')


def contact(request):
    return render(request, 'contact.html')


def payment(request):
    return render(request, 'payment.html')





class IndexView(View):
    def get(self, request):
        try:
            featured = Product.objects.filter(featured=True)
            latest = Product.objects.filter(latest=True)
            categories = Category.objects.all()
        except Product.DoesNotExist:
            featured, latest, categories = [], [], []
            messages.error(request, 'Failed to load products.')
        
        context = {
            'featured': featured,
            'latest': latest,
            'categories': categories
        }
        
        return render(request, 'index.html', context)

class ShopView(View):
    def get(self, request):
        # Fetch selected products from the session
        selected_product_ids = request.session.get('selected_products', [])

        # Fetch all categories along with their subcategories and products
        categories = Category.objects.prefetch_related('subcategories__products').all()

        # If no products are selected, fetch all products
        if not selected_product_ids:
            products = Product.objects.all()  # Fetch all products
            selected_products = []  # No specific selected products
        else:
            # Fetch only the selected products
            selected_products = Product.objects.filter(id__in=selected_product_ids)
            products = selected_products  # Assign selected products to 'products'

        context = {
            'categories': categories,
            'products': products,  # Display all products or selected products
            'selected_products': selected_products,  # This can be used to show specific selected products
        }

        return render(request, 'shop.html', context)

    @method_decorator(csrf_exempt)  # Needed for AJAX POST without CSRF token
    def post(self, request):
        # Handle the AJAX request for adding/removing products without reloading the page
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')

        # Get selected products from the session
        selected_product_ids = request.session.get('selected_products', [])

        # Add or remove the product based on the action
        if action == 'add' and product_id not in selected_product_ids:
            selected_product_ids.append(product_id)
        elif action == 'remove' and product_id in selected_product_ids:
            selected_product_ids.remove(product_id)

        # Save the updated selected products in session
        request.session['selected_products'] = selected_product_ids

        # Fetch updated selected products
        selected_products = Product.objects.filter(id__in=selected_product_ids)

        # Prepare the JSON response with updated selected products
        response_data = {
            'selected_products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image_url': product.image.url  # Make sure this returns the correct image URL
                } for product in selected_products
            ]
        }

        return JsonResponse(response_data)


# 2. Categories View
class CategoriesView(View):
    def get(self, request):
        # Fetch selected products from the session
        selected_product_ids = request.session.get('selected_products', [])

        # Fetch all categories along with their subcategories and products
        categories = Category.objects.prefetch_related('subcategories__products').all()

        # Fetch selected products based on their IDs
        selected_products = Product.objects.filter(id__in=selected_product_ids)

        context = {
            'categories': categories,
            'selected_products': selected_products  # Pass selected products to the template
        }

        return render(request, 'categories.html', context)

    @method_decorator(csrf_exempt)  # Needed for AJAX POST without CSRF token
    def post(self, request):
        # Handle the AJAX request for adding/removing products without reloading the page
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')

        # Get selected products from the session
        selected_product_ids = request.session.get('selected_products', [])

        # Add or remove the product based on the action
        if action == 'add' and product_id not in selected_product_ids:
            selected_product_ids.append(product_id)
        elif action == 'remove' and product_id in selected_product_ids:
            selected_product_ids.remove(product_id)

        # Save the updated selected products in session
        request.session['selected_products'] = selected_product_ids

        # Fetch updated selected products
        selected_products = Product.objects.filter(id__in=selected_product_ids)

        # Prepare the JSON response with updated selected products
        response_data = {
            'selected_products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image_url': product.image.url  # Make sure this returns the correct image URL
                } for product in selected_products
            ]
        }

        return JsonResponse(response_data)





# 3. Single Category View
class SingleCategoryView(View):
    def get(self, request, id):
        try:
            category = Product.objects.filter(category_id=id)
        except Product.DoesNotExist:
            category = []
            messages.error(request, 'Failed to load category products.')

        context = {
            'category': category
        }

        return render(request, 'category.html', context)



# Set up logging
logger = logging.getLogger(__name__)

# 5. Product Detail View with DRF
class ProductDetailView(APIView):
    def get(self, request, id):
        try:
            # Use DRF's get_object_or_404 to fetch the product or raise a 404 error
            product = get_object_or_404(Product, pk=id)
            # Return a response with the context data
            return render(request, 'product.html', {'product': product})

        except NotFound as e:
            # Handle 404 error gracefully
            logger.error(f"Product with id {id} not found: {e}")
            messages.error(request, 'Product not found.')
            return redirect('products')  # Adjust to your products list URL

        except Exception as e:
            # Catch any other exception and log it
            logger.error(f"An error occurred: {e}")
            messages.error(request, 'An unexpected error occurred.')
            return redirect('products')

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.add_product(product)

        return JsonResponse({'success': True, 'message': 'Product added to wishlist'})


@login_required
def remove_from_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        wishlist = Wishlist.objects.get(user=request.user)
        wishlist.remove_product(product)

        return JsonResponse({'success': True, 'message': 'Product removed from wishlist'})


class AddToCartView(LoginRequiredMixin, View):
    login_url = '/login'

    def post(self, request, product_id):
        try:
            basket_num = str(uuid.uuid4())
            quantity = int(request.POST.get('quantity', 1))  # Default quantity to 1

            # Fetch the product using product_id from the URL
            product = get_object_or_404(Product, pk=product_id)

            # Fetch the current user's cart (filter by unpaid orders)
            cart = ShopCart.objects.filter(user=request.user, paid_order=False)

            if cart.exists():
                # If cart exists, add or update the product
                cart_item = ShopCart.objects.filter(user=request.user, product=product).first()
                if cart_item:
                    cart_item.quantity += quantity
                    cart_item.save()
                else:
                    new_item = ShopCart(
                        user=request.user,
                        product=product,
                        basket_no=cart[0].basket_no,
                        quantity=quantity,
                        paid_order=False
                    )
                    new_item.save()
            else:
                # Create a new basket if no unpaid cart exists
                new_basket = ShopCart(
                    user=request.user,
                    product=product,
                    basket_no=basket_num,
                    quantity=quantity,
                    paid_order=False
                )
                new_basket.save()

            # Calculate total cart items for the user
            cart_item_count = ShopCart.objects.filter(user=request.user, paid_order=False).count()

            # Handle AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'cart_item_count': cart_item_count})
            else:
                # Non-AJAX: Show success message and redirect to the cart
                messages.success(request, f'{product.name} was added to your cart.')
                return redirect('cart')  # Replace 'cart' with the name of your cart view URL

        except Exception as e:
            # Log the error for debugging
            logging.error(f'Error in AddToCartView: {e}')

            # Handle AJAX requests with an error response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            else:
                # Non-AJAX: Show error message and redirect to the shop
                messages.error(request, "There was an error adding the product to the cart.")
                return redirect('shop')  # Replace 'shop' with a safe page URL


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


# 12. Delete Item View
class DeleteItemView(View):
    @login_required(login_url='/login')
    def post(self, request):
        itemid = request.POST['itemid']
        ShopCart.objects.filter(pk=itemid).delete()
        messages.success(request, 'Product deleted')
        return redirect('cart')


# 13. Increase Quantity View
class IncreaseQuantityView(View):
    @login_required(login_url='/login')
    def post(self, request):
        itemval = request.POST['itemval']
        if int(itemval) < 1:
            itemval = '1'
        valid = request.POST['valid']
        update = ShopCart.objects.get(pk=valid)
        update.quantity = itemval 
        update.save()
        messages.success(request, 'Product quantity updated successfully')
        return redirect('cart')

#########################   ##########3




def add_to_cart(request, product_id):
    """View to add a product to the cart."""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = ShopCart.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

def remove_from_cart(request, cart_item_id):
    """View to remove a product from the cart."""
    try:
        # Ensure that the user is authenticated and owns the cart item
        cart_item = get_object_or_404(ShopCart, id=cart_item_id, user=request.user)

        # Use transaction to ensure safe database operations
        with transaction.atomic():
            cart_item.delete()

        # Provide feedback to the user
        messages.success(request, "Item successfully removed from your cart.")

    except ShopCart.DoesNotExist:
        messages.error(request, "Cart item not found.")
    except Exception as e:
        # Log the exception for debugging purposes
        messages.error(request, "An error occurred while trying to remove the item.")
        print(f"Error removing item from cart: {str(e)}")  # Logging can be added if needed

    return redirect('cart')

def update_cart_item_quantity(request, cart_item_id):
    """View to update the quantity of a cart item."""
    cart_item = get_object_or_404(ShopCart, id=cart_item_id)
    quantity = request.POST.get('quantity', 1)
    cart_item.quantity = int(quantity)
    cart_item.save()
    return JsonResponse({'status': 'success'})










##################################
# 14. Checkout View
class CheckoutView(View):
    @login_required
    def get(self, request):
        # Get all items in the user's cart that haven't been paid for
        cart_items = ShopCart.objects.filter(user=request.user, paid_order=False)

        # Calculate the total price
        total = sum(item.product.price * item.quantity for item in cart_items)

        context = {
            'cart_items': cart_items,
            'total': total,
        }
        
        return render(request, 'checkout.html', context)

    @login_required
    def post(self, request):
        try:
            # Handle payment processing logic here (e.g., interacting with a payment gateway)

            # Mark all items in the user's cart as paid
            ShopCart.objects.filter(user=request.user, paid_order=False).update(paid_order=True)
            
            # Notify the user of the successful payment
            messages.success(request, 'Payment Successful')

            # Redirect to the payment completion page
            return redirect('order-confirmation')
        
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('cart')


# 15. Place Order View
class PlaceOrderView(View):
    @login_required(login_url='/login')
    def post(self, request):
        api_key = 'your_stripe_api_key'
        curl = 'https://api.stripe.com/v1/payment_intents'
        cburl = 'http://localhost:8000/completed'
        total = float(request.POST['total']) * 100
        cart_code = request.POST['cart_code']
        pay_code = str(uuid.uuid4())
        user = User.objects.get(username=request.user.username)
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']

        headers = {'Authorization': f'Bearer {api_key}'}
        data = {
            'amount': int(total),
            'currency': 'usd',
            'payment_method_types[]': 'card',
            'receipt_email': user.email,
            'metadata[basket_no]': cart_code,
            'metadata[pay_code]': pay_code
        }

        try:
            r = requests.post(curl, headers=headers, data=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Network busy, try again. Error: {str(e)}')
            return redirect('checkout')

        else:
            transback= json.loads(r.text)
            rd_url= transback['data']['authorization_url']
            
            paid = Payment.objects.create(
            user=user,
            amount=total,
            basket_no=cart_code,
            pay_code=pay_code,
            paid_order=True,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )

        bag = ShopCart.objects.filter(user__username=request.user, paid_order=False)
        for item in bag:
            item.paid_order = True
            item.save()

            stock = Product.objects.get(pk=item.product.id)
            stock.max -= item.quantity
            stock.save()
                
        return redirect(rd_url)
        # return redirect('checkout')




# @method_decorator(login_required(login_url='/login'), name='dispatch')
class CompletedPaymentView(View):
    def get(self, request):
        try:
            user = User.objects.get(username=request.user.username)
            # Perform any additional logic needed upon payment completion here

            # Mark all items in the user's cart as paid
            ShopCart.objects.filter(user=user, paid_order=False).update(paid_order=True)
            
            # Notify the user of the successful payment
            messages.success(request, 'Payment Successful')

            # Redirect the user to the products page or any other page
            return redirect('products')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('cart')
        
# 16. Completed Order View
class CompletedView(View):
    # @login_required(login_url='/login')
    def get(self, request):
        try:
            user = User.objects.get(username=request.user.username)
            
            # Mark all items in the user's cart as paid
            ShopCart.objects.filter(user=user, paid_order=False).update(paid_order=True)
            
            # Notify the user of the successful payment
            messages.success(request, 'Payment Successful')

            # # Redirect the user to the order confirmation page
            # return redirect('completed')

            # Render the completed.html template to show the payment confirmation
            return render(request, 'order_completed.html')
        
        except User.DoesNotExist:
            messages.error(request, 'User not found')
            return redirect('cart')


class UpdateProfile(APIView):

    def put(self, request):
        try:
            # Get the current user
            user = request.user

            # Update user's first name, last name, and email if provided in the request data
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            user.email = request.data.get('email', user.email)
            
            # Save the updated user information
            user.save()

            # Return a success response
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            # Return an error response if something goes wrong
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FilterProducts(APIView):

    def get(self, request):
        try:
            # Extract query parameters
            category_id = request.query_params.get('category_id')
            price_range = request.query_params.get('price_range')
            products = Product.objects.all()

            # Filter by category if provided
            if category_id:
                products = products.filter(category_id=category_id)

            # Filter by price range if provided
            if price_range:
                min_price, max_price = map(float, price_range.split('-'))
                products = products.filter(price__gte=min_price, price__lte=max_price)

            # Serialize the filtered products
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
def category_view(request):
    categories = Category.objects.prefetch_related('subcategories__products').all()
    return render(request, 'category_page.html', {'categories': categories})
    
class SortProducts(APIView):

    def get(self, request):
        try:
            # Extract sort parameter
            sort_by = request.query_params.get('sort_by')
            products = Product.objects.all()

            # Sort products based on the provided sort_by parameter
            if sort_by:
                if sort_by == 'price':
                    products = products.order_by('price')
                elif sort_by == 'name':
                    products = products.order_by('name')
                elif sort_by == 'date':
                    products = products.order_by('-created_at')

            # Serialize the sorted products
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=400) 
        
class RecentlyViewedProducts(APIView):

    def get(self, request):
        try:
            # Assuming you have a way to track recently viewed products
            # For example, using a model that tracks user views or storing in a session

            # Here we'll assume recently viewed products are stored in the session
            recently_viewed_ids = request.session.get('recently_viewed', [])
            products = Product.objects.filter(id__in=recently_viewed_ids)

            # Serialize the recently viewed products
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=400)




class SearchProducts(APIView):

    def get(self, request):
        try:
            # Get the search query parameter from the request
            query = request.query_params.get('q', '')

            # Perform a search on the Product model based on the query
            products = Product.objects.filter(name__icontains=query) | Product.objects.filter(description__icontains=query)

            # Serialize the matching products
            serializer = ProductSerializer(products, many=True)

            # Return the serialized products as a response
            return Response(serializer.data, status=200)

        except Exception as e:
            # Return an error response in case of any exceptions
            return Response({"error": str(e)}, status=400)

def filter_products(request):
    # Fetch filtered products
    category = request.GET.getlist('category')
    subcategory = request.GET.getlist('subcategory')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    color = request.GET.getlist('color')
    size = request.GET.getlist('size')

    products = Product.objects.all()

    if category:
        products = products.filter(category__in=category)
    if subcategory:
        products = products.filter(subcategory__in=subcategory)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if color:
        products = products.filter(color__id__in=color)
    if size:
        products = products.filter(size__id__in=size)
        
    # Render partial HTML for product grid
    return render(request, 'includes/product_grid.html', {'products': products})

class ConfirmPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Retrieve payment details from the request
            payment_id = request.data.get('payment_id')
            payment = get_object_or_404(Payment, id=payment_id, user=request.user)

            # Assuming an external API is used to confirm payment
            payment_gateway_url = "https://api.examplepaymentgateway.com/verify"
            response = requests.post(payment_gateway_url, data={'payment_id': payment.pay_code})

            if response.status_code == 200:
                payment_status = response.json().get('status')

                if payment_status == 'success':
                    # Update the payment status in the database
                    payment.paid_order = True
                    payment.save()

                    # Return a success response
                    return Response({"message": "Payment confirmed successfully."}, status=200)

                else:
                    # Payment failed
                    return Response({"error": "Payment could not be confirmed."}, status=400)

            else:
                # External API call failed
                return Response({"error": "Failed to verify payment with the payment gateway."}, status=400)

        except Exception as e:
            # Return an error response in case of any exceptions
            return Response({"error": str(e)}, status=400)


class OrderHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the logged-in user's payment history
            user = request.user
            orders = Payment.objects.filter(user=user)

            if not orders.exists():
                # If no orders are found, return a message indicating so
                return Response({"message": "No order history found."}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the order history
            serializer = PaymentSerializer(orders, many=True)

            # Return the serialized order history as JSON
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Payment.DoesNotExist:
            # Handle case where the payment records do not exist
            return Response({"error": "No payment records found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # General exception handler for any other errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




# def add_billing_address(request):
#     if request.method == "POST":
#         customer = AddCustomer.objects.get(id=user)
#         country = request.POST["country"]
#         state = request.POST["state"]
#         city = request.POST["city"]
#         area = request.POST["area"]
#         street = request.POST["street"]
#         door_no = request.POST["door_no"]
#         postal_code = request.POST["postal_code"]

#         BillingAddress.objects.create(
#             customer=customer,
#             country=country,
#             state=state,
#             city=city,
#             area=area,
#             street=street,
#             door_no=door_no,
#             postal_code=postal_code
#         )
#         return redirect('view-client', pk=user)
    
#     customer = AddCustomer.objects.get(id=user)
#     context = {
#         'customer': customer
#     }
    
#     return render(request, 'clients/add_billing_address.html', context)


# # @allowed_user(app_name='finance')
# def edit_billing_address(request, pk):
#     billing_address = BillingAddress.objects.get(id = pk)
#     if request.method == "POST":
#         billing_address.country = request.POST["country"]
#         billing_address.state = request.POST["state"]
#         billing_address.city = request.POST["city"]
#         billing_address.area = request.POST["area"]
#         billing_address.street = request.POST["street"]
#         billing_address.door_no = request.POST["door_no"]
#         billing_address.postal_code = request.POST["postal_code"]

#         billing_address.save()
#         return redirect('view-client', pk=clientid)
#     customer = AddCustomer.objects.filter(id = clientid)
#     billing_address = BillingAddress.objects.filter(id = pk)
#     context = {
#         'customer': customer,
#         'billing_address': billing_address,     
#     }

#     return render(request, 'clients/edit_billing_address.html', context)


# # @allowed_user(app_name='finance')
# def delete_billing_address(request, pk, user.id):
#     b = BillingAddress.objects.get(id = pk)
#     b.delete()
#     return redirect('view-client', pk = user.id)



