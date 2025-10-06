"""
IoTKit HTTP Module

This module provides HTTP client functionality for sending IoT data via REST API.
"""

import json
import requests
from typing import Dict, Any, Optional
import logging

from .utils import validate_data


class HTTPPublisher:
    """
    HTTP Publisher for sending IoT data via REST API.
    """
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None, 
                 auth_token: Optional[str] = None, timeout: int = 30):
        """
        Initialize HTTP Publisher.
        
        Args:
            url (str): Target URL for sending data
            headers (dict, optional): Additional HTTP headers
            auth_token (str, optional): Bearer token for authentication
            timeout (int): Request timeout in seconds (default: 30)
        """
        self.url = url
        self.timeout = timeout
        self.logger = logging.getLogger(f"iotkit.http.publisher.{url}")
        
        # Set default headers
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'IoTKit/1.0'
        }
        
        # Add custom headers if provided
        if headers:
            self.headers.update(headers)
        
        # Add authentication header if token provided
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
    
    def send(self, data: Dict[str, Any], method: str = 'POST', 
             endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Send data to HTTP endpoint.
        
        Args:
            data (dict): Data to send
            method (str): HTTP method (default: POST)
            endpoint (str, optional): Additional endpoint path
        
        Returns:
            dict: Response data with status and content
        
        Raises:
            ValueError: If data is invalid
            ConnectionError: If request fails
        """
        try:
            # Validate data
            validated_data = validate_data(data)
            
            # Prepare URL
            target_url = self.url
            if endpoint:
                target_url = f"{self.url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            # Send request
            response = requests.request(
                method=method.upper(),
                url=target_url,
                json=validated_data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # Prepare response data
            response_data = {
                'status_code': response.status_code,
                'success': response.ok,
                'url': target_url,
                'method': method.upper(),
                'data_sent': validated_data
            }
            
            # Add response content if available
            try:
                if response.content:
                    response_data['response'] = response.json()
            except json.JSONDecodeError:
                response_data['response'] = response.text
            
            # Log the request
            if response.ok:
                self.logger.info(f"Successfully sent data to {target_url}")
                self.logger.debug(f"Response: {response_data}")
            else:
                self.logger.warning(f"Request failed with status {response.status_code}")
                response.raise_for_status()
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request failed: {str(e)}")
            raise ConnectionError(f"Failed to send data to {target_url}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise ValueError(f"Failed to send data: {str(e)}")
    
    def send_batch(self, data_list: list, method: str = 'POST', 
                   endpoint: Optional[str] = None) -> list:
        """
        Send multiple data items in batch.
        
        Args:
            data_list (list): List of data dictionaries to send
            method (str): HTTP method (default: POST)
            endpoint (str, optional): Additional endpoint path
        
        Returns:
            list: List of response data for each item
        """
        results = []
        for i, data in enumerate(data_list):
            try:
                result = self.send(data, method, endpoint)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to send batch item {i}: {str(e)}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'data': data
                })
        return results
    
    def update_auth_token(self, token: str):
        """
        Update the Bearer authentication token.
        
        Args:
            token (str): New authentication token
        """
        self.headers['Authorization'] = f'Bearer {token}'
        self.logger.info("Authentication token updated")
    
    def add_header(self, key: str, value: str):
        """
        Add or update a header.
        
        Args:
            key (str): Header name
            value (str): Header value
        """
        self.headers[key] = value
    
    def remove_header(self, key: str):
        """
        Remove a header.
        
        Args:
            key (str): Header name to remove
        """
        if key in self.headers:
            del self.headers[key]
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get current headers.
        
        Returns:
            dict: Current headers
        """
        return self.headers.copy()


class HTTPReceiver:
    """
    HTTP Receiver for creating a simple webhook server to receive IoT data.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080):
        """
        Initialize HTTP Receiver.
        
        Args:
            host (str): Host to bind to (default: '0.0.0.0')
            port (int): Port to listen on (default: 8080)
        """
        self.host = host
        self.port = port
        self.logger = logging.getLogger(f"iotkit.http.receiver.{host}:{port}")
        self._callbacks = {}
    
    def add_endpoint(self, path: str, callback: callable, methods: list = None):
        """
        Add an endpoint handler.
        
        Args:
            path (str): URL path
            callback (callable): Function to handle requests
            methods (list): Allowed HTTP methods (default: ['POST'])
        """
        if methods is None:
            methods = ['POST']
        
        self._callbacks[path] = {
            'callback': callback,
            'methods': methods
        }
    
    def start_server(self):
        """
        Start the HTTP receiver server.
        
        Note: This is a simple implementation. For production use,
        consider using Flask, FastAPI, or similar frameworks.
        """
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse as urlparse
        
        class RequestHandler(BaseHTTPRequestHandler):
            def __init__(self, receiver, *args, **kwargs):
                self.receiver = receiver
                super().__init__(*args, **kwargs)
            
            def do_POST(self):
                self._handle_request('POST')
            
            def do_GET(self):
                self._handle_request('GET')
            
            def _handle_request(self, method):
                try:
                    # Parse URL
                    parsed_path = urlparse.urlparse(self.path)
                    path = parsed_path.path
                    
                    # Check if we have a handler for this path
                    if path in self.receiver._callbacks:
                        endpoint_config = self.receiver._callbacks[path]
                        
                        if method in endpoint_config['methods']:
                            # Read request data
                            content_length = int(self.headers.get('Content-Length', 0))
                            if content_length > 0:
                                post_data = self.rfile.read(content_length)
                                try:
                                    data = json.loads(post_data.decode('utf-8'))
                                except json.JSONDecodeError:
                                    data = post_data.decode('utf-8')
                            else:
                                data = None
                            
                            # Call the callback
                            try:
                                response = endpoint_config['callback'](data, method, path)
                                
                                # Send response
                                self.send_response(200)
                                self.send_header('Content-Type', 'application/json')
                                self.end_headers()
                                
                                if isinstance(response, dict):
                                    self.wfile.write(json.dumps(response).encode())
                                else:
                                    self.wfile.write(str(response).encode())
                                    
                            except Exception as e:
                                self.receiver.logger.error(f"Error in callback: {str(e)}")
                                self.send_response(500)
                                self.send_header('Content-Type', 'application/json')
                                self.end_headers()
                                self.wfile.write(json.dumps({'error': str(e)}).encode())
                        else:
                            # Method not allowed
                            self.send_response(405)
                            self.end_headers()
                    else:
                        # Path not found
                        self.send_response(404)
                        self.end_headers()
                        
                except Exception as e:
                    self.receiver.logger.error(f"Error handling request: {str(e)}")
                    self.send_response(500)
                    self.end_headers()
        
        # Create handler with receiver reference
        handler = lambda *args, **kwargs: RequestHandler(self, *args, **kwargs)
        
        # Start server
        server = HTTPServer((self.host, self.port), handler)
        self.logger.info(f"HTTP Receiver started on {self.host}:{self.port}")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info("HTTP Receiver stopped")
            server.shutdown()