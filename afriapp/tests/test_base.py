from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from afriapp.models import Customer, Product, Category, Service, ShopCart, Order, OrderItem, PaymentInfo
from logistics.models import DeliveryZone, DeliveryPartner, Shipment
import json
from decimal import Decimal

class BaseTestCase(TestCase):
    """Base test case with common setup for all API tests"""
    
    def setUp(self):
        """Set up test data that will be used across all tests"""
        self.client = Client()
        
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='adminpassword123'
        )
        
        self.regular_user = User.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password='userpassword123'
        )
        
        # Create customer profile for regular user
        self.customer = Customer.objects.create(
            user=self.regular_user,
            first_name='Test',
            last_name='User',
            email='user@example.com',
            phone_number='1234567890'
        )
        
        # Create product categories and services
        self.service = Service.objects.create(
            name='Test Service',
            description='Test service description'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description',
            service=self.service
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name='Test Product 1',
            price=Decimal('19.99'),
            description='Test product 1 description',
            category=self.category,
            stock_quantity=100,
            featured=True
        )
        
        self.product2 = Product.objects.create(
            name='Test Product 2',
            price=Decimal('29.99'),
            description='Test product 2 description',
            category=self.category,
            stock_quantity=50
        )
        
        # Create delivery zones and partners for logistics tests
        self.delivery_zone = DeliveryZone.objects.create(
            name='Test Zone',
            description='Test delivery zone',
            base_fee=Decimal('5.99'),
            is_active=True
        )
        
        self.delivery_partner = DeliveryPartner.objects.create(
            name='Test Partner',
            contact_person='Contact Person',
            phone='9876543210',
            email='partner@example.com',
            is_active=True
        )
    
    def create_authenticated_client(self, user=None):
        """Create a client that's already authenticated with the given user"""
        if user is None:
            user = self.regular_user
            
        client = Client()
        client.login(username=user.username, password='userpassword123' if user == self.regular_user else 'adminpassword123')
        return client
    
    def create_test_cart(self, user=None, product=None, quantity=1):
        """Create a test cart item"""
        if user is None:
            user = self.regular_user
        if product is None:
            product = self.product1
            
        return ShopCart.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            paid_order=False,
            basket_no='test-basket-123'
        )
    
    def create_test_order(self, customer=None):
        """Create a test order"""
        if customer is None:
            customer = self.customer
            
        return Order.objects.create(
            customer=customer,
            total_amount=Decimal('49.99'),
            subtotal=Decimal('45.99'),
            vat=Decimal('4.00'),
            total_price=Decimal('49.99'),
            shipping_cost=0,
            is_paid=True,
            status='Pending'
        )
    
    def create_test_shipment(self, order=None):
        """Create a test shipment"""
        if order is None:
            order = self.create_test_order()
            
        return Shipment.objects.create(
            order=order,
            tracking_number='TRACK123456789',
            delivery_partner=self.delivery_partner,
            delivery_zone=self.delivery_zone,
            status='pending',
            shipping_cost=Decimal('5.99')
        )
