"""
IoTKit Utilities Module

This module provides utility functions for IoT operations.
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, Union
import uuid
import logging


def generate_timestamp(format_type: str = "iso") -> str:
    """
    Generate current timestamp.
    
    Args:
        format_type (str): Format type - "iso", "unix", or "custom"
    
    Returns:
        str: Formatted timestamp
    """
    now = datetime.now(timezone.utc)
    
    if format_type == "iso":
        return now.isoformat()
    elif format_type == "unix":
        return str(int(now.timestamp()))
    elif format_type == "custom":
        return now.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        return now.isoformat()


def generate_device_id(prefix: str = "iotkit") -> str:
    """
    Generate unique device ID.
    
    Args:
        prefix (str): Prefix for the device ID
    
    Returns:
        str: Unique device ID
    """
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}"


def validate_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate IoT data structure.
    
    Args:
        data (dict): Data to validate
    
    Returns:
        dict: Validated data
    
    Raises:
        ValueError: If data is invalid
    """
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    
    # Check for required fields (at least one of name or value should exist)
    if not any(key in data for key in ['name', 'value', 'sensor', 'measurement']):
        raise ValueError("Data must contain at least one of: name, value, sensor, measurement")
    
    # Validate timestamp format if present
    if 'timestamp' in data:
        timestamp = data['timestamp']
        if not isinstance(timestamp, str):
            raise ValueError("Timestamp must be a string")
        
        # Try to parse as ISO format
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Invalid timestamp format. Use ISO 8601 format.")
    
    # Validate numeric values
    if 'value' in data:
        value = data['value']
        if not isinstance(value, (int, float, str)):
            raise ValueError("Value must be numeric or string")
        
        # Try to convert string to number if possible
        if isinstance(value, str):
            try:
                data['value'] = float(value)
            except ValueError:
                pass  # Keep as string if not convertible
    
    return data


def validate_sensor_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate sensor configuration.
    
    Args:
        config (dict): Sensor configuration
    
    Returns:
        dict: Validated configuration
    
    Raises:
        ValueError: If configuration is invalid
    """
    required_fields = ['name']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate name
    if not isinstance(config['name'], str) or not config['name'].strip():
        raise ValueError("Sensor name must be a non-empty string")
    
    # Validate mode if present
    if 'mode' in config:
        if config['mode'] not in ['random', 'manual']:
            raise ValueError("Mode must be 'random' or 'manual'")
    
    # Validate min/max values
    if 'min_val' in config and 'max_val' in config:
        min_val = config['min_val']
        max_val = config['max_val']
        
        if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
            raise ValueError("min_val and max_val must be numeric")
        
        if min_val >= max_val:
            raise ValueError("min_val must be less than max_val")
    
    return config


def encode_json(data: Any, pretty: bool = False) -> str:
    """
    Encode data to JSON string.
    
    Args:
        data: Data to encode
        pretty (bool): Whether to format JSON prettily
    
    Returns:
        str: JSON string
    
    Raises:
        ValueError: If data cannot be encoded
    """
    try:
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        else:
            return json.dumps(data, ensure_ascii=False, default=str)
    except Exception as e:
        raise ValueError(f"Failed to encode JSON: {str(e)}")


def decode_json(json_str: str) -> Any:
    """
    Decode JSON string to Python object.
    
    Args:
        json_str (str): JSON string to decode
    
    Returns:
        Any: Decoded Python object
    
    Raises:
        ValueError: If JSON cannot be decoded
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON: {str(e)}")


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if URL is valid
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def validate_mqtt_topic(topic: str) -> bool:
    """
    Validate MQTT topic format.
    
    Args:
        topic (str): MQTT topic to validate
    
    Returns:
        bool: True if topic is valid
    """
    if not isinstance(topic, str) or not topic:
        return False
    
    # MQTT topic rules:
    # - Cannot be empty
    # - Cannot contain null character
    # - Cannot start or end with /
    # - + and # have special meaning (wildcards)
    
    if '\x00' in topic:
        return False
    
    if topic.startswith('/') or topic.endswith('/'):
        return False
    
    # Basic validation - more complex rules exist but this covers basics
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename (str): Original filename
    
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters for Windows/Unix filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


def calculate_data_rate(data_count: int, time_seconds: float) -> float:
    """
    Calculate data transmission rate.
    
    Args:
        data_count (int): Number of data points
        time_seconds (float): Time period in seconds
    
    Returns:
        float: Data rate (items per second)
    """
    if time_seconds <= 0:
        return 0.0
    
    return data_count / time_seconds


def format_bytes(bytes_count: int) -> str:
    """
    Format byte count into human-readable format.
    
    Args:
        bytes_count (int): Number of bytes
    
    Returns:
        str: Formatted byte string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def setup_logging(level: str = "INFO", format_string: str = None) -> logging.Logger:
    """
    Setup logging configuration for IoTKit.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string (str, optional): Custom format string
    
    Returns:
        logging.Logger: Configured logger
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger = logging.getLogger("iotkit")
    logger.info("IoTKit logging initialized")
    return logger


def retry_operation(func: callable, max_retries: int = 3, delay: float = 1.0):
    """
    Retry decorator for unreliable operations.
    
    Args:
        func (callable): Function to retry
        max_retries (int): Maximum number of retries
        delay (float): Delay between retries in seconds
    
    Returns:
        callable: Decorated function
    """
    import time
    
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
                else:
                    raise last_exception
    
    return wrapper


class DataBuffer:
    """
    Simple data buffer for batching operations.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize data buffer.
        
        Args:
            max_size (int): Maximum buffer size
        """
        self.max_size = max_size
        self.buffer = []
        self.logger = logging.getLogger("iotkit.utils.buffer")
    
    def add(self, data: Any) -> bool:
        """
        Add data to buffer.
        
        Args:
            data: Data to add
        
        Returns:
            bool: True if buffer is full after adding
        """
        self.buffer.append(data)
        return len(self.buffer) >= self.max_size
    
    def get_all(self, clear: bool = True) -> list:
        """
        Get all data from buffer.
        
        Args:
            clear (bool): Clear buffer after getting data
        
        Returns:
            list: All buffered data
        """
        data = self.buffer.copy()
        if clear:
            self.buffer.clear()
        return data
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        return len(self.buffer) >= self.max_size
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return len(self.buffer) == 0
    
    def size(self) -> int:
        """Get current buffer size."""
        return len(self.buffer)
    
    def clear(self):
        """Clear the buffer."""
        self.buffer.clear()


# Configuration management
class Config:
    """
    Configuration manager for IoTKit.
    """
    
    def __init__(self):
        """Initialize configuration."""
        self.config = {
            'mqtt': {
                'default_port': 1883,
                'default_qos': 0,
                'keepalive': 60
            },
            'http': {
                'default_timeout': 30,
                'default_headers': {
                    'Content-Type': 'application/json',
                    'User-Agent': 'IoTKit/1.0'
                }
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'data': {
                'timestamp_format': 'iso',
                'validation_enabled': True,
                'buffer_size': 100
            }
        }
    
    def get(self, key: str, default=None):
        """
        Get configuration value.
        
        Args:
            key (str): Configuration key (dot notation supported)
            default: Default value if key not found
        
        Returns:
            Any: Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key (str): Configuration key (dot notation supported)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def load_from_file(self, filepath: str):
        """
        Load configuration from JSON file.
        
        Args:
            filepath (str): Path to configuration file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self.config.update(file_config)
        except Exception as e:
            raise ValueError(f"Failed to load config from {filepath}: {str(e)}")
    
    def save_to_file(self, filepath: str):
        """
        Save configuration to JSON file.
        
        Args:
            filepath (str): Path to save configuration
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to save config to {filepath}: {str(e)}")


# Global configuration instance
config = Config()