from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.utils.text import slugify
# Category model



# Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
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
    is_guest = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Service(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products', default='pix.jpg')
    description = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, null=False, blank=True)  # Allow blank for now

    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it doesn’t exist
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'service'
        managed = True
        verbose_name = 'service'
        verbose_name_plural = 'services'


class Category(models.Model):
    service = models.ForeignKey(Service, related_name='services', on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True, blank=True)  # Allow blank slug initially

    def save(self, *args, **kwargs):
        if not self.slug:  # Only create a slug if it doesn't exist
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():  # Change from Service to Category
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super(Category, self).save(*args, **kwargs)  # Change Service to Category

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
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
    date_created = models.DateTimeField(default=timezone.now)
    rating = models.CharField(max_length=50,default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product'
        managed = True
        verbose_name = 'product'
        verbose_name_plural = 'products'



class ShopCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    basket_no = models.CharField(max_length=36, null=True)
    quantity = models.IntegerField(default=1)
    paid_order = models.BooleanField(default=False)
    total = models.FloatField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        user_str = f"{self.user}'s" if self.user else "Guest"
        return f"{user_str} cart - {self.product.name} (Qty: {self.quantity})"

    def calculate_total_price(self):
        return self.quantity * self.product.price

    def save(self, *args, **kwargs):
        # Ensure either user or session_key is provided
        if not self.user and not self.session_key:
            raise ValueError("Either user or session_key must be provided")
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'shopcart'
        managed = True
        verbose_name = 'shopcart'
        verbose_name_plural = 'shopcarts'

class CartItem(models.Model):
    shop_cart = models.ForeignKey(ShopCart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"



# Order Model
import uuid
class Order(models.Model):
    item = models.ForeignKey('Product', on_delete=models.CASCADE, default=1),
    order_no = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    shipping_cost = models.PositiveIntegerField(default=0)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    payment = models.ForeignKey("PaymentInfo", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")  # Link to PaymentInfo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    basket_no = models.CharField(max_length=36, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)  # Payment Intent ID from Stripe
    is_paid = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=(
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ), default='Pending')

    def __str__(self):
        return f"{self.id}: Order {self.order_no} by {self.customer.first_name} {self.customer.last_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.product.name} (Qty: {self.quantity}) - Order {self.order.id}"




class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)  # Correct usage
    basket_no = models.CharField(max_length=36)
    pay_code = models.CharField(max_length=36)
    paid_order = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    # postal= models.CharField(max_length=20, default='00000', null=True, blank=True),  # Set default value
    new_postal= models.CharField(max_length=20, default='00000'),  # Set default value

    country = models.CharField(max_length=50, blank=True, null=False)  # New field for country
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Bank Transfer'),
            ('cash_on_delivery', 'Cash on Delivery'),
        ],
        default='credit_card'  # Set the default value here
    )
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # New field for transaction ID

    def __str__(self):
        return f"{self.user} - {self.basket_no}"

    class Meta:
        db_table = 'payment'
        managed = True
        verbose_name = 'payment'
        verbose_name_plural = 'payments'

class PaymentInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)  # Correct usage
    basket_no = models.CharField(max_length=36,null=True, blank=True)
    pay_code = models.CharField(max_length=36, null=True, blank=True)
    paid_order = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)  # Added email field for guest users
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    # postal= models.CharField(max_length=20, default='00000', null=True, blank=True),  # Set default value
    postal_code = models.CharField(max_length=20, default="")  # Set default value

    country = models.CharField(max_length=50, blank=True, null=False)  # New field for country
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Bank Transfer'),
            ('cash_on_delivery', 'Cash on Delivery'),
        ],
        default='credit_card'  # Set the default value here
    )
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # New field for transaction ID

    def __str__(self):
        if self.user:
            return f"{self.user} - {self.basket_no}"
        else:
            return f"Guest ({self.email}) - {self.basket_no}"

    class Meta:
        db_table = 'paymentinfo'
        managed = True
        verbose_name = 'paymentinfo'
        verbose_name_plural = 'paymentsinfo'

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    guest_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.product.name}"
        else:
            return f"Guest ({self.guest_email}) - {self.product.name}"

    def add_product(self, product):
        """Add a product to this wishlist"""
        # Check if product is already in wishlist
        if not Wishlist.objects.filter(user=self.user, product=product).exists():
            # Create a new wishlist item
            Wishlist.objects.create(user=self.user, product=product)

    def remove_product(self, product):
        """Remove a product from this wishlist"""
        Wishlist.objects.filter(user=self.user, product=product).delete()

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


class Conversation(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, default=False)
    forum = models.ForeignKey(Conversation, on_delete=models.CASCADE , null=True)
    value = models.TextField()
    sent = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.forum.name