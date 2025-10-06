"""
IoTKit Logger Module

This module provides data logging functionality for IoT data.
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Union
import logging

from .utils import generate_timestamp, validate_data


class DataLogger:
    """
    Data logger for IoT sensor data.
    Supports CSV and JSON output formats.
    """
    
    def __init__(self, filename: str = "data.csv", format_type: str = "csv", 
                 auto_create_dir: bool = True):
        """
        Initialize the data logger.
        
        Args:
            filename (str): Output filename (default: "data.csv")
            format_type (str): Output format - "csv" or "json" (default: "csv")
            auto_create_dir (bool): Automatically create directory if not exists
        
        Raises:
            ValueError: If format_type is not "csv" or "json"
        """
        if format_type not in ["csv", "json"]:
            raise ValueError("format_type must be either 'csv' or 'json'")
        
        self.filename = filename
        self.format_type = format_type
        self.auto_create_dir = auto_create_dir
        self.logger = logging.getLogger(f"iotkit.logger.{filename}")
        
        # Create directory if needed
        if self.auto_create_dir:
            directory = os.path.dirname(self.filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                self.logger.info(f"Created directory: {directory}")
        
        # Initialize file if it doesn't exist
        self._initialize_file()
    
    def _initialize_file(self):
        """Initialize the log file with headers if it doesn't exist."""
        if not os.path.exists(self.filename):
            if self.format_type == "csv":
                # Create CSV with headers
                with open(self.filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['timestamp', 'name', 'value', 'metadata'])
                    self.logger.info(f"Created CSV file: {self.filename}")
            elif self.format_type == "json":
                # Create JSON with empty array
                with open(self.filename, 'w', encoding='utf-8') as jsonfile:
                    json.dump([], jsonfile)
                    self.logger.info(f"Created JSON file: {self.filename}")
    
    def log(self, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> bool:
        """
        Log data to file.
        
        Args:
            data (dict): Data to log
            metadata (dict, optional): Additional metadata
        
        Returns:
            bool: True if logged successfully
        
        Raises:
            ValueError: If data is invalid
            IOError: If file operations fail
        """
        try:
            # Validate data
            validated_data = validate_data(data)
            
            # Add timestamp if not present
            if 'timestamp' not in validated_data:
                validated_data['timestamp'] = generate_timestamp()
            
            # Add metadata if provided
            if metadata:
                validated_data['metadata'] = metadata
            
            if self.format_type == "csv":
                return self._log_csv(validated_data)
            elif self.format_type == "json":
                return self._log_json(validated_data)
                
        except Exception as e:
            self.logger.error(f"Failed to log data: {str(e)}")
            raise IOError(f"Failed to log data: {str(e)}")
    
    def _log_csv(self, data: Dict[str, Any]) -> bool:
        """Log data to CSV file."""
        try:
            with open(self.filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Extract main fields
                timestamp = data.get('timestamp', '')
                name = data.get('name', '')
                value = data.get('value', '')
                
                # Convert metadata to JSON string
                metadata = {k: v for k, v in data.items() 
                           if k not in ['timestamp', 'name', 'value']}
                metadata_str = json.dumps(metadata) if metadata else ''
                
                writer.writerow([timestamp, name, value, metadata_str])
                self.logger.debug(f"Logged to CSV: {data}")
                return True
                
        except Exception as e:
            self.logger.error(f"CSV logging error: {str(e)}")
            return False
    
    def _log_json(self, data: Dict[str, Any]) -> bool:
        """Log data to JSON file."""
        try:
            # Read existing data
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as jsonfile:
                    try:
                        existing_data = json.load(jsonfile)
                    except json.JSONDecodeError:
                        existing_data = []
            else:
                existing_data = []
            
            # Append new data
            existing_data.append(data)
            
            # Write back to file
            with open(self.filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(existing_data, jsonfile, indent=2, ensure_ascii=False)
                self.logger.debug(f"Logged to JSON: {data}")
                return True
                
        except Exception as e:
            self.logger.error(f"JSON logging error: {str(e)}")
            return False
    
    def log_batch(self, data_list: List[Dict[str, Any]]) -> int:
        """
        Log multiple data items in batch.
        
        Args:
            data_list (list): List of data dictionaries
        
        Returns:
            int: Number of successfully logged items
        """
        success_count = 0
        for data in data_list:
            try:
                if self.log(data):
                    success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to log batch item: {str(e)}")
        
        self.logger.info(f"Batch log completed: {success_count}/{len(data_list)} successful")
        return success_count
    
    def read_data(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Read logged data from file.
        
        Args:
            limit (int, optional): Maximum number of records to return
        
        Returns:
            list: List of logged data
        
        Raises:
            IOError: If file operations fail
        """
        try:
            if not os.path.exists(self.filename):
                return []
            
            if self.format_type == "csv":
                return self._read_csv(limit)
            elif self.format_type == "json":
                return self._read_json(limit)
                
        except Exception as e:
            self.logger.error(f"Failed to read data: {str(e)}")
            raise IOError(f"Failed to read data: {str(e)}")
    
    def _read_csv(self, limit: int = None) -> List[Dict[str, Any]]:
        """Read data from CSV file."""
        data = []
        with open(self.filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if limit and i >= limit:
                    break
                
                # Parse metadata JSON
                try:
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                except json.JSONDecodeError:
                    metadata = {}
                
                # Reconstruct data
                record = {
                    'timestamp': row['timestamp'],
                    'name': row['name'],
                    'value': row['value']
                }
                record.update(metadata)
                data.append(record)
        
        return data
    
    def _read_json(self, limit: int = None) -> List[Dict[str, Any]]:
        """Read data from JSON file."""
        with open(self.filename, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            if limit:
                return data[-limit:]  # Return latest records
            return data
    
    def clear_data(self) -> bool:
        """
        Clear all logged data.
        
        Returns:
            bool: True if cleared successfully
        """
        try:
            self._initialize_file()
            self.logger.info(f"Cleared data file: {self.filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear data: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about logged data.
        
        Returns:
            dict: Statistics including record count, file size, etc.
        """
        stats = {
            'filename': self.filename,
            'format': self.format_type,
            'exists': os.path.exists(self.filename),
            'size_bytes': 0,
            'record_count': 0,
            'last_modified': None
        }
        
        if stats['exists']:
            try:
                # File size
                stats['size_bytes'] = os.path.getsize(self.filename)
                
                # Last modified time
                mtime = os.path.getmtime(self.filename)
                stats['last_modified'] = datetime.fromtimestamp(mtime).isoformat()
                
                # Record count
                if self.format_type == "csv":
                    with open(self.filename, 'r', encoding='utf-8') as csvfile:
                        reader = csv.reader(csvfile)
                        stats['record_count'] = sum(1 for row in reader) - 1  # Subtract header
                elif self.format_type == "json":
                    with open(self.filename, 'r', encoding='utf-8') as jsonfile:
                        data = json.load(jsonfile)
                        stats['record_count'] = len(data)
                        
            except Exception as e:
                self.logger.error(f"Failed to get stats: {str(e)}")
        
        return stats


class MultiLogger:
    """
    Logger that can write to multiple files simultaneously.
    """
    
    def __init__(self):
        """Initialize multi-logger."""
        self.loggers = {}
        self.logger = logging.getLogger("iotkit.multilogger")
    
    def add_logger(self, name: str, logger: DataLogger):
        """
        Add a logger to the collection.
        
        Args:
            name (str): Name for the logger
            logger (DataLogger): DataLogger instance
        """
        self.loggers[name] = logger
        self.logger.info(f"Added logger '{name}': {logger.filename}")
    
    def remove_logger(self, name: str):
        """
        Remove a logger from the collection.
        
        Args:
            name (str): Name of the logger to remove
        """
        if name in self.loggers:
            del self.loggers[name]
            self.logger.info(f"Removed logger '{name}'")
    
    def log(self, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, bool]:
        """
        Log data to all loggers.
        
        Args:
            data (dict): Data to log
            metadata (dict, optional): Additional metadata
        
        Returns:
            dict: Results from each logger
        """
        results = {}
        for name, logger in self.loggers.items():
            try:
                results[name] = logger.log(data, metadata)
            except Exception as e:
                self.logger.error(f"Logger '{name}' failed: {str(e)}")
                results[name] = False
        
        return results
    
    def get_loggers(self) -> List[str]:
        """
        Get list of logger names.
        
        Returns:
            list: List of logger names
        """
        return list(self.loggers.keys())