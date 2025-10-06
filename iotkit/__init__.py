"""
IoTKit - A comprehensive IoT simulation and communication library

This library provides tools for IoT device simulation, MQTT communication,
HTTP REST API integration, and data logging capabilities.

Author: IoTKit Development Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "IoTKit Development Team"
__license__ = "MIT"

# Core imports
from .sensor import Sensor, SensorCollection
from .mqtt import MQTTPublisher, MQTTSubscriber
from .http import HTTPPublisher, HTTPReceiver
from .websocket import WebSocketPublisher, WebSocketSubscriber, WebSocketServer, WebSocketBridge
from .logger import DataLogger, MultiLogger
from .config import ConfigManager, config_manager
from .utils import (
    generate_timestamp,
    generate_device_id,
    validate_data,
    validate_sensor_config,
    encode_json,
    decode_json,
    validate_url,
    validate_mqtt_topic,
    setup_logging,
    Config,
    config,
    DataBuffer
)

# Define what gets imported with "from iotkit import *"
__all__ = [
    # Core classes
    'Sensor',
    'SensorCollection',
    'MQTTPublisher',
    'MQTTSubscriber',
    'HTTPPublisher',
    'HTTPReceiver',
    'WebSocketPublisher',
    'WebSocketSubscriber',
    'WebSocketServer',
    'WebSocketBridge',
    'DataLogger',
    'MultiLogger',
    'ConfigManager',
    'config_manager',
    
    # Utility functions
    'generate_timestamp',
    'generate_device_id',
    'validate_data',
    'validate_sensor_config',
    'encode_json',
    'decode_json',
    'validate_url',
    'validate_mqtt_topic',
    'setup_logging',
    
    # Configuration
    'Config',
    'config',
    'DataBuffer',
    
    # Metadata
    '__version__',
    '__author__',
    '__license__'
]

# Setup default logging
import logging
logger = setup_logging()

def get_version():
    """Get the current version of IoTKit."""
    return __version__

def get_info():
    """Get library information."""
    return {
        'name': 'IoTKit',
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'description': 'A comprehensive IoT simulation and communication library'
    }

# Initialize library
logger.info(f"IoTKit v{__version__} initialized")