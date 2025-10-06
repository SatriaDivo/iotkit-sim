"""
IoTKit MQTT Module

This module provides MQTT publisher and subscriber functionality for IoT communication.
"""

import json
import threading
import time
from typing import Callable, Dict, Any, Optional
import logging

try:
    import paho.mqtt.client as mqtt
except ImportError:
    raise ImportError("paho-mqtt is required. Install with: pip install paho-mqtt")

from .utils import validate_data


class MQTTPublisher:
    """
    MQTT Publisher for sending IoT data.
    """
    
    def __init__(self, broker: str, topic: str, port: int = 1883, 
                 username: Optional[str] = None, password: Optional[str] = None,
                 client_id: Optional[str] = None):
        """
        Initialize MQTT Publisher.
        
        Args:
            broker (str): MQTT broker address
            topic (str): Default topic to publish to
            port (int): MQTT broker port (default: 1883)
            username (str, optional): Username for authentication
            password (str, optional): Password for authentication
            client_id (str, optional): Custom client ID
        """
        self.broker = broker
        self.topic = topic
        self.port = port
        self.username = username
        self.password = password
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=client_id or f"iotkit_pub_{int(time.time())}")
        
        # Set authentication if provided
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_publish = self._on_publish
        self.client.on_disconnect = self._on_disconnect
        
        self.connected = False
        self.logger = logging.getLogger(f"iotkit.mqtt.publisher.{self.broker}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to broker."""
        if rc == 0:
            self.connected = True
            self.logger.info(f"Connected to MQTT broker {self.broker}:{self.port}")
        else:
            self.connected = False
            self.logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for when message is published."""
        self.logger.debug(f"Message published with ID: {mid}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from broker."""
        self.connected = False
        self.logger.info(f"Disconnected from MQTT broker. Return code: {rc}")
    
    def connect(self, timeout: int = 10) -> bool:
        """
        Connect to MQTT broker.
        
        Args:
            timeout (int): Connection timeout in seconds
        
        Returns:
            bool: True if connected successfully
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            
            # Wait for connection
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                raise ConnectionError(f"Failed to connect to {self.broker}:{self.port} within {timeout}s")
            
            return True
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            raise ConnectionError(f"Failed to connect to MQTT broker: {str(e)}")
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
    
    def publish(self, data: Dict[str, Any], topic: Optional[str] = None, qos: int = 0) -> bool:
        """
        Publish data to MQTT topic.
        
        Args:
            data (dict): Data to publish
            topic (str, optional): Topic to publish to (uses default if None)
            qos (int): Quality of Service level (0, 1, or 2)
        
        Returns:
            bool: True if published successfully
        
        Raises:
            ConnectionError: If not connected to broker
            ValueError: If data is invalid
        """
        if not self.connected:
            raise ConnectionError("Not connected to MQTT broker. Call connect() first.")
        
        try:
            # Validate and serialize data
            validated_data = validate_data(data)
            message = json.dumps(validated_data)
            
            # Use provided topic or default
            publish_topic = topic or self.topic
            
            # Publish message
            result = self.client.publish(publish_topic, message, qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published to {publish_topic}: {message}")
                return True
            else:
                self.logger.error(f"Failed to publish message. Return code: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"Publish error: {str(e)}")
            raise ValueError(f"Failed to publish data: {str(e)}")


class MQTTSubscriber:
    """
    MQTT Subscriber for receiving IoT data.
    """
    
    def __init__(self, broker: str, topic: str, port: int = 1883,
                 username: Optional[str] = None, password: Optional[str] = None,
                 client_id: Optional[str] = None, on_message: Optional[Callable] = None):
        """
        Initialize MQTT Subscriber.
        
        Args:
            broker (str): MQTT broker address
            topic (str): Topic to subscribe to
            port (int): MQTT broker port (default: 1883)
            username (str, optional): Username for authentication
            password (str, optional): Password for authentication
            client_id (str, optional): Custom client ID
            on_message (callable, optional): Callback function for received messages
        """
        self.broker = broker
        self.topic = topic
        self.port = port
        self.username = username
        self.password = password
        self.on_message_callback = on_message
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=client_id or f"iotkit_sub_{int(time.time())}")
        
        # Set authentication if provided
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        self.connected = False
        self.subscribed = False
        self.logger = logging.getLogger(f"iotkit.mqtt.subscriber.{self.broker}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to broker."""
        if rc == 0:
            self.connected = True
            self.logger.info(f"Connected to MQTT broker {self.broker}:{self.port}")
            # Auto-subscribe to topic
            self.client.subscribe(self.topic)
        else:
            self.connected = False
            self.logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for when message is received."""
        try:
            # Decode message
            message_str = msg.payload.decode('utf-8')
            message_data = json.loads(message_str)
            
            self.logger.debug(f"Received message from {msg.topic}: {message_str}")
            
            # Call user-defined callback if provided
            if self.on_message_callback:
                self.on_message_callback(msg.topic, message_data)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from broker."""
        self.connected = False
        self.subscribed = False
        self.logger.info(f"Disconnected from MQTT broker. Return code: {rc}")
    
    def connect(self, timeout: int = 10) -> bool:
        """
        Connect to MQTT broker and subscribe to topic.
        
        Args:
            timeout (int): Connection timeout in seconds
        
        Returns:
            bool: True if connected and subscribed successfully
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            
            # Wait for connection
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                raise ConnectionError(f"Failed to connect to {self.broker}:{self.port} within {timeout}s")
            
            self.subscribed = True
            return True
            
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            raise ConnectionError(f"Failed to connect to MQTT broker: {str(e)}")
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        self.subscribed = False
    
    def set_message_callback(self, callback: Callable):
        """
        Set or update the message callback function.
        
        Args:
            callback (callable): Function to call when message is received
        """
        self.on_message_callback = callback
    
    def start_listening(self):
        """
        Start listening for messages (blocking).
        
        Raises:
            ConnectionError: If not connected to broker
        """
        if not self.connected:
            raise ConnectionError("Not connected to MQTT broker. Call connect() first.")
        
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            self.logger.info("Stopped listening for messages")
            self.disconnect()
    
    def start_listening_async(self):
        """
        Start listening for messages in a separate thread (non-blocking).
        
        Returns:
            threading.Thread: The thread object
        
        Raises:
            ConnectionError: If not connected to broker
        """
        if not self.connected:
            raise ConnectionError("Not connected to MQTT broker. Call connect() first.")
        
        def listen():
            try:
                self.client.loop_forever()
            except Exception as e:
                self.logger.error(f"Error in async listening: {str(e)}")
        
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        return thread