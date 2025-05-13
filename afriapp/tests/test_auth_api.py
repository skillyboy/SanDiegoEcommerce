from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from afriapp.models import Customer
from .test_base import BaseTestCase

class AuthenticationAPITestCase(BaseTestCase):
    """Test case for authentication APIs"""
    
    def test_signup_success(self):
        """Test successful user signup"""
        url = reverse('signupform')
        data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'newuserpassword123',
            'password2': 'newuserpassword123'
        }
        
        response = self.client.post(url, data)
        
        # Check redirect to index page on success
        self.assertRedirects(response, reverse('index'))
        
        # Verify user was created
        self.assertTrue(User.objects.filter(username='newuser@example.com').exists())
        
        # Verify customer profile was created
        self.assertTrue(Customer.objects.filter(email='newuser@example.com').exists())
    
    def test_signup_password_mismatch(self):
        """Test signup with mismatched passwords"""
        url = reverse('signupform')
        data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'newuserpassword123',
            'password2': 'differentpassword123'
        }
        
        response = self.client.post(url, data)
        
        # Check redirect back to signup page
        self.assertRedirects(response, reverse('signup'))
        
        # Verify user was not created
        self.assertFalse(User.objects.filter(username='newuser@example.com').exists())
    
    def test_signup_existing_email(self):
        """Test signup with an email that already exists"""
        url = reverse('signupform')
        data = {
            'first_name': 'Duplicate',
            'last_name': 'User',
            'email': 'user@example.com',  # This email already exists from setup
            'password1': 'newuserpassword123',
            'password2': 'newuserpassword123'
        }
        
        response = self.client.post(url, data)
        
        # Check redirect back to signup page
        self.assertRedirects(response, reverse('signup'))
    
    def test_login_success(self):
        """Test successful login"""
        url = reverse('login')
        data = {
            'username': 'user@example.com',
            'password': 'userpassword123'
        }
        
        response = self.client.post(url, data)
        
        # Check redirect to index page on success
        self.assertRedirects(response, reverse('index'))
        
        # Verify user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('login')
        data = {
            'username': 'user@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data)
        
        # Check redirect back to login page
        self.assertRedirects(response, reverse('login'))
        
        # Verify user is not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_logout(self):
        """Test user logout"""
        # First login
        self.client.login(username='user@example.com', password='userpassword123')
        
        # Then logout
        url = reverse('logout')
        response = self.client.get(url)
        
        # Check redirect to login page
        self.assertRedirects(response, reverse('login'))
        
        # Verify user is not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_password_change_success(self):
        """Test successful password change"""
        # Login first
        client = self.create_authenticated_client()
        
        url = reverse('password')
        data = {
            'old_password': 'userpassword123',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456'
        }
        
        response = client.post(url, data)
        
        # Check redirect to index page on success
        self.assertRedirects(response, reverse('index'))
        
        # Verify password was changed by trying to login with new password
        self.client.logout()
        login_success = self.client.login(username='user@example.com', password='newpassword456')
        self.assertTrue(login_success)
    
    def test_password_change_invalid_old_password(self):
        """Test password change with invalid old password"""
        # Login first
        client = self.create_authenticated_client()
        
        url = reverse('password')
        data = {
            'old_password': 'wrongpassword',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456'
        }
        
        response = client.post(url, data)
        
        # Check redirect back to password page
        self.assertRedirects(response, reverse('password'))
