from django.urls import path
from . import views
from .views import *
from .admininterface import *

urlpatterns = [
    path('populatedb/', populate_db, name='populate_db'),
    # Home and Test URLs
    path('', IndexView.as_view(), name='index'),
    path('home/', HomeView.as_view(), name='home'),
    path('test/', views.test, name='test'),
    path('search/', search_products, name='search_products'),

    # General Pages
    path('about/', views.about, name='about'),
    
    path('contact_us/', views.contact_us, name='contact_us'),
    path('faq/', views.faq, name='faq'),
    path('store-locator/', views.store_locator, name='store_locator'),
    path('coming-soon/', views.coming_soon, name='coming_soon'),
    path('404/', views.error_404, name='error_404'),  # Custom 404 page
    # path('populate/', views.addcats, name='addcats'),

    # Account Management
    path('shipping-and-returns/', views.shipping_and_returns, name='shipping_and_returns'),
    path('account-address/', views.account_address, name='account_address'),
    path('account-orders/', views.account_orders, name='account_orders'),
    path('account-wishlist/', views.account_wishlist, name='account_wishlist'),
    path('account-personal-info/', views.account_personal_info, name='account_personal_info'),
    path('wishlist/', views.account_wishlist, name='wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),

    # Authentication
    path('accounts/login/', LoginPageView.as_view(), name='login'),
    path('logout/', LogoutFuncView.as_view(), name='logout'),
    path('signup/', SignupFormView.as_view(), name='signupform'),
    path('password/', PasswordChangeView.as_view(), name='password'),

    # Shop and Product URLs
    path('shop/', ShopView.as_view(), name='shop'),
    path('shop/<int:category_id>/', IndexView.as_view(), name='shop_with_category'),  # Shop page with category
    path('product/<int:id>/', ProductDetailView.as_view(), name='product'),
    path('service/<int:id>/', ServiceDetailView.as_view(), name='service'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),

    # Cart and Checkout
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Payment and Checkout
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment_pipeline/', PaymentPipelineView.as_view(), name='payment_pipeline'),
    path('successpayment/', CompletedPaymentView.as_view(), name='successpayment'),

    # Orders
    path('orders/history/', OrderHistory.as_view(), name='order_history'),

    # Wishlist
    path('add_to_wishlist/', add_to_wishlist, name='add_to_wishlist'),

    # API Views
    path('cart/increase/<int:item_id>/', increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', decrease_quantity, name='decrease_quantity'),

    # Admin Dashboard URLs
    path('africanfoodadmin/', AdminDashboardView.as_view(), name='admin_dashboard'),

    # Admin: Manage Products
    path('admin/manage-products/', admin_manage_products, name='admin_manage_products'),
    path('admin/product/add/', admin_add_product, name='admin_add_product'),
    path('admin/product/edit/<int:pk>/', admin_edit_product, name='admin_edit_product'),
    path('admin/product/delete/<int:pk>/', admin_delete_product, name='admin_delete_product'),

    # Admin: Manage Categories
    path('admin/manage-categories/', admin_manage_categories, name='admin_manage_categories'),
    path('admin/category/edit/<int:category_id>/', admin_edit_category, name='admin_edit_category'),
    path('admin/category/delete/<int:category_id>/', admin_delete_category, name='admin_delete_category'),

    # Admin: Orders and Customers
    path('admin/view-orders/', admin_view_orders, name='admin_view_orders'),
    path('admin/manage-customers/', admin_manage_customers, name='admin_manage_customers'),

    # Admin: Sales Reports
    path('admin/sales-reports/', admin_sales_reports, name='admin_sales_reports'),

    # Admin: Account Settings
    path('admin/account-settings/', admin_account_settings, name='admin_account_settings'),


    path('account_update/', views.account_update, name='account_update'),

    path('groceries/', views.groceries, name='groceries'),
    path('local-delivery/', views.local_delivery, name='local_delivery'),
    path('deals/', views.deals, name='deals'),
    path('clearance/', views.clearance, name='clearance'),
    path('file-claim/', views.file_claim, name='file_claim'),
    path('blog/', views.blog, name='blog'),
    path('stores/', views.stores, name='stores'),
    path('my-orders/', views.my_orders, name='my_orders'),
    
]
