"""
IoTKit Configuration Module

This module provides configuration management from YAML/JSON files.
"""

import json
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


class ConfigManager:
    """
    Configuration manager for IoTKit.
    
    Supports loading configuration from YAML and JSON files.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file (str, optional): Path to configuration file
        """
        self.config_file = config_file
        self.config = {}
        self.default_config = self._get_default_config()
        
        if config_file:
            self.load_config(config_file)
        else:
            self.config = self.default_config.copy()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "mqtt": {
                "broker": "mqtt.eclipseprojects.io",
                "port": 1883,
                "topic_prefix": "iotkit",
                "username": None,
                "password": None,
                "client_id_prefix": "iotkit_client"
            },
            "http": {
                "base_url": "http://localhost:5000/api",
                "timeout": 30,
                "headers": {
                    "Content-Type": "application/json"
                },
                "auth_token": None
            },
            "sensors": {
                "default_mode": "random",
                "reading_interval": 2.0,
                "precision": 2
            },
            "logging": {
                "log_level": "INFO",
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_format": "csv",
                "auto_timestamp": True
            },
            "general": {
                "device_id_prefix": "iotkit_device",
                "data_retention_days": 30,
                "batch_size": 10
            }
        }
    
    def load_config(self, config_file: str) -> None:
        """
        Load configuration from file.
        
        Args:
            config_file (str): Path to configuration file
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If file format is not supported
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        file_ext = Path(config_file).suffix.lower()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if file_ext == '.json':
                    loaded_config = json.load(f)
                elif file_ext in ['.yml', '.yaml']:
                    if yaml is None:
                        raise ImportError("PyYAML is required for YAML support. Install with: pip install PyYAML")
                    loaded_config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_ext}. Use .json, .yml, or .yaml")
            
            # Merge with default config
            self.config = self._deep_merge(self.default_config, loaded_config)
            self.config_file = config_file
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
    
    def save_config(self, config_file: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            config_file (str, optional): Path to save config. Uses current config_file if not provided.
        
        Raises:
            ValueError: If no config file is specified
        """
        file_path = config_file or self.config_file
        if not file_path:
            raise ValueError("No config file specified")
        
        file_ext = Path(file_path).suffix.lower()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_ext == '.json':
                json.dump(self.config, f, indent=2)
            elif file_ext in ['.yml', '.yaml']:
                if yaml is None:
                    raise ImportError("PyYAML is required for YAML support. Install with: pip install PyYAML")
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key (str): Configuration key (e.g., 'mqtt.broker')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key (str): Configuration key (e.g., 'mqtt.broker')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_mqtt_config(self) -> Dict[str, Any]:
        """Get MQTT configuration."""
        return self.config.get('mqtt', {})
    
    def get_http_config(self) -> Dict[str, Any]:
        """Get HTTP configuration."""
        return self.config.get('http', {})
    
    def get_sensor_config(self) -> Dict[str, Any]:
        """Get sensor configuration."""
        return self.config.get('sensors', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config.get('logging', {})
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        Deep merge two dictionaries.
        
        Args:
            base (dict): Base dictionary
            update (dict): Dictionary to merge into base
        
        Returns:
            dict: Merged dictionary
        """
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self.default_config.copy()
    
    def validate_config(self) -> bool:
        """
        Validate current configuration.
        
        Returns:
            bool: True if configuration is valid
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate MQTT config
        mqtt_config = self.get_mqtt_config()
        if not mqtt_config.get('broker'):
            raise ValueError("MQTT broker is required")
        
        if not isinstance(mqtt_config.get('port', 1883), int):
            raise ValueError("MQTT port must be an integer")
        
        # Validate HTTP config
        http_config = self.get_http_config()
        if not http_config.get('base_url'):
            raise ValueError("HTTP base_url is required")
        
        # Validate sensor config
        sensor_config = self.get_sensor_config()
        if sensor_config.get('default_mode') not in ['random', 'manual']:
            raise ValueError("Sensor default_mode must be 'random' or 'manual'")
        
        return True
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return json.dumps(self.config, indent=2)


# Global configuration instance
config_manager = ConfigManager()