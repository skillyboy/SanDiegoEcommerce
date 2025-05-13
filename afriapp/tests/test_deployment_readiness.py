import os
import unittest
from django.conf import settings

class DeploymentReadinessTestCase(unittest.TestCase):
    """Test case for checking deployment readiness"""
    
    def test_settings_configuration(self):
        """Test that the settings are properly configured for deployment"""
        # Check that SECRET_KEY is set
        self.assertIsNotNone(settings.SECRET_KEY)
        
        # Check that ALLOWED_HOSTS is set
        self.assertTrue(len(settings.ALLOWED_HOSTS) > 0)
        
        # Check that STATIC_URL is set
        self.assertIsNotNone(settings.STATIC_URL)
        
        # Check that STATIC_ROOT is set
        self.assertIsNotNone(settings.STATIC_ROOT)
        
        # Check that MEDIA_URL is set
        self.assertIsNotNone(settings.MEDIA_URL)
        
        # Check that MEDIA_ROOT is set
        self.assertIsNotNone(settings.MEDIA_ROOT)
    
    def test_required_files_exist(self):
        """Test that required files for deployment exist"""
        # Check that Procfile exists
        self.assertTrue(os.path.exists(os.path.join(settings.BASE_DIR, 'Procfile')))
        
        # Check that requirements.txt exists
        self.assertTrue(os.path.exists(os.path.join(settings.BASE_DIR, 'requirements.txt')))
        
        # Check that .gitignore exists
        self.assertTrue(os.path.exists(os.path.join(settings.BASE_DIR, '.gitignore')))
        
        # Check that manage.py exists
        self.assertTrue(os.path.exists(os.path.join(settings.BASE_DIR, 'manage.py')))
        
        # Check that wsgi.py exists
        self.assertTrue(os.path.exists(os.path.join(settings.BASE_DIR, 'project', 'wsgi.py')))
    
    def test_installed_apps(self):
        """Test that required apps are installed"""
        # Check that django.contrib.admin is installed
        self.assertIn('django.contrib.admin', settings.INSTALLED_APPS)
        
        # Check that django.contrib.auth is installed
        self.assertIn('django.contrib.auth', settings.INSTALLED_APPS)
        
        # Check that django.contrib.contenttypes is installed
        self.assertIn('django.contrib.contenttypes', settings.INSTALLED_APPS)
        
        # Check that django.contrib.sessions is installed
        self.assertIn('django.contrib.sessions', settings.INSTALLED_APPS)
        
        # Check that django.contrib.messages is installed
        self.assertIn('django.contrib.messages', settings.INSTALLED_APPS)
        
        # Check that django.contrib.staticfiles is installed
        self.assertIn('django.contrib.staticfiles', settings.INSTALLED_APPS)
        
        # Check that afriapp is installed
        self.assertIn('afriapp', settings.INSTALLED_APPS)
        
        # Check that logistics is installed
        self.assertIn('logistics', settings.INSTALLED_APPS)
    
    def test_middleware(self):
        """Test that required middleware is installed"""
        # Check that django.middleware.security.SecurityMiddleware is installed
        self.assertIn('django.middleware.security.SecurityMiddleware', settings.MIDDLEWARE)
        
        # Check that django.contrib.sessions.middleware.SessionMiddleware is installed
        self.assertIn('django.contrib.sessions.middleware.SessionMiddleware', settings.MIDDLEWARE)
        
        # Check that django.middleware.common.CommonMiddleware is installed
        self.assertIn('django.middleware.common.CommonMiddleware', settings.MIDDLEWARE)
        
        # Check that django.middleware.csrf.CsrfViewMiddleware is installed
        self.assertIn('django.middleware.csrf.CsrfViewMiddleware', settings.MIDDLEWARE)
        
        # Check that django.contrib.auth.middleware.AuthenticationMiddleware is installed
        self.assertIn('django.contrib.auth.middleware.AuthenticationMiddleware', settings.MIDDLEWARE)
        
        # Check that django.contrib.messages.middleware.MessageMiddleware is installed
        self.assertIn('django.contrib.messages.middleware.MessageMiddleware', settings.MIDDLEWARE)
        
        # Check that django.middleware.clickjacking.XFrameOptionsMiddleware is installed
        self.assertIn('django.middleware.clickjacking.XFrameOptionsMiddleware', settings.MIDDLEWARE)
    
    def test_database_configuration(self):
        """Test that the database is properly configured"""
        # Check that DATABASES is set
        self.assertIsNotNone(settings.DATABASES)
        
        # Check that default database is set
        self.assertIn('default', settings.DATABASES)
    
    def test_stripe_configuration(self):
        """Test that Stripe is properly configured"""
        # Check that STRIPE_PUBLIC_KEY is set
        self.assertIsNotNone(settings.STRIPE_PUBLIC_KEY)
        
        # Check that STRIPE_SECRET_KEY is set
        self.assertIsNotNone(settings.STRIPE_SECRET_KEY)
        
        # Check that STRIPE_WEBHOOK_SECRET is set
        self.assertIsNotNone(settings.STRIPE_WEBHOOK_SECRET)
