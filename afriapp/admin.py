from django.contrib import admin
from .models import *

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'price', 'image', 'min', 'max', 'featured', 'latest', 'available')
    list_filter = ('featured', 'latest', 'available')
    search_fields = ('name', 'category__title')
    ordering = ('name',)

class ShopCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'basket_no', 'quantity', 'paid_order', 'total')
    search_fields = ('user__username', 'product__name')
    list_filter = ('paid_order',)
    ordering = ('user',)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'basket_no', 'pay_code', 'paid_order', 'first_name', 'last_name', 'phone', 'address', 'city', 'state', 'created_at')
    list_filter = ('paid_order', 'created_at')
    search_fields = ('user__username', 'basket_no', 'pay_code')
    ordering = ('-created_at',)

class SlideAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'title', 'comment')
    search_fields = ('title',)

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')
    ordering = ('-added_at',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating', 'comment', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ShopCart, ShopCartAdmin)
admin.site.register(Slide, SlideAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Review, ReviewAdmin)


admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(SubCategory)

