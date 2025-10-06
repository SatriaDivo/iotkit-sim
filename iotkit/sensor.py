"""
IoTKit Sensor Module

This module provides virtual sensors for IoT simulation.
"""

import random
from typing import Union, Dict, Any
from .utils import generate_timestamp, validate_data


class Sensor:
    """
    Virtual sensor for IoT simulation.
    
    Supports two modes:
    - random: generates random values within min-max range
    - manual: allows manual input of values
    """
    
    def __init__(self, name: str, min_val: float = 0, max_val: float = 100, mode: str = "random"):
        """
        Initialize the sensor.
        
        Args:
            name (str): Name of the sensor
            min_val (float): Minimum value for the sensor
            max_val (float): Maximum value for the sensor
            mode (str): Operation mode - "random" or "manual"
        
        Raises:
            ValueError: If mode is not "random" or "manual"
        """
        if mode not in ["random", "manual"]:
            raise ValueError("Mode must be either 'random' or 'manual'")
        
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.mode = mode
        self._manual_value = None
        
    def read(self) -> float:
        """
        Read current sensor value.
        
        Returns:
            float: Current sensor value
        
        Raises:
            ValueError: If in manual mode and no value has been set
        """
        if self.mode == "random":
            return round(random.uniform(self.min_val, self.max_val), 2)
        elif self.mode == "manual":
            if self._manual_value is None:
                raise ValueError("Manual value not set. Use set_value() first.")
            return self._manual_value
    
    def set_value(self, value: float) -> None:
        """
        Set manual value for the sensor (only works in manual mode).
        
        Args:
            value (float): Value to set
        
        Raises:
            ValueError: If sensor is not in manual mode
        """
        if self.mode != "manual":
            raise ValueError("set_value() only works in manual mode")
        
        if not (self.min_val <= value <= self.max_val):
            raise ValueError(f"Value must be between {self.min_val} and {self.max_val}")
        
        self._manual_value = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert sensor data to dictionary format.
        
        Returns:
            dict: Sensor data with name, value, and timestamp
        """
        try:
            value = self.read()
            data = {
                "name": self.name,
                "value": value,
                "timestamp": generate_timestamp(),
                "min": self.min_val,
                "max": self.max_val,
                "mode": self.mode
            }
            return validate_data(data)
        except Exception as e:
            raise RuntimeError(f"Failed to read sensor data: {str(e)}")


class SensorCollection:
    """
    Collection of multiple sensors for batch operations.
    """
    
    def __init__(self):
        """Initialize empty sensor collection."""
        self.sensors = {}
    
    def add_sensor(self, sensor: Sensor) -> None:
        """
        Add a sensor to the collection.
        
        Args:
            sensor (Sensor): Sensor instance to add
        """
        self.sensors[sensor.name] = sensor
    
    def remove_sensor(self, name: str) -> None:
        """
        Remove a sensor from the collection.
        
        Args:
            name (str): Name of the sensor to remove
        """
        if name in self.sensors:
            del self.sensors[name]
    
    def read_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Read all sensors in the collection.
        
        Returns:
            dict: Dictionary of sensor data
        """
        data = {}
        for name, sensor in self.sensors.items():
            try:
                data[name] = sensor.to_dict()
            except Exception as e:
                data[name] = {"error": str(e), "timestamp": generate_timestamp()}
        return data
    
    def get_sensor(self, name: str) -> Union[Sensor, None]:
        """
        Get a specific sensor by name.
        
        Args:
            name (str): Name of the sensor
        
        Returns:
            Sensor or None: The sensor instance or None if not found
        """
        return self.sensors.get(name)
    
    def list_sensors(self) -> list:
        """
        Get list of all sensor names.
        
        Returns:
            list: List of sensor names
        """
        return list(self.sensors.keys())