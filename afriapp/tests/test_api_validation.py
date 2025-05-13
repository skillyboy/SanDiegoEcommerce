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

class APIValidationTestCase(BaseTestCase):
    """Test case for validating data correlation between different parts of the system"""
    
    def setUp(self):
        """Set up test data specific to API validation tests"""
        super().setUp()
        
        # Create a complete order with payment and shipment
        self.payment_info = PaymentInfo.objects.create(
            user=self.regular_user,
            amount=Decimal('49.99'),
            basket_no='test-basket-api',
            pay_code='test-pay-code-api',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            address='123 Test St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country',
            payment_method='credit_card',
            paid_order=True
        )
        
        self.order = Order.objects.create(
            customer=self.customer,
            payment=self.payment_info,
            total_amount=Decimal('49.99'),
            subtotal=Decimal('45.99'),
            vat=Decimal('4.00'),
            total_price=Decimal('49.99'),
            shipping_cost=0,
            is_paid=True,
            status='Pending',
            shipping_address='123 Test St, Test City, Test State, 12345, Test Country'
        )
        
        self.order_item1 = OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
        
        self.order_item2 = OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=1,
            price=self.product2.price
        )
        
        self.shipment = Shipment.objects.create(
            order=self.order,
            tracking_number='TRACK-API-TEST',
            delivery_partner=self.delivery_partner,
            delivery_zone=self.delivery_zone,
            status='in_transit',
            shipping_cost=Decimal('5.99'),
            estimated_delivery=timezone.now() + timezone.timedelta(days=3)
        )
        
        # Create shipment updates
        self.shipment_update1 = ShipmentUpdate.objects.create(
            shipment=self.shipment,
            status='pending',
            location='Warehouse',
            notes='Order received',
            timestamp=timezone.now() - timezone.timedelta(days=2)
        )
        
        self.shipment_update2 = ShipmentUpdate.objects.create(
            shipment=self.shipment,
            status='in_transit',
            location='Distribution Center',
            notes='Shipment is now in transit',
            timestamp=timezone.now() - timezone.timedelta(days=1)
        )
    
    def test_order_payment_correlation(self):
        """Test that order and payment information are correctly correlated"""
        # Login as the regular user
        client = self.create_authenticated_client()
        
        # Get order detail
        url = reverse('order_detail', args=[self.order.id])
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that order in context has correct payment info
        self.assertIn('order', response.context)
        order = response.context['order']
        self.assertEqual(order.payment, self.payment_info)
        self.assertEqual(order.total_amount, self.payment_info.amount)
        
        # Check that payment info has the correct user
        self.assertEqual(self.payment_info.user, self.regular_user)
        
        # Check that order has the correct customer
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.customer.user, self.regular_user)
    
    def test_order_items_correlation(self):
        """Test that order items correctly reflect the products and quantities"""
        # Login as the regular user
        client = self.create_authenticated_client()
        
        # Get order detail
        url = reverse('order_detail', args=[self.order.id])
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that order items in context are correct
        self.assertIn('order_items', response.context)
        order_items = response.context['order_items']
        
        # Verify there are 2 order items
        self.assertEqual(len(order_items), 2)
        
        # Create a dictionary of product IDs to quantities for easy checking
        item_dict = {item.product.id: item.quantity for item in order_items}
        
        # Verify product1 has quantity 2
        self.assertIn(self.product1.id, item_dict)
        self.assertEqual(item_dict[self.product1.id], 2)
        
        # Verify product2 has quantity 1
        self.assertIn(self.product2.id, item_dict)
        self.assertEqual(item_dict[self.product2.id], 1)
        
        # Verify total price calculation
        expected_total = (self.product1.price * 2) + (self.product2.price * 1)
        self.assertEqual(self.order.subtotal, expected_total)
    
    def test_order_shipment_correlation(self):
        """Test that order and shipment information are correctly correlated"""
        # Login as admin to access shipment details
        client = self.create_authenticated_client(self.admin_user)
        
        # Get shipment detail
        url = reverse('logistics:shipment_detail', args=[self.shipment.pk])
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipment in context has correct order
        self.assertIn('shipment', response.context)
        shipment = response.context['shipment']
        self.assertEqual(shipment.order, self.order)
        
        # Check that shipment has correct delivery partner and zone
        self.assertEqual(shipment.delivery_partner, self.delivery_partner)
        self.assertEqual(shipment.delivery_zone, self.delivery_zone)
        
        # Check that shipment status is correct
        self.assertEqual(shipment.status, 'in_transit')
    
    def test_shipment_updates_correlation(self):
        """Test that shipment updates are correctly associated with the shipment"""
        # Login as admin to access shipment details
        client = self.create_authenticated_client(self.admin_user)
        
        # Get shipment detail
        url = reverse('logistics:shipment_detail', args=[self.shipment.pk])
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that updates in context are correct
        self.assertIn('updates', response.context)
        updates = response.context['updates']
        
        # Verify there are 2 updates
        self.assertEqual(len(updates), 2)
        
        # Verify the updates are for the correct shipment
        for update in updates:
            self.assertEqual(update.shipment, self.shipment)
        
        # Verify the latest update matches the shipment status
        latest_update = updates[0]  # Assuming ordered by -timestamp
        self.assertEqual(latest_update.status, self.shipment.status)
    
    def test_customer_order_correlation(self):
        """Test that customer and order information are correctly correlated"""
        # Login as the regular user
        client = self.create_authenticated_client()
        
        # Get order history
        url = reverse('order_history')
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that orders in context are for the correct customer
        self.assertIn('orders', response.context)
        orders = response.context['orders']
        
        # Verify there is at least one order
        self.assertGreater(len(orders), 0)
        
        # Verify all orders are for the correct customer
        for order in orders:
            self.assertEqual(order.customer, self.customer)
            self.assertEqual(order.customer.user, self.regular_user)
    
    def test_public_tracking_data_correlation(self):
        """Test that public tracking page shows correct shipment and order data"""
        # Access the public tracking page (no login required)
        url = reverse('logistics:track_shipment')
        response = self.client.get(f"{url}?tracking_number={self.shipment.tracking_number}")
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipment in context is correct
        self.assertIn('shipment', response.context)
        shipment = response.context['shipment']
        self.assertEqual(shipment, self.shipment)
        
        # Check that updates in context are correct
        self.assertIn('updates', response.context)
        updates = response.context['updates']
        
        # Verify there are 2 updates
        self.assertEqual(len(updates), 2)
        
        # Verify the updates are for the correct shipment
        for update in updates:
            self.assertEqual(update.shipment, self.shipment)
    
    def test_data_integrity_across_system(self):
        """Test data integrity and correlation across the entire system"""
        # This test verifies that all parts of the system maintain data integrity
        
        # 1. Verify order total matches sum of order items
        order_items_total = sum(item.price * item.quantity for item in OrderItem.objects.filter(order=self.order))
        self.assertEqual(self.order.subtotal, order_items_total)
        
        # 2. Verify order customer matches user's customer profile
        self.assertEqual(self.order.customer, self.regular_user.customer_profile)
        
        # 3. Verify shipment order matches the original order
        self.assertEqual(self.shipment.order, self.order)
        
        # 4. Verify shipment updates are all for the correct shipment
        for update in ShipmentUpdate.objects.filter(shipment=self.shipment):
            self.assertEqual(update.shipment, self.shipment)
        
        # 5. Verify payment info is correctly linked to the order
        self.assertEqual(self.order.payment, self.payment_info)
        
        # 6. Verify payment info user matches order customer's user
        self.assertEqual(self.payment_info.user, self.order.customer.user)
