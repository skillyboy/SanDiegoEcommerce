from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from afriapp.models import Customer, Product, Category, Service, ShopCart, Order, OrderItem, PaymentInfo
from logistics.models import DeliveryZone, DeliveryPartner, Shipment
from .test_base import BaseTestCase
import json
from decimal import Decimal
from unittest.mock import patch, MagicMock

class ShoppingFlowTestCase(BaseTestCase):
    """Test case for the complete shopping flow from adding to cart to checkout to payment"""
    
    def test_guest_add_to_cart(self):
        """Test adding a product to cart as a guest user"""
        # Create a client with a session
        client = Client()
        client.get('/')  # Make a request to create a session
        session_key = client.session.session_key
        
        url = reverse('add_to_cart', args=[self.product1.id])
        data = {
            'quantity': 2
        }
        
        response = client.post(url, data)
        
        # Check redirect to cart page
        self.assertRedirects(response, reverse('cart'))
        
        # Verify product was added to cart
        cart_item = ShopCart.objects.filter(
            user=None,
            session_key=session_key,
            product=self.product1,
            paid_order=False
        ).first()
        
        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.quantity, 2)
    
    def test_authenticated_add_to_cart(self):
        """Test adding a product to cart as an authenticated user"""
        # Login first
        client = self.create_authenticated_client()
        
        url = reverse('add_to_cart', args=[self.product1.id])
        data = {
            'quantity': 3
        }
        
        response = client.post(url, data)
        
        # Check redirect to cart page
        self.assertRedirects(response, reverse('cart'))
        
        # Verify product was added to cart
        cart_item = ShopCart.objects.filter(
            user=self.regular_user,
            product=self.product1,
            paid_order=False
        ).first()
        
        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.quantity, 3)
    
    def test_view_cart(self):
        """Test viewing the cart page"""
        # Create a cart item for the user
        cart_item = self.create_test_cart(user=self.regular_user, product=self.product1, quantity=2)
        
        # Login and view cart
        client = self.create_authenticated_client()
        url = reverse('cart')
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that cart items are in context
        self.assertIn('cart_items', response.context)
        self.assertEqual(len(response.context['cart_items']), 1)
        self.assertEqual(response.context['cart_items'][0], cart_item)
        
        # Check that subtotal, vat, and total are in context
        self.assertIn('subtotal', response.context)
        self.assertIn('vat', response.context)
        self.assertIn('total', response.context)
    
    def test_guest_cart_transfer_on_login(self):
        """Test that guest cart items are transferred to user cart on login"""
        # Create a guest cart item
        client = Client()
        client.get('/')  # Make a request to create a session
        session_key = client.session.session_key
        
        guest_cart_item = ShopCart.objects.create(
            user=None,
            session_key=session_key,
            product=self.product1,
            quantity=2,
            paid_order=False
        )
        
        # Login the user using the same client (to maintain session)
        login_url = reverse('login')
        login_data = {
            'username': 'user@example.com',
            'password': 'userpassword123'
        }
        
        response = client.post(login_url, login_data)
        
        # Check that the guest cart item was transferred to the user
        user_cart_item = ShopCart.objects.filter(
            user=self.regular_user,
            product=self.product1,
            paid_order=False
        ).first()
        
        self.assertIsNotNone(user_cart_item)
        self.assertEqual(user_cart_item.quantity, 2)
        
        # Check that the guest cart item was deleted
        self.assertFalse(ShopCart.objects.filter(id=guest_cart_item.id).exists())
    
    def test_checkout_page_authenticated(self):
        """Test accessing the checkout page as an authenticated user with items in cart"""
        # Create a cart item for the user
        cart_item = self.create_test_cart(user=self.regular_user, product=self.product1, quantity=2)
        
        # Login and access checkout
        client = self.create_authenticated_client()
        url = reverse('checkout')
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that cart items are in context
        self.assertIn('cart_items', response.context)
        self.assertEqual(len(response.context['cart_items']), 1)
        
        # Check that customer info is in context
        self.assertIn('customer', response.context)
        self.assertEqual(response.context['customer'], self.customer)
    
    def test_checkout_page_unauthenticated_redirect(self):
        """Test that unauthenticated users are redirected to login when accessing checkout"""
        url = reverse('checkout')
        response = self.client.get(url)
        
        # Check redirect to login page
        self.assertRedirects(response, reverse('login') + '?next=' + url)
    
    @patch('stripe.checkout.Session.create')
    def test_payment_pipeline(self, mock_stripe_session):
        """Test the payment pipeline process"""
        # Mock the Stripe session creation
        mock_stripe_session.return_value = MagicMock(id='test_session_123')
        
        # Create a cart item for the user
        cart_item = self.create_test_cart(user=self.regular_user, product=self.product1, quantity=2)
        
        # Login and submit payment form
        client = self.create_authenticated_client()
        url = reverse('payment_pipeline')
        payment_data = {
            'basket_no': 'test-basket-123',
            'shipping_option': 'standard',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'country': 'Test Country',
            'payment_method': 'credit_card'
        }
        
        response = client.post(url, payment_data)
        
        # Check response status and content
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('id', response_data)
        self.assertEqual(response_data['id'], 'test_session_123')
        
        # Verify payment info was created
        payment_info = PaymentInfo.objects.filter(
            user=self.regular_user,
            basket_no='test-basket-123',
            paid_order=False
        ).first()
        
        self.assertIsNotNone(payment_info)
        self.assertEqual(payment_info.first_name, 'Test')
        self.assertEqual(payment_info.last_name, 'User')
    
    def test_completed_payment_view(self):
        """Test the completed payment view that creates an order"""
        # Create a cart item for the user
        cart_item = self.create_test_cart(user=self.regular_user, product=self.product1, quantity=2)
        
        # Create a payment info record
        payment_info = PaymentInfo.objects.create(
            user=self.regular_user,
            amount=Decimal('39.98'),  # 19.99 * 2
            basket_no='test-basket-123',
            pay_code='test-pay-code',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            address='123 Test St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country',
            payment_method='credit_card',
            paid_order=False
        )
        
        # Login and access the completed payment view
        client = self.create_authenticated_client()
        url = reverse('successpayment')
        response = client.get(url)
        
        # Check redirect to order history page
        self.assertRedirects(response, reverse('order_history'))
        
        # Verify order was created
        order = Order.objects.filter(
            customer=self.customer,
            payment=payment_info,
            is_paid=True
        ).first()
        
        self.assertIsNotNone(order)
        
        # Verify order items were created
        order_item = OrderItem.objects.filter(
            order=order,
            product=self.product1,
            quantity=2
        ).first()
        
        self.assertIsNotNone(order_item)
        
        # Verify cart items were marked as paid
        updated_cart_item = ShopCart.objects.get(id=cart_item.id)
        self.assertTrue(updated_cart_item.paid_order)
    
    def test_order_history_view(self):
        """Test viewing order history"""
        # Create a test order
        order = self.create_test_order(customer=self.customer)
        
        # Create an order item
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
        
        # Login and view order history
        client = self.create_authenticated_client()
        url = reverse('order_history')
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that orders are in context
        self.assertIn('orders', response.context)
        self.assertEqual(len(response.context['orders']), 1)
        self.assertEqual(response.context['orders'][0], order)
    
    def test_order_detail_view(self):
        """Test viewing order details"""
        # Create a test order
        order = self.create_test_order(customer=self.customer)
        
        # Create an order item
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
        
        # Login and view order details
        client = self.create_authenticated_client()
        url = reverse('order_detail', args=[order.id])
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that order and order items are in context
        self.assertIn('order', response.context)
        self.assertEqual(response.context['order'], order)
        self.assertIn('order_items', response.context)
        self.assertEqual(len(response.context['order_items']), 1)
        self.assertEqual(response.context['order_items'][0], order_item)
