from django.test import TestCase
from django.urls import reverse
from logistics.models import Shipment, ShipmentUpdate, DeliveryZone, DeliveryPartner
from afriapp.models import Order
from afriapp.tests.test_base import BaseTestCase
import json
from decimal import Decimal

class LogisticsAPITestCase(BaseTestCase):
    """Test case for logistics-related APIs"""
    
    def test_logistics_dashboard_view(self):
        """Test the logistics dashboard view"""
        # Create a test shipment
        shipment = self.create_test_shipment()
        
        # Login as admin
        client = self.create_authenticated_client(self.admin_user)
        
        url = reverse('logistics:dashboard')
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipment counts are in context
        self.assertIn('pending_shipments', response.context)
        self.assertIn('in_transit_shipments', response.context)
        self.assertIn('delivered_shipments', response.context)
        self.assertIn('total_shipments', response.context)
        
        # Verify counts
        self.assertEqual(response.context['pending_shipments'], 1)  # Our test shipment is pending
        self.assertEqual(response.context['total_shipments'], 1)
    
    def test_shipment_list_view(self):
        """Test the shipment list view"""
        # Create a test shipment
        shipment = self.create_test_shipment()
        
        # Login as admin
        client = self.create_authenticated_client(self.admin_user)
        
        url = reverse('logistics:shipment_list')
        response = client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipments are in context
        self.assertIn('shipments', response.context)
        self.assertEqual(len(response.context['shipments']), 1)
        self.assertEqual(response.context['shipments'][0], shipment)
    
    def test_shipment_list_view_with_status_filter(self):
        """Test the shipment list view with status filter"""
        # Create a pending shipment
        pending_shipment = self.create_test_shipment()
        
        # Create an in-transit shipment
        order = self.create_test_order()
        in_transit_shipment = Shipment.objects.create(
            order=order,
            tracking_number='TRACK987654321',
            delivery_partner=self.delivery_partner,
            delivery_zone=self.delivery_zone,
            status='in_transit',
            shipping_cost=Decimal('5.99')
        )
        
        # Login as admin
        client = self.create_authenticated_client(self.admin_user)
        
        # Filter by pending status
        url = reverse('logistics:shipment_list')
        response = client.get(f"{url}?status=pending")
        
        # Check that only pending shipments are in context
        self.assertEqual(len(response.context['shipments']), 1)
        self.assertEqual(response.context['shipments'][0], pending_shipment)
        
        # Filter by in_transit status
        response = client.get(f"{url}?status=in_transit")
        
        # Check that only in-transit shipments are in context
        self.assertEqual(len(response.context['shipments']), 1)
        self.assertEqual(response.context['shipments'][0], in_transit_shipment)
    
    def test_shipment_detail_view(self):
        """Test the shipment detail view"""
        # Create a test shipment
        shipment = self.create_test_shipment()
        
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
        """Test adding a shipment update"""
        # Create a test shipment
        shipment = self.create_test_shipment()
        
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
            status='in_transit'
        ).first()
        
        self.assertIsNotNone(update)
        self.assertEqual(update.location, 'Distribution Center')
        self.assertEqual(update.notes, 'Shipment is now in transit')
        
        # Verify shipment status was updated
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, 'in_transit')
    
    def test_create_shipment(self):
        """Test creating a new shipment"""
        # Create a test order
        order = self.create_test_order()
        
        # Login as admin
        client = self.create_authenticated_client(self.admin_user)
        
        url = reverse('logistics:create_shipment')
        data = {
            'order_id': order.id,
            'tracking_number': 'TRACK123456',
            'delivery_partner': self.delivery_partner.id,
            'delivery_zone': self.delivery_zone.id,
            'shipping_cost': '5.99'
        }
        
        response = client.post(url, data)
        
        # Verify shipment was created
        shipment = Shipment.objects.filter(
            order=order,
            tracking_number='TRACK123456'
        ).first()
        
        self.assertIsNotNone(shipment)
        self.assertEqual(shipment.delivery_partner, self.delivery_partner)
        self.assertEqual(shipment.delivery_zone, self.delivery_zone)
        self.assertEqual(shipment.shipping_cost, Decimal('5.99'))
        self.assertEqual(shipment.status, 'pending')
        
        # Check redirect to shipment detail page
        self.assertRedirects(response, reverse('logistics:shipment_detail', args=[shipment.pk]))
    
    def test_track_shipment(self):
        """Test the public shipment tracking page"""
        # Create a test shipment
        shipment = self.create_test_shipment()
        
        # Create a shipment update
        update = ShipmentUpdate.objects.create(
            shipment=shipment,
            status='processing',
            location='Warehouse',
            notes='Processing for shipment'
        )
        
        url = reverse('logistics:track_shipment')
        response = self.client.get(f"{url}?tracking_number={shipment.tracking_number}")
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipment and updates are in context
        self.assertIn('shipment', response.context)
        self.assertEqual(response.context['shipment'], shipment)
        self.assertIn('updates', response.context)
        self.assertEqual(len(response.context['updates']), 1)
        self.assertEqual(response.context['updates'][0], update)
    
    def test_track_shipment_invalid_tracking_number(self):
        """Test the tracking page with an invalid tracking number"""
        url = reverse('logistics:track_shipment')
        response = self.client.get(f"{url}?tracking_number=INVALID123")
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that shipment is None in context
        self.assertIn('shipment', response.context)
        self.assertIsNone(response.context['shipment'])
