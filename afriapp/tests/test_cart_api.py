from django.test import TestCase, Client
from django.urls import reverse
from afriapp.models import ShopCart
from .test_base import BaseTestCase
import json
from decimal import Decimal

class CartAPITestCase(BaseTestCase):
    """Test case for cart-related APIs"""

    def test_add_to_cart_authenticated(self):
        """Test adding a product to cart as an authenticated user"""
        # Login first
        client = self.create_authenticated_client()

        url = reverse('add_to_cart', args=[self.product1.id])
        data = {
            'quantity': 2
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
        self.assertEqual(cart_item.quantity, 2)

    def test_add_to_cart_unauthenticated(self):
        """Test adding a product to cart as an unauthenticated user"""
        # No login, using anonymous client
        url = reverse('add_to_cart', args=[self.product1.id])
        data = {
            'quantity': 1
        }

        # Post to add to cart
        response = self.client.post(url, data)

        # Check redirect to cart page
        self.assertRedirects(response, reverse('cart'))

        # Verify product was added to cart using session key
        session_key = self.client.session.session_key
        self.assertIsNotNone(session_key)

        cart_item = ShopCart.objects.filter(
            user=None,  # No user for guest shopping
            session_key=session_key,
            product=self.product1,
            paid_order=False
        ).first()

        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.quantity, 1)

    def test_cart_view_authenticated(self):
        """Test viewing the cart as an authenticated user"""
        # Create a cart item first
        self.create_test_cart(quantity=3)

        # Login
        client = self.create_authenticated_client()

        url = reverse('cart')
        response = client.get(url)

        # Check response status
        self.assertEqual(response.status_code, 200)

        # Check that cart items are in context
        self.assertIn('cart', response.context)
        self.assertEqual(len(response.context['cart']), 1)

        # Check cart summary calculations
        self.assertIn('subtotal', response.context)
        self.assertIn('vat', response.context)
        self.assertIn('total', response.context)

        # Expected values (3 * 19.99 = 59.97, VAT = 4.50, Total = 64.47)
        expected_subtotal = round(3 * Decimal('19.99'), 2)
        expected_vat = round(expected_subtotal * Decimal('0.075'), 2)
        expected_total = expected_subtotal + expected_vat

        self.assertAlmostEqual(Decimal(response.context['subtotal']), expected_subtotal, places=2)
        self.assertAlmostEqual(Decimal(response.context['vat']), expected_vat, places=2)
        self.assertAlmostEqual(Decimal(response.context['total']), expected_total, places=2)

    def test_cart_view_guest(self):
        """Test viewing the cart as a guest user"""
        # Create a client with a session
        client = Client()
        client.get('/')  # Make a request to create a session
        session_key = client.session.session_key

        # Create a cart item for the guest user
        ShopCart.objects.create(
            user=None,
            session_key=session_key,
            product=self.product1,
            quantity=2,
            paid_order=False,
            basket_no='test-basket-guest'
        )

        url = reverse('cart')
        response = client.get(url)

        # Check response status
        self.assertEqual(response.status_code, 200)

        # Check that cart items are in context
        self.assertIn('cart', response.context)
        self.assertEqual(len(response.context['cart']), 1)

        # Check cart summary calculations
        self.assertIn('subtotal', response.context)
        self.assertIn('vat', response.context)
        self.assertIn('total', response.context)

        # Expected values (2 * 19.99 = 39.98, VAT = 3.00, Total = 42.98)
        expected_subtotal = round(2 * Decimal('19.99'), 2)
        expected_vat = round(expected_subtotal * Decimal('0.075'), 2)
        expected_total = expected_subtotal + expected_vat

        self.assertAlmostEqual(Decimal(response.context['subtotal']), expected_subtotal, places=2)
        self.assertAlmostEqual(Decimal(response.context['vat']), expected_vat, places=2)
        self.assertAlmostEqual(Decimal(response.context['total']), expected_total, places=2)

    def test_increase_quantity_authenticated(self):
        """Test increasing cart item quantity for authenticated user"""
        # Create a cart item first
        cart_item = self.create_test_cart(quantity=1)

        # Login
        client = self.create_authenticated_client()

        url = reverse('increase_quantity', args=[cart_item.id])
        response = client.post(url)

        # Check response status and content
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['new_quantity'], 2)

        # Verify quantity was increased in database
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

    def test_increase_quantity_guest(self):
        """Test increasing cart item quantity for guest user"""
        # Create a client with a session
        client = Client()
        client.get('/')  # Make a request to create a session
        session_key = client.session.session_key

        # Create a cart item for the guest user
        cart_item = ShopCart.objects.create(
            user=None,
            session_key=session_key,
            product=self.product1,
            quantity=1,
            paid_order=False
        )

        url = reverse('increase_quantity', args=[cart_item.id])
        response = client.post(url)

        # Check response status and content
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['new_quantity'], 2)

        # Verify quantity was increased in database
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

    def test_decrease_quantity_authenticated(self):
        """Test decreasing cart item quantity for authenticated user"""
        # Create a cart item first with quantity 2
        cart_item = self.create_test_cart(quantity=2)

        # Login
        client = self.create_authenticated_client()

        url = reverse('decrease_quantity', args=[cart_item.id])
        response = client.post(url)

        # Check response status and content
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['new_quantity'], 1)

        # Verify quantity was decreased in database
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)

    def test_decrease_quantity_guest(self):
        """Test decreasing cart item quantity for guest user"""
        # Create a client with a session
        client = Client()
        client.get('/')  # Make a request to create a session
        session_key = client.session.session_key

        # Create a cart item for the guest user
        cart_item = ShopCart.objects.create(
            user=None,
            session_key=session_key,
            product=self.product1,
            quantity=2,
            paid_order=False
        )

        url = reverse('decrease_quantity', args=[cart_item.id])
        response = client.post(url)

        # Check response status and content
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['new_quantity'], 1)

        # Verify quantity was decreased in database
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)

    def test_decrease_quantity_minimum(self):
        """Test decreasing cart item quantity when already at minimum (1)"""
        # Create a cart item first with quantity 1
        cart_item = self.create_test_cart(quantity=1)

        # Login
        client = self.create_authenticated_client()

        url = reverse('decrease_quantity', args=[cart_item.id])
        response = client.post(url)

        # Check response status and content
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['new_quantity'], 1)  # Should still be 1

        # Verify quantity is still 1 in database
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)

    def test_remove_from_cart_authenticated(self):
        """Test removing an item from cart for authenticated user"""
        # Create a cart item first
        cart_item = self.create_test_cart()

        # Login
        client = self.create_authenticated_client()

        url = reverse('remove_from_cart', args=[cart_item.id])
        response = client.post(url)

        # Check redirect back to cart page
        self.assertRedirects(response, reverse('cart'))

        # Verify item was removed from database
        self.assertFalse(ShopCart.objects.filter(id=cart_item.id).exists())

    def test_remove_from_cart_guest(self):
        """Test removing an item from cart for guest user"""
        # Create a client with a session
        client = Client()
        client.get('/')  # Make a request to create a session
        session_key = client.session.session_key

        # Create a cart item for the guest user
        cart_item = ShopCart.objects.create(
            user=None,
            session_key=session_key,
            product=self.product1,
            quantity=1,
            paid_order=False
        )

        url = reverse('remove_from_cart', args=[cart_item.id])
        response = client.post(url)

        # Check redirect back to cart page
        self.assertRedirects(response, reverse('cart'))

        # Verify item was removed from database
        self.assertFalse(ShopCart.objects.filter(id=cart_item.id).exists())

    def test_checkout_view(self):
        """Test the checkout view"""
        # Create a cart item first
        self.create_test_cart()

        # Login
        client = self.create_authenticated_client()

        url = reverse('checkout')
        response = client.get(url)

        # Check response status
        self.assertEqual(response.status_code, 200)

        # Check that cart items and customer info are in context
        self.assertIn('cart', response.context)
        self.assertIn('customer', response.context)
        self.assertEqual(response.context['customer'], self.customer)

    def test_checkout_view_empty_cart(self):
        """Test the checkout view with an empty cart"""
        # Login without creating any cart items
        client = self.create_authenticated_client()

        url = reverse('checkout')
        response = client.get(url)

        # Check redirect to cart page
        self.assertRedirects(response, reverse('cart'))
