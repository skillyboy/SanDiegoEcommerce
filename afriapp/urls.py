from django.urls import path

from . import views
from .views import *
from .admininterface import *


urlpatterns = [
    path('addcats/', views.addcats, name='addcats'),
  
    path('about/', views.about, name='about'),
    path('overview/', views.overview, name='overview'),
    
    path('contact_us/', views.contact_us, name='contact_us'),
    path('faq/', views.faq, name='faq'),
    path('store-locator/', views.store_locator, name='store_locator'),
    path('shipping-and-returns/', views.shipping_and_returns, name='shipping_and_returns'),
    path('account-address/', views.account_address, name='account_address'),
    path('account-orders/', views.account_orders, name='account_orders'),
    path('wishlist/', views.account_wishlist, name='wishlist'),
    path('payment/', payment, name='payment'),
    path('account-personal-info/', views.account_personal_info, name='account_personal_info'),
    # path('account-payment-edit/', views.account_payment_edit, name='account_payment_edit'),
    path('coming-soon/', views.coming_soon, name='coming_soon'),
    path('404/', views.error_404, name='error_404'),  # Custom 404 page

    path('', IndexView.as_view(), name='index'),
    path('shop/', ShopView.as_view(), name='shop'),
    
    
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('category/<int:id>/', SingleCategoryView.as_view(), name='category'),
    path('product/<int:id>/', ProductDetailView.as_view(), name='details'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('logout/', LogoutFuncView.as_view(), name='logout'),
    path('signup/', SignupFormView.as_view(), name='signupform'),
    path('password/', PasswordChangeView.as_view(), name='password'),
    # API Views
    path('increase/', IncreaseQuantityView.as_view(), name='increase'),
    path('add_to_wishlist/', add_to_wishlist, name='add_to_wishlist'),
   
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('addtocart/<int:product_id>/', AddToCartView.as_view(), name='addtocart'),
    
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    
   
   
    path('deleteitem/', DeleteItemView.as_view(), name='deleteitem'),
   
   
   
   
   
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('placeorder/', PlaceOrderView.as_view(), name='placeorder'),
    path('payment/', CompletedPaymentView.as_view(), name='payment'),
    
    path('completed/', CompletedView.as_view(), name='completed'),

    path('profile/update/', UpdateProfile.as_view(), name='update_profile'),
    path('orders/history/', OrderHistory.as_view(), name='order_history'),
    path('products/search/', SearchProducts.as_view(), name='search_products'),
    
    # path('products/<int:product_id>/review/', SubmitReview.as_view(), name='submit_review'),
    # path('products/<int:product_id>/reviews/', ViewReviews.as_view(), name='view_reviews'),
    path('payment/confirm/', ConfirmPayment.as_view(), name='confirm_payment'),
    # path('payment/invoice/<int:order_id>/', ViewInvoice.as_view(), name='view_invoice'),
    # path('cart/reminder/', SendCartReminder.as_view(), name='send_cart_reminder'),
    path('products/filter/', FilterProducts.as_view(), name='filter_products'),
    path('products/sort/', SortProducts.as_view(), name='sort_products'),
    # path('newsletter/subscribe/', SubscribeNewsletter.as_view(), name='subscribe_newsletter'),
    path('products/recently-viewed/', RecentlyViewedProducts.as_view(), name='recently_viewed_products'),

  # Admin dashboard
    path('africanfoodadmin/', AdminDashboardView.as_view(), name='admin_dashboard'),

    # Manage products
    path('admin/manage-products/', admin_manage_products, name='admin_manage_products'),

    # View orders
    path('admin/view-orders/', admin_view_orders, name='admin_view_orders'),

    # Manage customers
    path('admin/manage-customers/', admin_manage_customers, name='admin_manage_customers'),

    # Manage categories
    path('admin/manage-categories/', admin_manage_categories, name='admin_manage_categories'),

    # Sales reports
    path('admin/sales-reports/', admin_sales_reports, name='admin_sales_reports'),

    path('admin/add-category/', admin_add_category, name='admin_add_category'),
    # Add other URL patterns here

    path('admin/category/edit/<int:category_id>/', admin_edit_category, name='admin_edit_category'),

    path('admin/category/delete/<int:category_id>/', admin_delete_category, name='admin_delete_category'),
    path('admin/product/add/', admin_add_product, name='admin_add_product'),
    path('admin/product/edit/<int:pk>/', admin_edit_product, name='admin_edit_product'),

    path('admin/product/delete/<int:pk>/', admin_delete_product, name='admin_delete_product'),
    
    
    path('admin/account-settings/', admin_account_settings, name='admin_account_settings'),
]
