from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.shortcuts import render, redirect, get_object_or_404

from django.views import View
from django.utils.decorators import method_decorator
from .forms import *

# Admin Dashboard

@method_decorator(login_required, name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        # Get the total count of customers, orders, and products
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        total_products = Product.objects.count()
        
        # Get orders that are pending or completed
        pending_orders = Order.objects.filter(status='pending').count()
        completed_orders = Order.objects.filter(status='completed').count()
        
        context = {
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_products': total_products,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
        }
        
        return render(request, 'admininterface/admin_dashboard.html', context)

# Manage Products
@login_required
def admin_manage_products(request):
    products = Product.objects.all()
    return render(request, 'admininterface/admin_manage_products.html', {'products': products})

# View Orders
@login_required
def admin_view_orders(request):
    orders = Order.objects.all()
    return render(request, 'admininterface/admin_view_orders.html', {'orders': orders})

# Manage Customers
@login_required
def admin_manage_customers(request):
    customers = Customer.objects.all()
    return render(request, 'admininterface/admin_manage_customers.html', {'customers': customers})

# Manage Categories
@login_required
def admin_manage_categories(request):
    categories = Category.objects.all()
    return render(request, 'admininterface/admin_manage_categories.html', {'categories': categories})

# Sales Reports
@login_required
def admin_sales_reports(request):
    # Sales report logic goes here, could involve fetching sales data, aggregating, etc.
    return render(request, 'admininterface/admin_sales_reports.html')

# Account Settings
@login_required
def admin_account_settings(request):
    if request.method == 'POST':
        # Handle account settings update logic (e.g., password change, profile update)
        messages.success(request, 'Account settings updated successfully!')
        return redirect('admin_account_settings')
    return render(request, 'admininterface/admin_account_settings.html')



def get_total_users():
    return User.objects.count()

def get_total_orders():
    return Order.objects.count()

def get_total_products():
    return Product.objects.count()

# You can create other admin functions here to fetch, update or manipulate data for the admin dashboard.


@login_required
def admin_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('admin_manage_products')
        else:
            messages.error(request, 'There was an error adding the product. Please check the form.')
    else:
        form = ProductForm()

    context = {
        'form': form,
    }

    return render(request, 'admininterface/admin_add_product.html', context)


@login_required
def admin_edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_manage_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admininterface/admin_edit_product.html', {'form': form, 'product': product})

@login_required
def admin_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('admin_manage_products')

    return render(request, 'admin_delete_product.html', {'product': product})

@login_required
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)  # Fetch the category by ID
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)  # Bind form to existing category
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_manage_categories')  # Redirect to category list page
    else:
        form = CategoryForm(instance=category)  # Pre-fill form with existing data
    
    context = {
        'form': form,
        'category': category
    }
    return render(request, 'admininterface/admin_edit_category.html', context)
@login_required
def admin_add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_manage_categories')  # Redirect after successful submission
    else:
        form = CategoryForm()
    return render(request, 'admininterface/admin_add_category.html', {'form': form})



@login_required
def admin_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('admin_manage_categories')  # Redirect to manage categories page

    return render(request, 'admininterface/admin_confirm_delete.html', {'category': category})
