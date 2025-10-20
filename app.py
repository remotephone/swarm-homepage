#!/usr/bin/env python3
"""
Swarm Homepage - A service discovery dashboard for Docker Swarm with Traefik
"""
import os
import logging
import requests
from flask import Flask, render_template, jsonify
import docker
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
TRAEFIK_API_URL = os.getenv('TRAEFIK_API_URL', 'http://traefik:8080/api')
DOCKER_SOCKET = os.getenv('DOCKER_SOCKET', 'unix://var/run/docker.sock')
REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', '60'))


class ServiceDiscovery:
    """Service discovery handler for Docker Swarm and Traefik"""
    
    def __init__(self, docker_socket: str, traefik_api_url: str):
        self.docker_socket = docker_socket
        self.traefik_api_url = traefik_api_url
        self.docker_client = None
        self._init_docker_client()
    
    def _init_docker_client(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.DockerClient(base_url=self.docker_socket)
            self.docker_client.ping()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.docker_client = None
    
    def get_services_from_docker(self) -> List[Dict]:
        """Get services from Docker labels"""
        services = []
        
        if not self.docker_client:
            logger.warning("Docker client not available")
            return services
        
        try:
            # Get all containers
            containers = self.docker_client.containers.list()
            logger.info(f"Found {len(containers)} containers to review")
            for container in containers:
                labels = container.labels
                
                # Look for Traefik labels
                service_info = self._extract_service_info(container.name, labels)
                if service_info:
                    services.append(service_info)
            
            logger.info(f"Found {len(services)} services from Docker")
        except Exception as e:
            logger.error(f"Error getting services from Docker: {e}")
        
        return services
    
    def _extract_service_info(self, container_name: str, labels: Dict) -> Optional[Dict]:
        """Extract service information from container labels"""
        # Check if Traefik is enabled
        traefik_enabled = labels.get('traefik.enable', '').lower() == 'true'
        logger.info(f"Traefik enabled for {container_name}")
        if not traefik_enabled:
            return None
        
        # Try to find service URL from various Traefik label formats
        service_url = None
        service_name = container_name
        
        # Check for common Traefik label patterns
        for key, value in labels.items():
            # Look for router rule with Host
            if 'traefik.http.routers' in key and '.rule' in key:
                # Extract hostname from rule like "Host(`example.com`)"
                logger.info("Found http.routers, extracting hostname from Host rule")
                if 'Host(' in value:
                    hostname = value.split('Host(')[1].split(')')[0].strip('`').strip('"')
                    # Determine protocol
                    protocol = 'https' if 'https' in key or labels.get(key.replace('.rule', '.tls'), '') else 'http'
                    service_url = f"{protocol}://{hostname}"
                    logger.info(f"Got service URL {service_url}")
            
            # Look for service name
            if 'traefik.http.services' in key and '.loadbalancer' in key:
                service_name = key.split('.')[3]  # Extract service name from label
        
        # Fallback: check for custom homepage labels
        if not service_url:
            service_url = labels.get('homepage.url', labels.get('swarm.homepage.url', ''))
            logger.info("no service url found")
        
        if service_url:
            # Extract hostname for default description
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(service_url)
                hostname = parsed_url.hostname or parsed_url.netloc
            except Exception:
                hostname = service_url
            
            # Get values with defaults
            name = labels.get('homepage.name', labels.get('swarm.homepage.name', service_name))
            description = labels.get('homepage.description', labels.get('swarm.homepage.description', ''))
            
            # If no description provided, create a default one
            if not description:
                description = f'Service available at {hostname}'
            
            return {
                'name': name,
                'url': service_url,
                'description': description,
                'icon': labels.get('homepage.icon', labels.get('swarm.homepage.icon', '')),
                'category': labels.get('homepage.category', labels.get('swarm.homepage.category', 'Services'))
            }
        
        return None
    
    def get_services_from_traefik(self) -> List[Dict]:
        """Get services from Traefik API"""
        services = []
        
        try:
            # Try to get routers from Traefik API
            response = requests.get(f"{self.traefik_api_url}/http/routers", timeout=5)
            response.raise_for_status()
            routers = response.json()
            
            for router in routers:
                # Skip internal routers
                if router.get('name', '').startswith('api@'):
                    continue
                
                rule = router.get('rule', '')
                if 'Host(' in rule:
                    hostname = rule.split('Host(')[1].split(')')[0].strip('`').strip('"')
                    protocol = 'https' if router.get('tls') else 'http'
                    
                    services.append({
                        'name': router.get('name', hostname).split('@')[0],
                        'url': f"{protocol}://{hostname}",
                        'description': '',
                        'icon': '',
                        'category': 'Services'
                    })
            
            logger.info(f"Found {len(services)} services from Traefik API")
        except Exception as e:
            logger.warning(f"Could not fetch services from Traefik API: {e}")
        
        return services
    
    def discover_services(self) -> List[Dict]:
        """Discover all services"""
        # Try Docker first (more detailed information from labels)
        services = self.get_services_from_docker()
        
        # If Docker fails or returns nothing, try Traefik API
        if not services:
            services = self.get_services_from_traefik()
        
        # Remove duplicates and sort
        unique_services = {}
        for service in services:
            key = service['url']
            if key not in unique_services:
                unique_services[key] = service
        
        sorted_services = sorted(unique_services.values(), key=lambda x: (x['category'], x['name']))
        
        return sorted_services


# Initialize service discovery
discovery = ServiceDiscovery(DOCKER_SOCKET, TRAEFIK_API_URL)


@app.route('/')
def index():
    """Render the homepage"""
    return render_template('index.html', refresh_interval=REFRESH_INTERVAL)


@app.route('/api/services')
def get_services():
    """API endpoint to get discovered services"""
    services = discovery.discover_services()
    return jsonify(services)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=False)
