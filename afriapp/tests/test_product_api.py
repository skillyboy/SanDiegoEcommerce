from django.test import TestCase
from django.urls import reverse
from afriapp.models import Product, Category, Service
from .test_base import BaseTestCase
import json

class ProductAPITestCase(BaseTestCase):
    """Test case for product-related APIs"""
    
    def test_index_view(self):
        """Test the index view displays featured products"""
        url = reverse('index')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that featured products are in context
        self.assertIn('featured', response.context)
        self.assertIn(self.product1, response.context['featured'])
        self.assertNotIn(self.product2, response.context['featured'])  # Not featured
    
    def test_shop_view(self):
        """Test the shop view displays all products"""
        url = reverse('shop')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that all products are in context
        self.assertIn('products', response.context)
        self.assertIn(self.product1, response.context['products'])
        self.assertIn(self.product2, response.context['products'])
    
    def test_shop_view_with_category_filter(self):
        """Test the shop view with category filter"""
        url = reverse('shop')
        response = self.client.get(f"{url}?category_id={self.category.id}")
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that only products from the specified category are in context
        self.assertIn('products', response.context)
        self.assertIn(self.product1, response.context['products'])
        self.assertIn(self.product2, response.context['products'])
        
        # Create another category and product
        other_category = Category.objects.create(
            name='Other Category',
            description='Other category description',
            service=self.service
        )
        
        other_product = Product.objects.create(
            name='Other Product',
            price=39.99,
            description='Other product description',
            category=other_category,
            stock_quantity=20
        )
        
        # Test filtering again
        response = self.client.get(f"{url}?category_id={self.category.id}")
        
        # Check that only products from the specified category are in context
        self.assertIn(self.product1, response.context['products'])
        self.assertIn(self.product2, response.context['products'])
        self.assertNotIn(other_product, response.context['products'])
    
    def test_product_detail_view(self):
        """Test the product detail view"""
        url = reverse('product', args=[self.product1.id])
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct product is in context
        self.assertIn('product', response.context)
        self.assertEqual(response.context['product'], self.product1)
    
    def test_product_detail_view_nonexistent_product(self):
        """Test the product detail view with a nonexistent product ID"""
        url = reverse('product', args=[999])  # Nonexistent ID
        response = self.client.get(url)
        
        # Check response status (should be 404)
        self.assertEqual(response.status_code, 404)
    
    def test_search_products(self):
        """Test the product search functionality"""
        url = reverse('search_products')
        
        # Search for "Test Product 1"
        response = self.client.get(f"{url}?q=Test Product 1")
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that only matching products are in context
        self.assertIn('products', response.context)
        self.assertIn(self.product1, response.context['products'])
        self.assertNotIn(self.product2, response.context['products'])
        
        # Search for "Test" (should match both products)
        response = self.client.get(f"{url}?q=Test")
        
        # Check that both products are in context
        self.assertIn(self.product1, response.context['products'])
        self.assertIn(self.product2, response.context['products'])
    
    def test_add_to_wishlist(self):
        """Test adding a product to wishlist"""
        # Login first
        client = self.create_authenticated_client()
        
        url = reverse('add_to_wishlist')
        data = {
            'product_id': self.product1.id
        }
        
        response = client.post(url, data)
        
        # Check response status and content
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify product was added to wishlist
        self.assertTrue(self.regular_user.wishlist_set.filter(products=self.product1).exists())
