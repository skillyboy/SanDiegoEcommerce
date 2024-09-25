from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.utils.text import slugify
# Category model



# Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products', default='pix.jpg')
    description = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Use name instead of title
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'category'
        managed = True
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        
        
class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)  # Allow blank slug initially

    def save(self, *args, **kwargs):
        if not self.slug:  # Only create a slug if it doesn't exist
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while SubCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    # product :
{
    "sizes": ["S", "M", "L", "XL"],
    "colors": ["Red", "Blue", "Green"],
    "types": ["Cotton", "Polyester"]
}
   
class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products', default='pix.jpg')
    description = models.TextField()
    featured = models.BooleanField(default=False)
    latest = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    min = models.IntegerField(default=1)
    max = models.IntegerField(default=20)
    stock_quantity = models.PositiveIntegerField(default=0)
    options = models.JSONField(blank=True, null=True)  # Using JSONField for storing varying keys

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product'
        managed = True
        verbose_name = 'product'
        verbose_name_plural = 'products'


# Order Model
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    is_paid = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=(
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ), default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.customer.first_name} {self.customer.last_name}"


# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"





# ShopCart model
class ShopCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    basket_no = models.CharField(max_length=36, null=True)
    quantity = models.IntegerField()
    paid_order = models.BooleanField(default=False)
    total = models.FloatField(null=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    class Meta:
        db_table = 'shopcart'
        managed = True
        verbose_name = 'shopcart'
        verbose_name_plural = 'shopcarts'

# Payment model
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    basket_no = models.CharField(max_length=36)
    pay_code = models.CharField(max_length=36)
    paid_order = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.basket_no}"

    class Meta:
        db_table = 'payment'
        managed = True
        verbose_name = 'payment'
        verbose_name_plural = 'payments'

# Slide model (for homepage/carousel)
class Slide(models.Model):
    image = models.ImageField(upload_to='slidepix', default='slide.jpg')
    title = models.CharField(max_length=30)
    comment = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'slide'
        managed = True
        verbose_name = 'slide'
        verbose_name_plural = 'slides'

# Wishlist model
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    class Meta:
        db_table = 'wishlist'
        managed = True
        verbose_name = 'wishlist'
        verbose_name_plural = 'wishlists'

# Review model
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"

    class Meta:
        db_table = 'review'
        managed = True
        verbose_name = 'review'
        verbose_name_plural = 'reviews'
