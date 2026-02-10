from django.test import TestCase
from django.urls import reverse
from afriapp.models import PaymentInfo, Order, ShopCart
from .test_base import BaseTestCase
from unittest.mock import patch, MagicMock
from decimal import Decimal

class PaymentAPITestCase(BaseTestCase):
    """Test case for payment-related APIs"""
    
    @patch('stripe.checkout.Session.create')
    def test_payment_pipeline(self, mock_stripe_session):
        """Test the payment pipeline"""
        # Mock the Stripe checkout session
        mock_session = MagicMock()
        mock_session.url = 'https://stripe.com/checkout/test-session'
        mock_session.id = 'cs_test_123456789'
        mock_stripe_session.return_value = mock_session
        
        # Create a cart item first
        cart_item = self.create_test_cart()
        
        # Login
        client = self.create_authenticated_client()
        
        url = reverse('payment_pipeline')
        data = {
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
            'payment_method': 'card'
        }
        
        response = client.post(url, data)
        
        # Check redirect to Stripe checkout
        self.assertRedirects(response, 'https://stripe.com/checkout/test-session', fetch_redirect_response=False)
        
        # Verify payment info was created
        payment = PaymentInfo.objects.filter(
            user=self.regular_user,
            basket_no='test-basket-123'
        ).first()
        
        self.assertIsNotNone(payment)
        self.assertEqual(payment.first_name, 'Test')
        self.assertEqual(payment.last_name, 'User')
        self.assertEqual(payment.stripe_payment_intent_id, 'cs_test_123456789')
        
        # Verify Stripe session was created with correct parameters
        mock_stripe_session.assert_called_once()
        call_kwargs = mock_stripe_session.call_args[1]
        self.assertEqual(call_kwargs['payment_method_types'], ['card'])
        self.assertEqual(call_kwargs['metadata']['basket_no'], 'test-basket-123')
        self.assertEqual(call_kwargs['metadata']['payment_id'], str(payment.id))
        self.assertEqual(call_kwargs['mode'], 'payment')
    
    @patch('stripe.PaymentIntent.retrieve')
    def test_completed_payment_view(self, mock_payment_intent):
        """Test the completed payment view"""
        # Mock the Stripe payment intent
        mock_intent = MagicMock()
        mock_intent.status = 'succeeded'
        mock_payment_intent.return_value = mock_intent
        
        # Create a cart item and payment info
        cart_item = self.create_test_cart()
        payment = PaymentInfo.objects.create(
            user=self.regular_user,
            amount=1999,  # $19.99 in cents
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
            payment_method='card',
            transaction_id='test-transaction-id',
            stripe_payment_intent_id='pi_test_123456789'
        )
        
        # Login
        client = self.create_authenticated_client()
        
        url = reverse('successpayment')
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Verify order was created
        order = Order.objects.filter(
            customer=self.customer,
            basket_no='test-basket-123'
        ).first()
        
        self.assertIsNotNone(order)
        self.assertTrue(order.is_paid)
        
        # Verify cart items were marked as paid
        cart_item.refresh_from_db()
        self.assertTrue(cart_item.paid_order)
    
    def test_completed_payment_view_no_payment(self):
        """Test the completed payment view with no payment info"""
        # Login without creating payment info
        client = self.create_authenticated_client()
        
        url = reverse('successpayment')
        response = client.get(url)
        
        # Check redirect to cart page
        self.assertRedirects(response, reverse('cart'))
