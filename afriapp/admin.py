from django.contrib import admin
from .models import *




admin.site.register(Service)
admin.site.register(Product)
admin.site.register(ShopCart)
admin.site.register(Slide)
admin.site.register(Wishlist)
admin.site.register(Review)

admin.site.register(Payment)
admin.site.register(Customer)
admin.site.register(Order)
# admin.site.register(OrderItem)
admin.site.register(Category)

