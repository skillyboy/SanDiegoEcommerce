"""
Configuration for microservice integration with the main Django application.
This file contains settings and utilities for communicating with the microservice.
"""

import os
import requests
from django.conf import settings

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {name}")

# Microservice connection settings
MICROSERVICE_BASE_URL = os.getenv('MICROSERVICE_BASE_URL', 'http://localhost:8001')
# MICROSERVICE_API_KEY = os.getenv('MICROSERVICE_API_KEY', '')  # Now optional, defaults to empty string
MICROSERVICE_TIMEOUT = int(os.getenv('MICROSERVICE_TIMEOUT', '5'))  # seconds

# API endpoints
API_ENDPOINTS = {
    'farm': f"{MICROSERVICE_BASE_URL}/api/v1/farms",
    'market': f"{MICROSERVICE_BASE_URL}/api/v1/market",
    'thrift': f"{MICROSERVICE_BASE_URL}/api/v1/thrift",
    'orders': f"{MICROSERVICE_BASE_URL}/api/v1/orders",
    'price_discovery': f"{MICROSERVICE_BASE_URL}/api/v1/market/price-discovery",
}

class MicroserviceClient:
    """Client for interacting with the microservice API"""
    
    @staticmethod
    def _get_headers():
        """Get the headers for API requests"""
        headers = {'Content-Type': 'application/json'}
        if MICROSERVICE_API_KEY:
            headers['Authorization'] = f'Bearer {MICROSERVICE_API_KEY}'
        return headers
    
    @classmethod
    def get(cls, endpoint, params=None):
        """Make a GET request to the microservice"""
        try:
            response = requests.get(
                endpoint,
                headers=cls._get_headers(),
                params=params,
                timeout=MICROSERVICE_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if settings.DEBUG:
                print(f"Microservice request error: {e}")
            return {'error': str(e)}
    
    @classmethod
    def post(cls, endpoint, data):
        """Make a POST request to the microservice"""
        try:
            response = requests.post(
                endpoint,
                headers=cls._get_headers(),
                json=data,
                timeout=MICROSERVICE_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if settings.DEBUG:
                print(f"Microservice request error: {e}")
            return {'error': str(e)}
    
    @classmethod
    def get_price_discovery(cls, crop_type):
        """Get price discovery data for a crop type"""
        return cls.get(
            API_ENDPOINTS['price_discovery'],
            params={'crop_type': crop_type}
        )
    
    @classmethod
    def process_thrift_data(cls, data):
        """Process thrift data through the microservice"""
        return cls.post(
            f"{API_ENDPOINTS['thrift']}/process-thrift",
            data={'data': data}
        )
