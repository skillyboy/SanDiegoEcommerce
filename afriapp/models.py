from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


# Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_guest = models.BooleanField(default=False)

    class Meta:
        managed = True
        verbose_name = 'customer'
        verbose_name_plural = 'customers'

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.email


# Newsletter Model
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

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
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    image = models.ImageField(upload_to='products', default='pix.jpg')
    description = models.TextField()
    featured = models.BooleanField(default=False)
    latest = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    min_purchase = models.PositiveIntegerField(default=1)
    max_purchase = models.PositiveIntegerField(default=20)
    stock_quantity = models.PositiveIntegerField(default=0)
    options = models.JSONField(blank=True, null=True)  # Using JSONField for storing varying keys
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    cultural_significance = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique
            counter = 1
            original_slug = self.slug
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price

    def get_discount_percentage(self):
        if self.is_on_sale():
            discount = ((self.price - self.sale_price) / self.price) * 100
            return int(discount)
        return 0

    def get_display_price(self):
        if self.is_on_sale():
            return self.sale_price
        return self.price

    def is_in_stock(self):
        return self.stock_quantity > 0

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product'
        managed = True
        verbose_name = 'product'
        verbose_name_plural = 'products'
        ordering = ['-date_created']



class ShopCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    basket_no = models.CharField(max_length=36, null=True)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    paid_order = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        if self.user:
            user_str = f"{self.user}'s"
        elif self.customer:
            user_str = f"{self.customer}'s"
        else:
            user_str = "Guest"
        return f"{user_str} cart - {self.product.name} (Qty: {self.quantity})"

    def calculate_total_price(self):
        # Use the product's display price (handles sale prices)
        return self.quantity * self.product.get_display_price()

    def save(self, *args, **kwargs):
        # Ensure either user, customer or session_key is provided
        if not self.user and not self.customer and not self.session_key:
            raise ValueError("Either user, customer or session_key must be provided")

        # Enforce quantity limits based on product settings
        if self.quantity < self.product.min_purchase:
            self.quantity = self.product.min_purchase
        elif self.quantity > self.product.max_purchase:
            self.quantity = self.product.max_purchase

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'shopcart'
        managed = True
        verbose_name = 'shopcart'
        verbose_name_plural = 'shopcarts'
        ordering = ['-date_added']

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
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded')
    )

    order_no = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    payment = models.ForeignKey("PaymentInfo", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Financial details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Payment details
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Shipping details
    shipping_address = models.TextField(blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)

    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    def calculate_total(self):
        """Calculate the total order amount"""
        self.subtotal = sum(item.get_total() for item in self.order_items.all())
        self.total = self.subtotal + self.shipping_cost + self.tax - self.discount
        return self.total

    def mark_as_paid(self):
        """Mark the order as paid"""
        self.is_paid = True
        self.paid_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Order #{self.order_no} - {self.customer.first_name} {self.customer.last_name} ({self.status})"

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_total(self):
        """Calculate the total price for this item"""
        return (self.price * self.quantity) - self.discount

    def __str__(self):
        return f"{self.product.name} (Qty: {self.quantity}) - Order {self.order.order_no}"

    class Meta:
        ordering = ['id']




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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    guest_email = models.EmailField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.product.name}"
        elif self.customer:
            return f"{self.customer.first_name} - {self.product.name}"
        else:
            return f"Guest ({self.guest_email or 'unknown'}) - {self.product.name}"

    @classmethod
    def add_product(cls, product, user=None, customer=None, guest_email=None, session_key=None):
        """Add a product to a wishlist"""
        # Determine which identifier to use
        if user:
            # Check if product is already in wishlist for this user
            if not cls.objects.filter(user=user, product=product).exists():
                return cls.objects.create(user=user, product=product)
        elif customer:
            # Check if product is already in wishlist for this customer
            if not cls.objects.filter(customer=customer, product=product).exists():
                return cls.objects.create(customer=customer, product=product)
        elif guest_email:
            # Check if product is already in wishlist for this email
            if not cls.objects.filter(guest_email=guest_email, product=product).exists():
                return cls.objects.create(guest_email=guest_email, product=product)
        elif session_key:
            # Check if product is already in wishlist for this session
            if not cls.objects.filter(session_key=session_key, product=product).exists():
                return cls.objects.create(session_key=session_key, product=product)
        return None

    @classmethod
    def remove_product(cls, product, user=None, customer=None, guest_email=None, session_key=None):
        """Remove a product from a wishlist"""
        filters = {'product': product}

        if user:
            filters['user'] = user
        elif customer:
            filters['customer'] = customer
        elif guest_email:
            filters['guest_email'] = guest_email
        elif session_key:
            filters['session_key'] = session_key
        else:
            return False

        return cls.objects.filter(**filters).delete()[0] > 0

    def save(self, *args, **kwargs):
        # Ensure at least one identifier is provided
        if not self.user and not self.customer and not self.guest_email and not self.session_key:
            raise ValueError("At least one of user, customer, guest_email, or session_key must be provided")
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'wishlist'
        managed = True
        verbose_name = 'wishlist'
        verbose_name_plural = 'wishlists'
        ordering = ['-added_at']
        # Ensure a product can only be in a wishlist once per user/customer/guest
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                condition=models.Q(user__isnull=False),
                name='unique_user_product'
            ),
            models.UniqueConstraint(
                fields=['customer', 'product'],
                condition=models.Q(customer__isnull=False),
                name='unique_customer_product'
            ),
            models.UniqueConstraint(
                fields=['guest_email', 'product'],
                condition=models.Q(guest_email__isnull=False),
                name='unique_guest_email_product'
            ),
            models.UniqueConstraint(
                fields=['session_key', 'product'],
                condition=models.Q(session_key__isnull=False),
                name='unique_session_key_product'
            ),
        ]

# Review model
class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES, default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=100, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Ensure either user or customer is provided
        if not self.user and not self.customer:
            raise ValueError("Either user or customer must be provided")

        # Check if this is a verified purchase
        if self.user:
            # Check if user has purchased this product
            self.is_verified_purchase = OrderItem.objects.filter(
                order__customer__user=self.user,
                product=self.product,
                order__is_paid=True
            ).exists()
        elif self.customer:
            # Check if customer has purchased this product
            self.is_verified_purchase = OrderItem.objects.filter(
                order__customer=self.customer,
                product=self.product,
                order__is_paid=True
            ).exists()

        super().save(*args, **kwargs)

        # Update product rating
        self.update_product_rating()

    def update_product_rating(self):
        """Update the product's average rating"""
        avg_rating = Review.objects.filter(
            product=self.product,
            is_approved=True
        ).aggregate(models.Avg('rating'))['rating__avg'] or 0

        self.product.rating = avg_rating
        self.product.save(update_fields=['rating'])

    def get_reviewer_name(self):
        """Get the name of the reviewer"""
        if self.user:
            return self.user.get_full_name() or self.user.username
        elif self.customer:
            return f"{self.customer.first_name} {self.customer.last_name}"
        return "Anonymous"

    def __str__(self):
        reviewer = self.get_reviewer_name()
        return f"{reviewer} - {self.product.name} - {self.rating} stars"

    class Meta:
        db_table = 'review'
        managed = True
        verbose_name = 'review'
        verbose_name_plural = 'reviews'
        ordering = ['-created_at']
        # Ensure a user/customer can only review a product once
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                condition=models.Q(user__isnull=False),
                name='unique_user_product_review'
            ),
            models.UniqueConstraint(
                fields=['customer', 'product'],
                condition=models.Q(customer__isnull=False),
                name='unique_customer_product_review'
            ),
        ]


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

class GuestProfile(models.Model):
    """Model to track guest users and their preferences"""
    email = models.EmailField(unique=True)
    newsletter_subscribed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    last_action = models.CharField(max_length=50, default='browse')  # browse, cart, wishlist, etc.
    conversion_attempts = models.IntegerField(default=0)  # track how many times we try to convert to full user

    def __str__(self):
        return f"Guest: {self.email}"

    class Meta:
        verbose_name = "Guest Profile"
        verbose_name_plural = "Guest Profiles"