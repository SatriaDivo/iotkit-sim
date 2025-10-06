"""
IoTKit WebSocket Module

This module provides WebSocket client and server functionality for real-time IoT communication.
"""

import json
import asyncio
import threading
import logging
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    from websockets.client import WebSocketClientProtocol
except ImportError:
    raise ImportError("websockets is required. Install with: pip install websockets")

from .utils import validate_data, generate_timestamp


class WebSocketPublisher:
    """
    WebSocket Publisher for sending IoT data to WebSocket servers.
    """
    
    def __init__(self, uri: str, headers: Optional[Dict[str, str]] = None,
                 auto_reconnect: bool = True, reconnect_interval: int = 5):
        """
        Initialize WebSocket Publisher.
        
        Args:
            uri (str): WebSocket server URI (ws:// or wss://)
            headers (dict, optional): Additional headers for connection
            auto_reconnect (bool): Auto-reconnect on connection loss
            reconnect_interval (int): Seconds between reconnection attempts
        """
        self.uri = uri
        self.headers = headers or {}
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.running = False
        self.logger = logging.getLogger(f"iotkit.websocket.publisher.{uri}")
        
        # Event loop and thread management
        self.loop = None
        self.thread = None
        self._stop_event = threading.Event()
    
    async def _connect(self) -> bool:
        """
        Connect to WebSocket server.
        
        Returns:
            bool: True if connected successfully
        """
        try:
            self.websocket = await websockets.connect(
                self.uri,
                extra_headers=self.headers
            )
            self.connected = True
            self.logger.info(f"Connected to WebSocket server: {self.uri}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.uri}: {str(e)}")
            self.connected = False
            return False
    
    async def _disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
            self.connected = False
            self.logger.info("Disconnected from WebSocket server")
    
    async def _send_data(self, data: Dict[str, Any]) -> bool:
        """
        Send data through WebSocket.
        
        Args:
            data (dict): Data to send
        
        Returns:
            bool: True if sent successfully
        """
        if not self.connected or not self.websocket:
            return False
        
        try:
            validated_data = validate_data(data)
            message = json.dumps(validated_data)
            await self.websocket.send(message)
            self.logger.debug(f"Sent WebSocket message: {message}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send WebSocket message: {str(e)}")
            self.connected = False
            return False
    
    async def _run_loop(self):
        """Main event loop for WebSocket connection."""
        while self.running and not self._stop_event.is_set():
            if not self.connected:
                if await self._connect():
                    continue
                else:
                    if self.auto_reconnect:
                        self.logger.info(f"Retrying connection in {self.reconnect_interval}s...")
                        await asyncio.sleep(self.reconnect_interval)
                        continue
                    else:
                        break
            
            try:
                # Keep connection alive with ping
                if self.websocket:
                    await self.websocket.ping()
                    await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Connection error: {str(e)}")
                self.connected = False
                if not self.auto_reconnect:
                    break
    
    def start(self):
        """Start WebSocket publisher in background thread."""
        if self.running:
            return
        
        self.running = True
        self._stop_event.clear()
        
        def run_async():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._run_loop())
        
        self.thread = threading.Thread(target=run_async, daemon=True)
        self.thread.start()
        
        # Wait a moment for connection
        time.sleep(1)
    
    def stop(self):
        """Stop WebSocket publisher."""
        self.running = False
        self._stop_event.set()
        
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._disconnect(), self.loop)
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
    
    def send(self, data: Dict[str, Any]) -> bool:
        """
        Send data through WebSocket (thread-safe).
        
        Args:
            data (dict): Data to send
        
        Returns:
            bool: True if sent successfully
        """
        if not self.running or not self.loop:
            return False
        
        try:
            future = asyncio.run_coroutine_threadsafe(self._send_data(data), self.loop)
            return future.result(timeout=5)
        except Exception as e:
            self.logger.error(f"Failed to send data: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.connected


class WebSocketSubscriber:
    """
    WebSocket Subscriber for receiving IoT data from WebSocket servers.
    """
    
    def __init__(self, uri: str, on_message: Optional[Callable] = None,
                 headers: Optional[Dict[str, str]] = None,
                 auto_reconnect: bool = True, reconnect_interval: int = 5):
        """
        Initialize WebSocket Subscriber.
        
        Args:
            uri (str): WebSocket server URI
            on_message (callable, optional): Callback for received messages
            headers (dict, optional): Additional headers for connection
            auto_reconnect (bool): Auto-reconnect on connection loss
            reconnect_interval (int): Seconds between reconnection attempts
        """
        self.uri = uri
        self.on_message_callback = on_message
        self.headers = headers or {}
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.running = False
        self.logger = logging.getLogger(f"iotkit.websocket.subscriber.{uri}")
        
        self.loop = None
        self.thread = None
        self._stop_event = threading.Event()
    
    async def _connect(self) -> bool:
        """Connect to WebSocket server."""
        try:
            self.websocket = await websockets.connect(
                self.uri,
                extra_headers=self.headers
            )
            self.connected = True
            self.logger.info(f"Connected to WebSocket server: {self.uri}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.uri}: {str(e)}")
            self.connected = False
            return False
    
    async def _disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
            self.connected = False
            self.logger.info("Disconnected from WebSocket server")
    
    async def _listen_for_messages(self):
        """Listen for incoming WebSocket messages."""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    self.logger.debug(f"Received WebSocket message: {data}")
                    
                    if self.on_message_callback:
                        self.on_message_callback(data)
                        
                except json.JSONDecodeError:
                    self.logger.warning(f"Received non-JSON message: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing message: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error listening for messages: {str(e)}")
            self.connected = False
    
    async def _run_loop(self):
        """Main event loop for WebSocket subscriber."""
        while self.running and not self._stop_event.is_set():
            if not self.connected:
                if await self._connect():
                    # Start listening for messages
                    await self._listen_for_messages()
                else:
                    if self.auto_reconnect:
                        self.logger.info(f"Retrying connection in {self.reconnect_interval}s...")
                        await asyncio.sleep(self.reconnect_interval)
                        continue
                    else:
                        break
            
            await asyncio.sleep(0.1)
    
    def start(self):
        """Start WebSocket subscriber in background thread."""
        if self.running:
            return
        
        self.running = True
        self._stop_event.clear()
        
        def run_async():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._run_loop())
        
        self.thread = threading.Thread(target=run_async, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop WebSocket subscriber."""
        self.running = False
        self._stop_event.set()
        
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._disconnect(), self.loop)
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
    
    def set_message_callback(self, callback: Callable):
        """
        Set or update the message callback function.
        
        Args:
            callback (callable): Function to call when message is received
        """
        self.on_message_callback = callback
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.connected


class WebSocketServer:
    """
    WebSocket Server for receiving IoT data from WebSocket clients.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765,
                 on_message: Optional[Callable] = None,
                 on_connect: Optional[Callable] = None,
                 on_disconnect: Optional[Callable] = None):
        """
        Initialize WebSocket Server.
        
        Args:
            host (str): Host to bind to
            port (int): Port to listen on
            on_message (callable, optional): Callback for received messages
            on_connect (callable, optional): Callback for client connections
            on_disconnect (callable, optional): Callback for client disconnections
        """
        self.host = host
        self.port = port
        self.on_message_callback = on_message
        self.on_connect_callback = on_connect
        self.on_disconnect_callback = on_disconnect
        
        self.server = None
        self.running = False
        self.clients: List[WebSocketServerProtocol] = []
        self.logger = logging.getLogger(f"iotkit.websocket.server.{host}:{port}")
        
        self.loop = None
        self.thread = None
    
    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle individual client connections.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.logger.info(f"Client connected: {client_address}")
        
        # Add to clients list
        self.clients.append(websocket)
        
        # Call connect callback
        if self.on_connect_callback:
            try:
                self.on_connect_callback(websocket, client_address)
            except Exception as e:
                self.logger.error(f"Error in connect callback: {str(e)}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    self.logger.debug(f"Received from {client_address}: {data}")
                    
                    if self.on_message_callback:
                        self.on_message_callback(websocket, data, client_address)
                        
                except json.JSONDecodeError:
                    self.logger.warning(f"Received non-JSON message from {client_address}: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing message from {client_address}: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Error handling client {client_address}: {str(e)}")
        
        finally:
            # Remove from clients list
            if websocket in self.clients:
                self.clients.remove(websocket)
            
            # Call disconnect callback
            if self.on_disconnect_callback:
                try:
                    self.on_disconnect_callback(websocket, client_address)
                except Exception as e:
                    self.logger.error(f"Error in disconnect callback: {str(e)}")
            
            self.logger.info(f"Client disconnected: {client_address}")
    
    async def _start_server(self):
        """Start the WebSocket server."""
        try:
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port
            )
            self.logger.info(f"WebSocket server started on {self.host}:{self.port}")
            
            # Keep server running
            await self.server.wait_closed()
            
        except Exception as e:
            self.logger.error(f"Server error: {str(e)}")
    
    def start(self):
        """Start WebSocket server in background thread."""
        if self.running:
            return
        
        self.running = True
        
        def run_async():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._start_server())
        
        self.thread = threading.Thread(target=run_async, daemon=True)
        self.thread.start()
        
        # Wait a moment for server to start
        time.sleep(1)
    
    def stop(self):
        """Stop WebSocket server."""
        self.running = False
        
        if self.server:
            self.server.close()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
    
    async def _broadcast_data(self, data: Dict[str, Any]):
        """
        Broadcast data to all connected clients.
        
        Args:
            data (dict): Data to broadcast
        """
        if not self.clients:
            return
        
        try:
            validated_data = validate_data(data)
            message = json.dumps(validated_data)
            
            # Send to all connected clients
            disconnected = []
            for client in self.clients:
                try:
                    await client.send(message)
                except Exception as e:
                    self.logger.warning(f"Failed to send to client: {str(e)}")
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                if client in self.clients:
                    self.clients.remove(client)
                    
        except Exception as e:
            self.logger.error(f"Broadcast error: {str(e)}")
    
    def broadcast(self, data: Dict[str, Any]) -> bool:
        """
        Broadcast data to all connected clients (thread-safe).
        
        Args:
            data (dict): Data to broadcast
        
        Returns:
            bool: True if broadcast was attempted
        """
        if not self.running or not self.loop:
            return False
        
        try:
            asyncio.run_coroutine_threadsafe(self._broadcast_data(data), self.loop)
            return True
        except Exception as e:
            self.logger.error(f"Failed to broadcast data: {str(e)}")
            return False
    
    def get_connected_clients_count(self) -> int:
        """Get number of connected clients."""
        return len(self.clients)
    
    def set_message_callback(self, callback: Callable):
        """Set message callback."""
        self.on_message_callback = callback
    
    def set_connect_callback(self, callback: Callable):
        """Set connect callback."""
        self.on_connect_callback = callback
    
    def set_disconnect_callback(self, callback: Callable):
        """Set disconnect callback."""
        self.on_disconnect_callback = callback


class WebSocketBridge:
    """
    WebSocket Bridge for connecting different IoT protocols via WebSocket.
    """
    
    def __init__(self, server_port: int = 8765):
        """
        Initialize WebSocket Bridge.
        
        Args:
            server_port (int): Port for WebSocket server
        """
        self.server = WebSocketServer("localhost", server_port)
        self.publishers: Dict[str, WebSocketPublisher] = {}
        self.subscribers: Dict[str, WebSocketSubscriber] = {}
        self.logger = logging.getLogger("iotkit.websocket.bridge")
        
        # Set server callbacks
        self.server.set_message_callback(self._handle_server_message)
        self.server.set_connect_callback(self._handle_client_connect)
        self.server.set_disconnect_callback(self._handle_client_disconnect)
    
    def _handle_server_message(self, websocket, data: Dict[str, Any], client_address: str):
        """Handle messages from WebSocket server clients."""
        self.logger.info(f"Bridge received message from {client_address}: {data}")
        
        # Add timestamp and source
        bridge_data = {
            "source": "websocket_client",
            "client_address": client_address,
            "bridge_timestamp": generate_timestamp(),
            "data": data
        }
        
        # Broadcast to all publishers
        for name, publisher in self.publishers.items():
            if publisher.is_connected():
                publisher.send(bridge_data)
    
    def _handle_client_connect(self, websocket, client_address: str):
        """Handle client connections."""
        self.logger.info(f"Client connected to bridge: {client_address}")
    
    def _handle_client_disconnect(self, websocket, client_address: str):
        """Handle client disconnections."""
        self.logger.info(f"Client disconnected from bridge: {client_address}")
    
    def add_publisher(self, name: str, uri: str):
        """
        Add WebSocket publisher to bridge.
        
        Args:
            name (str): Publisher name
            uri (str): WebSocket URI to connect to
        """
        publisher = WebSocketPublisher(uri)
        self.publishers[name] = publisher
        publisher.start()
        self.logger.info(f"Added WebSocket publisher '{name}': {uri}")
    
    def add_subscriber(self, name: str, uri: str, callback: Optional[Callable] = None):
        """
        Add WebSocket subscriber to bridge.
        
        Args:
            name (str): Subscriber name
            uri (str): WebSocket URI to connect to
            callback (callable, optional): Message callback
        """
        def default_callback(data):
            self.logger.info(f"Subscriber '{name}' received: {data}")
            # Broadcast to server clients
            self.server.broadcast({
                "source": "websocket_subscriber",
                "subscriber_name": name,
                "bridge_timestamp": generate_timestamp(),
                "data": data
            })
        
        subscriber = WebSocketSubscriber(uri, callback or default_callback)
        self.subscribers[name] = subscriber
        subscriber.start()
        self.logger.info(f"Added WebSocket subscriber '{name}': {uri}")
    
    def start(self):
        """Start the WebSocket bridge."""
        self.server.start()
        self.logger.info("WebSocket bridge started")
    
    def stop(self):
        """Stop the WebSocket bridge."""
        # Stop all publishers
        for publisher in self.publishers.values():
            publisher.stop()
        
        # Stop all subscribers
        for subscriber in self.subscribers.values():
            subscriber.stop()
        
        # Stop server
        self.server.stop()
        self.logger.info("WebSocket bridge stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge status."""
        return {
            "server_clients": self.server.get_connected_clients_count(),
            "publishers": {name: pub.is_connected() for name, pub in self.publishers.items()},
            "subscribers": {name: sub.is_connected() for name, sub in self.subscribers.items()}
        }