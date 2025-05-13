from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from afriapp.models import Customer, Product, Category, Service, ShopCart, Order, OrderItem, PaymentInfo
from logistics.models import DeliveryZone, DeliveryPartner, Shipment, ShipmentUpdate
from .test_base import BaseTestCase
import json
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.utils import timezone

class EndToEndFlowTestCase(BaseTestCase):
    """Test case for the complete end-to-end flow from account creation to shopping to payment to logistics"""
    
    def test_complete_flow_new_user(self):
        """Test the complete flow for a new user from signup to order to shipment"""
        client = Client()
        
        # Step 1: Create a new user account
        signup_url = reverse('signupform')
        signup_data = {
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'newcustomer@example.com',
            'password1': 'newcustomerpass123',
            'password2': 'newcustomerpass123'
        }
        
        response = client.post(signup_url, signup_data)
        
        # Check redirect to index page on success
        self.assertRedirects(response, reverse('index'))
        
        # Verify user was created
        new_user = User.objects.get(username='newcustomer@example.com')
        self.assertIsNotNone(new_user)
        
        # Verify customer profile was created
        new_customer = Customer.objects.get(email='newcustomer@example.com')
        self.assertIsNotNone(new_customer)
        self.assertEqual(new_customer.first_name, 'New')
        self.assertEqual(new_customer.last_name, 'Customer')
        
        # Step 2: Add products to cart
        add_to_cart_url = reverse('add_to_cart', args=[self.product1.id])
        cart_data = {
            'quantity': 2
        }
        
        response = client.post(add_to_cart_url, cart_data)
        
        # Check redirect to cart page
        self.assertRedirects(response, reverse('cart'))
        
        # Add another product to cart
        add_to_cart_url2 = reverse('add_to_cart', args=[self.product2.id])
        cart_data2 = {
            'quantity': 1
        }
        
        response = client.post(add_to_cart_url2, cart_data2)
        
        # Verify cart items were added
        cart_items = ShopCart.objects.filter(
            user=new_user,
            paid_order=False
        )
        
        self.assertEqual(cart_items.count(), 2)
        
        # Step 3: Go to checkout
        checkout_url = reverse('checkout')
        response = client.get(checkout_url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Submit payment information
        with patch('stripe.checkout.Session.create') as mock_stripe_session:
            # Mock the Stripe session creation
            mock_stripe_session.return_value = MagicMock(id='test_session_e2e')
            
            payment_url = reverse('payment_pipeline')
            payment_data = {
                'basket_no': 'test-basket-e2e',
                'shipping_option': 'standard',
                'first_name': 'New',
                'last_name': 'Customer',
                'phone': '9876543210',
                'address': '456 New St',
                'city': 'New City',
                'state': 'New State',
                'postal_code': '54321',
                'country': 'New Country',
                'payment_method': 'credit_card'
            }
            
            response = client.post(payment_url, payment_data)
            
            # Check response status and content
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.content)
            self.assertIn('id', response_data)
            self.assertEqual(response_data['id'], 'test_session_e2e')
        
        # Step 5: Complete payment and create order
        # First, verify payment info was created
        payment_info = PaymentInfo.objects.filter(
            user=new_user,
            basket_no='test-basket-e2e',
            paid_order=False
        ).first()
        
        self.assertIsNotNone(payment_info)
        
        # Now simulate payment completion
        success_url = reverse('successpayment')
        response = client.get(success_url)
        
        # Check redirect to order history page
        self.assertRedirects(response, reverse('order_history'))
        
        # Verify order was created
        order = Order.objects.filter(
            customer=new_customer,
            payment=payment_info,
            is_paid=True
        ).first()
        
        self.assertIsNotNone(order)
        
        # Verify order items were created
        order_items = OrderItem.objects.filter(order=order)
        self.assertEqual(order_items.count(), 2)
        
        # Verify cart items were marked as paid
        updated_cart_items = ShopCart.objects.filter(user=new_user)
        for item in updated_cart_items:
            self.assertTrue(item.paid_order)
        
        # Step 6: Create shipment for the order (as admin)
        admin_client = self.create_authenticated_client(self.admin_user)
        
        create_shipment_url = reverse('logistics:create_shipment')
        shipment_data = {
            'order_id': order.id,
            'tracking_number': 'TRACK-E2E-TEST',
            'delivery_partner': self.delivery_partner.id,
            'delivery_zone': self.delivery_zone.id,
            'shipping_cost': '5.99'
        }
        
        response = admin_client.post(create_shipment_url, shipment_data)
        
        # Verify shipment was created
        shipment = Shipment.objects.get(tracking_number='TRACK-E2E-TEST')
        self.assertEqual(shipment.order, order)
        self.assertEqual(shipment.status, 'pending')
        
        # Step 7: Update shipment status (as admin)
        update_url = reverse('logistics:add_shipment_update', args=[shipment.pk])
        
        # Update to processing
        admin_client.post(update_url, {
            'status': 'processing',
            'location': 'Warehouse',
            'notes': 'Processing the shipment'
        })
        
        # Update to in_transit
        admin_client.post(update_url, {
            'status': 'in_transit',
            'location': 'Distribution Center',
            'notes': 'Shipment is now in transit'
        })
        
        # Update to delivered
        admin_client.post(update_url, {
            'status': 'delivered',
            'location': 'Customer Address',
            'notes': 'Successfully delivered to customer'
        })
        
        # Verify final shipment status
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, 'delivered')
        
        # Step 8: Customer tracks shipment
        track_url = reverse('logistics:track_shipment')
        response = client.get(f"{track_url}?tracking_number=TRACK-E2E-TEST")
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipment and updates are in context
        self.assertIn('shipment', response.context)
        self.assertEqual(response.context['shipment'], shipment)
        self.assertIn('updates', response.context)
        self.assertEqual(len(response.context['updates']), 3)  # All 3 status updates
    
    def test_complete_flow_guest_to_user(self):
        """Test the complete flow starting as a guest user, then converting to registered user"""
        client = Client()
        
        # Step 1: Add products to cart as guest
        client.get('/')  # Make a request to create a session
        session_key = client.session.session_key
        
        add_to_cart_url = reverse('add_to_cart', args=[self.product1.id])
        cart_data = {
            'quantity': 3
        }
        
        response = client.post(add_to_cart_url, cart_data)
        
        # Check redirect to cart page
        self.assertRedirects(response, reverse('cart'))
        
        # Verify guest cart item was created
        guest_cart_item = ShopCart.objects.filter(
            user=None,
            session_key=session_key,
            product=self.product1,
            paid_order=False
        ).first()
        
        self.assertIsNotNone(guest_cart_item)
        self.assertEqual(guest_cart_item.quantity, 3)
        
        # Step 2: Try to access checkout (should redirect to login)
        checkout_url = reverse('checkout')
        response = client.get(checkout_url)
        
        # Check redirect to login page
        self.assertRedirects(response, reverse('login') + '?next=' + checkout_url)
        
        # Step 3: Create a new user account
        signup_url = reverse('signupform')
        signup_data = {
            'first_name': 'Guest',
            'last_name': 'User',
            'email': 'guestuser@example.com',
            'password1': 'guestuserpass123',
            'password2': 'guestuserpass123'
        }
        
        response = client.post(signup_url, signup_data)
        
        # Check redirect to index page on success
        self.assertRedirects(response, reverse('index'))
        
        # Verify user was created
        new_user = User.objects.get(username='guestuser@example.com')
        self.assertIsNotNone(new_user)
        
        # Verify customer profile was created
        new_customer = Customer.objects.get(email='guestuser@example.com')
        self.assertIsNotNone(new_customer)
        
        # Step 4: Verify guest cart was transferred to user
        user_cart_item = ShopCart.objects.filter(
            user=new_user,
            product=self.product1,
            paid_order=False
        ).first()
        
        self.assertIsNotNone(user_cart_item)
        self.assertEqual(user_cart_item.quantity, 3)
        
        # Step 5: Now proceed with checkout and payment as in the previous test
        # The rest of the flow would be identical to the previous test
        
        # This demonstrates that guest users can add items to cart and then
        # register to complete their purchase, with their cart being preserved
    
    def test_complete_flow_existing_user(self):
        """Test the complete flow for an existing user"""
        # This would be similar to test_complete_flow_new_user but starting with login
        # instead of signup, and using the existing self.regular_user
        
        client = Client()
        
        # Step 1: Login with existing user
        login_url = reverse('login')
        login_data = {
            'username': 'user@example.com',
            'password': 'userpassword123'
        }
        
        response = client.post(login_url, login_data)
        
        # Check redirect to index page on success
        self.assertRedirects(response, reverse('index'))
        
        # The rest of the flow would be identical to test_complete_flow_new_user
        # starting from Step 2: Add products to cart
