from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from afriapp.models import Customer, Product, Category, Service
import json

class APIEndpointTestCase(TestCase):
    """Test case for API endpoints without relying on database operations"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpassword123'
        )
        
        # Create a customer profile
        self.customer = Customer.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            phone_number='1234567890'
        )
        
        # Create a service
        self.service = Service.objects.create(
            name='Test Service',
            description='Test service description'
        )
        
        # Create a category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description',
            service=self.service
        )
        
        # Create a product
        self.product = Product.objects.create(
            name='Test Product',
            price=19.99,
            description='Test product description',
            category=self.category,
            stock_quantity=100
        )
        
        # Create a client
        self.client = Client()
    
    def test_index_view(self):
        """Test the index view"""
        url = reverse('index')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is used
        self.assertTemplateUsed(response, 'index.html')
    
    def test_shop_view(self):
        """Test the shop view"""
        url = reverse('shop')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is used
        self.assertTemplateUsed(response, 'shop.html')
        
        # Check that products are in context
        self.assertIn('products', response.context)
    
    def test_product_detail_view(self):
        """Test the product detail view"""
        url = reverse('product', args=[self.product.id])
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is used
        self.assertTemplateUsed(response, 'product.html')
        
        # Check that product is in context
        self.assertIn('product', response.context)
        self.assertEqual(response.context['product'], self.product)
    
    def test_cart_view_unauthenticated(self):
        """Test the cart view for unauthenticated users"""
        url = reverse('cart')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is used
        self.assertTemplateUsed(response, 'cart.html')
    
    def test_cart_view_authenticated(self):
        """Test the cart view for authenticated users"""
        # Login the user
        self.client.login(username='testuser@example.com', password='testpassword123')
        
        url = reverse('cart')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is used
        self.assertTemplateUsed(response, 'cart.html')
    
    def test_checkout_view_unauthenticated(self):
        """Test the checkout view for unauthenticated users"""
        url = reverse('checkout')
        response = self.client.get(url)
        
        # Check redirect to login page
        self.assertRedirects(response, reverse('login') + '?next=' + url)
    
    def test_checkout_view_authenticated(self):
        """Test the checkout view for authenticated users"""
        # Login the user
        self.client.login(username='testuser@example.com', password='testpassword123')
        
        url = reverse('checkout')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is used
        self.assertTemplateUsed(response, 'checkout.html')
    
    def test_login_view(self):
        """Test the login view"""
        url = reverse('login')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is used
        self.assertTemplateUsed(response, 'login.html')
        
        # Test login with valid credentials
        data = {
            'username': 'testuser@example.com',
            'password': 'testpassword123'
        }
        
        response = self.client.post(url, data)
        
        # Check redirect to index page
        self.assertRedirects(response, reverse('index'))
        
        # Test login with invalid credentials
        data = {
            'username': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data)
        
        # Check redirect to login page
        self.assertRedirects(response, reverse('login'))
    
    def test_signup_view(self):
        """Test the signup view"""
        url = reverse('signupform')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is used
        self.assertTemplateUsed(response, 'signup.html')
        
        # Test signup with valid data
        data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'newuserpassword123',
            'password2': 'newuserpassword123'
        }
        
        response = self.client.post(url, data)
        
        # Check redirect to index page
        self.assertRedirects(response, reverse('index'))
        
        # Verify user was created
        self.assertTrue(User.objects.filter(username='newuser@example.com').exists())
        
        # Verify customer profile was created
        self.assertTrue(Customer.objects.filter(email='newuser@example.com').exists())
