from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from afriapp.models import Customer, Product, Category, Service, ShopCart, Order, OrderItem, PaymentInfo
from logistics.models import DeliveryZone, DeliveryPartner, Shipment, ShipmentUpdate
from afriapp.tests.test_base import BaseTestCase
import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

class LogisticsFlowTestCase(BaseTestCase):
    """Test case for the complete logistics flow from order to shipment to tracking"""
    
    def setUp(self):
        """Set up test data specific to logistics flow tests"""
        super().setUp()
        
        # Create a test order
        self.order = self.create_test_order()
        
        # Create order items
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
    
    def test_create_shipment_for_order(self):
        """Test creating a shipment for an order"""
        # Login as admin
        client = self.create_authenticated_client(self.admin_user)
        
        url = reverse('logistics:create_shipment')
        data = {
            'order_id': self.order.id,
            'tracking_number': 'TRACK123456789',
            'delivery_partner': self.delivery_partner.id,
            'delivery_zone': self.delivery_zone.id,
            'shipping_cost': '5.99'
        }
        
        response = client.post(url, data)
        
        # Verify shipment was created
        shipment = Shipment.objects.filter(
            order=self.order,
            tracking_number='TRACK123456789'
        ).first()
        
        self.assertIsNotNone(shipment)
        self.assertEqual(shipment.delivery_partner, self.delivery_partner)
        self.assertEqual(shipment.delivery_zone, self.delivery_zone)
        self.assertEqual(shipment.shipping_cost, Decimal('5.99'))
        self.assertEqual(shipment.status, 'pending')
        
        # Check redirect to shipment detail page
        self.assertRedirects(response, reverse('logistics:shipment_detail', args=[shipment.pk]))
    
    def test_shipment_detail_view(self):
        """Test viewing shipment details"""
        # Create a test shipment
        shipment = self.create_test_shipment(order=self.order)
        
        # Create a shipment update
        update = ShipmentUpdate.objects.create(
            shipment=shipment,
            status='processing',
            location='Warehouse',
            notes='Processing for shipment'
        )
        
        # Login as admin
        client = self.create_authenticated_client(self.admin_user)
        
        url = reverse('logistics:shipment_detail', args=[shipment.pk])
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipment and updates are in context
        self.assertIn('shipment', response.context)
        self.assertEqual(response.context['shipment'], shipment)
        self.assertIn('updates', response.context)
        self.assertEqual(len(response.context['updates']), 1)
        self.assertEqual(response.context['updates'][0], update)
    
    def test_add_shipment_update(self):
        """Test adding an update to a shipment"""
        # Create a test shipment
        shipment = self.create_test_shipment(order=self.order)
        
        # Login as admin
        client = self.create_authenticated_client(self.admin_user)
        
        url = reverse('logistics:add_shipment_update', args=[shipment.pk])
        data = {
            'status': 'in_transit',
            'location': 'Distribution Center',
            'notes': 'Shipment is now in transit'
        }
        
        response = client.post(url, data)
        
        # Check redirect to shipment detail page
        self.assertRedirects(response, reverse('logistics:shipment_detail', args=[shipment.pk]))
        
        # Verify update was created
        update = ShipmentUpdate.objects.filter(
            shipment=shipment,
            status='in_transit',
            location='Distribution Center'
        ).first()
        
        self.assertIsNotNone(update)
        
        # Verify shipment status was updated
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, 'in_transit')
    
    def test_track_shipment_public(self):
        """Test the public shipment tracking page"""
        # Create a test shipment
        shipment = self.create_test_shipment(order=self.order)
        
        # Create multiple shipment updates to test the timeline
        updates = [
            ShipmentUpdate.objects.create(
                shipment=shipment,
                status='pending',
                location='Warehouse',
                notes='Order received',
                timestamp=timezone.now() - timedelta(days=3)
            ),
            ShipmentUpdate.objects.create(
                shipment=shipment,
                status='processing',
                location='Warehouse',
                notes='Processing for shipment',
                timestamp=timezone.now() - timedelta(days=2)
            ),
            ShipmentUpdate.objects.create(
                shipment=shipment,
                status='in_transit',
                location='Distribution Center',
                notes='Shipment is now in transit',
                timestamp=timezone.now() - timedelta(days=1)
            )
        ]
        
        # Update the shipment status to match the latest update
        shipment.status = 'in_transit'
        shipment.save()
        
        # Access the public tracking page
        url = reverse('logistics:track_shipment')
        response = self.client.get(f"{url}?tracking_number={shipment.tracking_number}")
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipment and updates are in context
        self.assertIn('shipment', response.context)
        self.assertEqual(response.context['shipment'], shipment)
        self.assertIn('updates', response.context)
        self.assertEqual(len(response.context['updates']), 3)
    
    def test_track_shipment_invalid_tracking(self):
        """Test tracking with an invalid tracking number"""
        url = reverse('logistics:track_shipment')
        response = self.client.get(f"{url}?tracking_number=INVALID123")
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipment is None in context
        self.assertIn('shipment', response.context)
        self.assertIsNone(response.context['shipment'])
    
    def test_shipment_list_view_with_filters(self):
        """Test the shipment list view with various filters"""
        # Create multiple shipments with different statuses
        pending_shipment = self.create_test_shipment(order=self.order)
        pending_shipment.status = 'pending'
        pending_shipment.save()
        
        # Create another order
        order2 = self.create_test_order()
        
        # Create an in-transit shipment
        in_transit_shipment = Shipment.objects.create(
            order=order2,
            tracking_number='TRACK987654321',
            delivery_partner=self.delivery_partner,
            delivery_zone=self.delivery_zone,
            status='in_transit',
            shipping_cost=Decimal('5.99')
        )
        
        # Create a delivered shipment
        delivered_shipment = Shipment.objects.create(
            order=self.create_test_order(),
            tracking_number='TRACK555555555',
            delivery_partner=self.delivery_partner,
            delivery_zone=self.delivery_zone,
            status='delivered',
            shipping_cost=Decimal('5.99'),
            actual_delivery=timezone.now()
        )
        
        # Login as admin
        client = self.create_authenticated_client(self.admin_user)
        
        # Test without filters (should return all shipments)
        url = reverse('logistics:shipment_list')
        response = client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['shipments']), 3)
        
        # Test with status filter: pending
        response = client.get(f"{url}?status=pending")
        self.assertEqual(len(response.context['shipments']), 1)
        self.assertEqual(response.context['shipments'][0], pending_shipment)
        
        # Test with status filter: in_transit
        response = client.get(f"{url}?status=in_transit")
        self.assertEqual(len(response.context['shipments']), 1)
        self.assertEqual(response.context['shipments'][0], in_transit_shipment)
        
        # Test with status filter: delivered
        response = client.get(f"{url}?status=delivered")
        self.assertEqual(len(response.context['shipments']), 1)
        self.assertEqual(response.context['shipments'][0], delivered_shipment)
        
        # Test with search filter by tracking number
        response = client.get(f"{url}?search=TRACK9876")
        self.assertEqual(len(response.context['shipments']), 1)
        self.assertEqual(response.context['shipments'][0], in_transit_shipment)
    
    def test_complete_order_to_delivery_flow(self):
        """Test the complete flow from order to delivery"""
        # Create a test order
        order = self.create_test_order()
        
        # Create order items
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
        
        # Login as admin
        client = self.create_authenticated_client(self.admin_user)
        
        # Step 1: Create shipment
        create_url = reverse('logistics:create_shipment')
        create_data = {
            'order_id': order.id,
            'tracking_number': 'TRACK-FLOW-TEST',
            'delivery_partner': self.delivery_partner.id,
            'delivery_zone': self.delivery_zone.id,
            'shipping_cost': '5.99'
        }
        
        client.post(create_url, create_data)
        
        # Verify shipment was created
        shipment = Shipment.objects.get(tracking_number='TRACK-FLOW-TEST')
        self.assertEqual(shipment.status, 'pending')
        
        # Step 2: Update to processing
        update_url = reverse('logistics:add_shipment_update', args=[shipment.pk])
        processing_data = {
            'status': 'processing',
            'location': 'Warehouse',
            'notes': 'Processing the shipment'
        }
        
        client.post(update_url, processing_data)
        
        # Verify status updated
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, 'processing')
        
        # Step 3: Update to in_transit
        in_transit_data = {
            'status': 'in_transit',
            'location': 'Distribution Center',
            'notes': 'Shipment is now in transit'
        }
        
        client.post(update_url, in_transit_data)
        
        # Verify status updated
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, 'in_transit')
        
        # Step 4: Update to out_for_delivery
        out_for_delivery_data = {
            'status': 'out_for_delivery',
            'location': 'Local Delivery Center',
            'notes': 'Out for delivery today'
        }
        
        client.post(update_url, out_for_delivery_data)
        
        # Verify status updated
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, 'out_for_delivery')
        
        # Step 5: Update to delivered
        delivered_data = {
            'status': 'delivered',
            'location': 'Customer Address',
            'notes': 'Successfully delivered to customer'
        }
        
        client.post(update_url, delivered_data)
        
        # Verify status updated
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, 'delivered')
        
        # Step 6: Verify tracking page shows all updates
        track_url = reverse('logistics:track_shipment')
        response = self.client.get(f"{track_url}?tracking_number=TRACK-FLOW-TEST")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['shipment'], shipment)
        self.assertEqual(len(response.context['updates']), 5)  # All 5 status updates
