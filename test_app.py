#!/usr/bin/env python3
"""
Simple tests for the swarm-homepage application
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import ServiceDiscovery, app


class TestServiceDiscovery(unittest.TestCase):
    """Test the ServiceDiscovery class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.discovery = ServiceDiscovery(
            'unix://var/run/docker.sock',
            'http://traefik:8080/api'
        )
    
    def test_extract_service_info_with_valid_labels(self):
        """Test extracting service info from valid container labels"""
        labels = {
            'traefik.enable': 'true',
            'traefik.http.routers.myapp.rule': 'Host(`myapp.example.com`)',
            'homepage.name': 'My App',
            'homepage.description': 'A test application',
            'homepage.category': 'Applications'
        }
        
        result = self.discovery._extract_service_info('myapp', labels)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'My App')
        self.assertEqual(result['url'], 'http://myapp.example.com')
        self.assertEqual(result['description'], 'A test application')
        self.assertEqual(result['category'], 'Applications')
    
    def test_extract_service_info_with_https(self):
        """Test extracting service info with HTTPS"""
        labels = {
            'traefik.enable': 'true',
            'traefik.http.routers.myapp-websecure.rule': 'Host(`secure.example.com`)',
            'traefik.http.routers.myapp-websecure.tls': 'true',
            'homepage.name': 'Secure App'
        }
        
        result = self.discovery._extract_service_info('myapp', labels)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['url'], 'https://secure.example.com')
    
    def test_extract_service_info_disabled_traefik(self):
        """Test that disabled Traefik services are not included"""
        labels = {
            'traefik.enable': 'false',
            'traefik.http.routers.myapp.rule': 'Host(`myapp.example.com`)'
        }
        
        result = self.discovery._extract_service_info('myapp', labels)
        
        self.assertIsNone(result)
    
    def test_extract_service_info_with_custom_url(self):
        """Test extracting service info with custom URL"""
        labels = {
            'traefik.enable': 'true',
            'homepage.url': 'https://custom.example.com',
            'homepage.name': 'Custom App'
        }
        
        result = self.discovery._extract_service_info('myapp', labels)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['url'], 'https://custom.example.com')
    
    def test_extract_service_info_alternative_labels(self):
        """Test extracting service info with swarm.homepage labels"""
        labels = {
            'traefik.enable': 'true',
            'traefik.http.routers.myapp.rule': 'Host(`myapp.example.com`)',
            'swarm.homepage.name': 'Swarm App',
            'swarm.homepage.description': 'Using alternative labels'
        }
        
        result = self.discovery._extract_service_info('myapp', labels)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Swarm App')
        self.assertEqual(result['description'], 'Using alternative labels')
    
    def test_extract_service_info_with_default_description(self):
        """Test that services without description get a default one"""
        labels = {
            'traefik.enable': 'true',
            'traefik.http.routers.myapp.rule': 'Host(`myapp.example.com`)',
            'homepage.name': 'My App'
        }
        
        result = self.discovery._extract_service_info('myapp', labels)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'My App')
        self.assertEqual(result['description'], 'Service available at myapp.example.com')
    
    def test_extract_service_info_minimal_labels(self):
        """Test extracting service info with only required Traefik labels"""
        labels = {
            'traefik.enable': 'true',
            'traefik.http.routers.webapp.rule': 'Host(`webapp.local`)'
        }
        
        result = self.discovery._extract_service_info('webapp-container', labels)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'webapp-container')
        self.assertEqual(result['url'], 'http://webapp.local')
        self.assertEqual(result['description'], 'Service available at webapp.local')
        self.assertEqual(result['category'], 'Services')


class TestFlaskApp(unittest.TestCase):
    """Test Flask application endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_index_endpoint(self):
        """Test the main index page"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Swarm Homepage', response.data)
    
    @patch('app.discovery')
    def test_services_endpoint(self, mock_discovery):
        """Test the services API endpoint"""
        # Mock the discover_services method
        mock_discovery.discover_services.return_value = [
            {
                'name': 'Test Service',
                'url': 'http://test.example.com',
                'description': 'A test service',
                'icon': '',
                'category': 'Applications'
            }
        ]
        
        response = self.client.get('/api/services')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Service')


if __name__ == '__main__':
    unittest.main()
