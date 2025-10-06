#!/usr/bin/env python3
"""
IoTKit Configuration Example

This example demonstrates how to use configuration files with IoTKit library.
"""

from iotkit import ConfigManager, Sensor, MQTTPublisher, HTTPPublisher, DataLogger
import time
import logging

def main():
    """Main example function demonstrating configuration usage."""
    print("=== IoTKit Configuration Example ===")
    
    # 1. Load configuration from YAML file
    print("\n1. Loading configuration from YAML file...")
    try:
        config = ConfigManager("config_example.yaml")
        print("✓ Configuration loaded successfully from YAML")
    except FileNotFoundError:
        print("✗ YAML config file not found, trying JSON...")
        try:
            config = ConfigManager("config_example.json")
            print("✓ Configuration loaded successfully from JSON")
        except FileNotFoundError:
            print("✗ No config file found, using default configuration")
            config = ConfigManager()
    
    # 2. Display loaded configuration
    print("\n2. Current Configuration:")
    print("MQTT Broker:", config.get("mqtt.broker"))
    print("MQTT Port:", config.get("mqtt.port"))
    print("HTTP Base URL:", config.get("http.base_url"))
    print("Sensor Default Mode:", config.get("sensors.default_mode"))
    print("Log Level:", config.get("logging.log_level"))
    
    # 3. Create sensors using configuration
    print("\n3. Creating sensors using configuration...")
    
    # Temperature sensor from config
    temp_config = config.get("sensors.temperature", {})
    temp_sensor = Sensor(
        "temperature",
        min_val=temp_config.get("min_val", 20),
        max_val=temp_config.get("max_val", 30),
        mode=config.get("sensors.default_mode", "random")
    )
    print(f"✓ Temperature sensor created: {temp_config.get('min_val', 20)}-{temp_config.get('max_val', 30)}°C")
    
    # Humidity sensor from config
    humidity_config = config.get("sensors.humidity", {})
    humidity_sensor = Sensor(
        "humidity",
        min_val=humidity_config.get("min_val", 40),
        max_val=humidity_config.get("max_val", 80),
        mode=config.get("sensors.default_mode", "random")
    )
    print(f"✓ Humidity sensor created: {humidity_config.get('min_val', 40)}-{humidity_config.get('max_val', 80)}%")
    
    # 4. Create communication components using configuration
    print("\n4. Setting up communication...")
    
    # MQTT Publisher
    mqtt_config = config.get_mqtt_config()
    try:
        mqtt_pub = MQTTPublisher(
            broker=mqtt_config["broker"],
            topic=f"{mqtt_config['topic_prefix']}/example",
            port=mqtt_config["port"],
            client_id_prefix=mqtt_config["client_id_prefix"]
        )
        print(f"✓ MQTT Publisher created: {mqtt_config['broker']}:{mqtt_config['port']}")
    except Exception as e:
        print(f"✗ MQTT Publisher creation failed: {e}")
        mqtt_pub = None
    
    # HTTP Publisher
    http_config = config.get_http_config()
    try:
        http_pub = HTTPPublisher(
            url=f"{http_config['base_url']}/sensors",
            timeout=http_config["timeout"],
            headers=http_config.get("headers", {})
        )
        print(f"✓ HTTP Publisher created: {http_config['base_url']}")
    except Exception as e:
        print(f"✗ HTTP Publisher creation failed: {e}")
        http_pub = None
    
    # 5. Create logger using configuration
    logging_config = config.get_logging_config()
    log_format = logging_config.get("file_format", "csv")
    log_dir = logging_config.get("log_directory", "logs")
    
    import os
    os.makedirs(log_dir, exist_ok=True)
    
    logger = DataLogger(f"{log_dir}/sensor_data_config.{log_format}", format_type=log_format)
    print(f"✓ Data Logger created: {log_dir}/sensor_data_config.{log_format}")
    
    # 6. Modify configuration at runtime
    print("\n5. Modifying configuration at runtime...")
    
    # Change reading interval
    old_interval = config.get("sensors.reading_interval", 2.0)
    config.set("sensors.reading_interval", 1.5)
    new_interval = config.get("sensors.reading_interval")
    print(f"Reading interval changed: {old_interval}s → {new_interval}s")
    
    # Add new sensor configuration
    config.set("sensors.pressure.min_val", 1000.0)
    config.set("sensors.pressure.max_val", 1100.0)
    config.set("sensors.pressure.unit", "hPa")
    print("✓ New pressure sensor configuration added")
    
    # 7. Validate configuration
    print("\n6. Validating configuration...")
    try:
        config.validate_config()
        print("✓ Configuration is valid")
    except ValueError as e:
        print(f"✗ Configuration validation failed: {e}")
    
    # 8. Save modified configuration
    print("\n7. Saving modified configuration...")
    try:
        config.save_config("modified_config.yaml")
        print("✓ Modified configuration saved to modified_config.yaml")
    except Exception as e:
        print(f"✗ Failed to save configuration: {e}")
    
    # 9. Data collection demonstration
    print("\n8. Starting data collection with configuration-based setup...")
    print("Collecting 5 samples...")
    
    reading_interval = config.get("sensors.reading_interval", 2.0)
    
    for i in range(5):
        # Read sensor data
        temp_data = temp_sensor.to_dict()
        humidity_data = humidity_sensor.to_dict()
        
        print(f"\nSample {i+1}:")
        print(f"  Temperature: {temp_data['value']}°C")
        print(f"  Humidity: {humidity_data['value']}%")
        
        # Log data
        logger.log(temp_data)
        logger.log(humidity_data)
        
        # Send via MQTT if available
        if mqtt_pub:
            try:
                mqtt_pub.connect()
                mqtt_pub.publish(temp_data)
                mqtt_pub.publish(humidity_data)
                print("  ✓ Data sent via MQTT")
            except Exception as e:
                print(f"  ✗ MQTT send failed: {e}")
        
        # Send via HTTP if available
        if http_pub:
            try:
                http_pub.send(temp_data)
                http_pub.send(humidity_data)
                print("  ✓ Data sent via HTTP")
            except Exception as e:
                print(f"  ✗ HTTP send failed: {e}")
        
        if i < 4:  # Don't sleep after last iteration
            time.sleep(reading_interval)
    
    # 10. Display configuration summary
    print("\n9. Configuration Summary:")
    print("=" * 50)
    print(f"MQTT: {config.get('mqtt.broker')}:{config.get('mqtt.port')}")
    print(f"HTTP: {config.get('http.base_url')}")
    print(f"Sensors: {len([k for k in config.config.get('sensors', {}).keys() if isinstance(config.config['sensors'][k], dict)])} configured")
    print(f"Log Format: {config.get('logging.file_format')}")
    print(f"Reading Interval: {config.get('sensors.reading_interval')}s")
    print("=" * 50)
    
    print("\n✓ Configuration example completed successfully!")
    print("\nFiles created:")
    print("- modified_config.yaml (modified configuration)")
    print(f"- {log_dir}/sensor_data_config.{log_format} (sensor data log)")

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()