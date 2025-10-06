#!/usr/bin/env python3
"""
IoTKit Example Usage

This example demonstrates how to use the IoTKit library for IoT simulation
and communication.
"""

from iotkit import Sensor, MQTTPublisher, HTTPPublisher, DataLogger
import time
import logging

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)

def main():
    """Main example function."""
    print("=== IoTKit Example ===")
    
    # Create a temperature sensor
    sensor = Sensor("suhu", min_val=20, max_val=30, mode="random")
    print(f"Created sensor: {sensor.name}")
    
    # Create MQTT publisher (using public test broker)
    try:
        mqtt_pub = MQTTPublisher(broker="mqtt.eclipseprojects.io", topic="iotkit/sensor/suhu")
        print("MQTT Publisher created")
    except Exception as e:
        print(f"MQTT Publisher creation failed: {e}")
        mqtt_pub = None
    
    # Create HTTP publisher (example endpoint - will likely fail)
    try:
        http_pub = HTTPPublisher(url="http://localhost:5000/api/sensor")
        print("HTTP Publisher created")
    except Exception as e:
        print(f"HTTP Publisher creation failed: {e}")
        http_pub = None
    
    # Create data logger
    logger = DataLogger("sensor_log.csv")
    print("Data Logger created")
    
    print("\nStarting data collection and transmission...")
    print("Press Ctrl+C to stop")
    
    try:
        # Connect to MQTT broker if available
        if mqtt_pub:
            try:
                mqtt_pub.connect()
                print("Connected to MQTT broker")
            except Exception as e:
                print(f"MQTT connection failed: {e}")
                mqtt_pub = None
        
        # Main loop
        for i in range(10):  # Run for 10 iterations
            # Read sensor data
            data = sensor.to_dict()
            print(f"\nIteration {i+1}: {data}")
            
            # Publish to MQTT
            if mqtt_pub:
                try:
                    mqtt_pub.publish(data)
                    print("✓ Sent to MQTT")
                except Exception as e:
                    print(f"✗ MQTT send failed: {e}")
            
            # Send via HTTP
            if http_pub:
                try:
                    response = http_pub.send(data)
                    print("✓ Sent via HTTP")
                except Exception as e:
                    print(f"✗ HTTP send failed: {e}")
            
            # Log to file
            try:
                logger.log(data)
                print("✓ Logged to file")
            except Exception as e:
                print(f"✗ Logging failed: {e}")
            
            # Wait before next iteration
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    finally:
        # Cleanup
        if mqtt_pub and mqtt_pub.connected:
            mqtt_pub.disconnect()
            print("Disconnected from MQTT")
        
        # Show logged data statistics
        try:
            stats = logger.get_stats()
            print(f"\nLogging statistics:")
            print(f"  File: {stats['filename']}")
            print(f"  Records: {stats['record_count']}")
            print(f"  Size: {stats['size_bytes']} bytes")
        except Exception as e:
            print(f"Failed to get stats: {e}")


def demo_manual_sensor():
    """Demonstrate manual sensor mode."""
    print("\n=== Manual Sensor Demo ===")
    
    # Create manual sensor
    manual_sensor = Sensor("pressure", min_val=0, max_val=100, mode="manual")
    
    # Set some values manually
    values = [25.5, 30.2, 28.9, 32.1, 29.8]
    
    for value in values:
        manual_sensor.set_value(value)
        data = manual_sensor.to_dict()
        print(f"Manual sensor reading: {data}")


def demo_multiple_sensors():
    """Demonstrate multiple sensors with SensorCollection."""
    print("\n=== Multiple Sensors Demo ===")
    
    from iotkit import SensorCollection
    
    # Create sensor collection
    collection = SensorCollection()
    
    # Add multiple sensors
    sensors_config = [
        {"name": "temperature", "min_val": 18, "max_val": 35, "mode": "random"},
        {"name": "humidity", "min_val": 30, "max_val": 90, "mode": "random"},
        {"name": "pressure", "min_val": 990, "max_val": 1030, "mode": "random"},
    ]
    
    for config in sensors_config:
        sensor = Sensor(**config)
        collection.add_sensor(sensor)
    
    print(f"Created collection with sensors: {collection.list_sensors()}")
    
    # Read all sensors
    all_data = collection.read_all()
    for sensor_name, data in all_data.items():
        print(f"{sensor_name}: {data}")


def demo_batch_logging():
    """Demonstrate batch logging."""
    print("\n=== Batch Logging Demo ===")
    
    # Create JSON logger
    json_logger = DataLogger("batch_data.json", format_type="json")
    
    # Generate batch data
    batch_data = []
    for i in range(5):
        sensor = Sensor(f"sensor_{i}", min_val=0, max_val=100)
        data = sensor.to_dict()
        batch_data.append(data)
    
    # Log batch
    success_count = json_logger.log_batch(batch_data)
    print(f"Batch logged: {success_count}/{len(batch_data)} successful")
    
    # Read back the data
    logged_data = json_logger.read_data()
    print(f"Read back {len(logged_data)} records")


def demo_mqtt_subscriber():
    """Demonstrate MQTT subscriber (commented out as it's blocking)."""
    print("\n=== MQTT Subscriber Demo (Info Only) ===")
    print("MQTT Subscriber example:")
    print("""
    from iotkit import MQTTSubscriber
    
    def on_message_received(topic, data):
        print(f"Received from {topic}: {data}")
    
    # Create subscriber
    subscriber = MQTTSubscriber(
        broker="mqtt.eclipseprojects.io",
        topic="iotkit/sensor/+",  # Subscribe to all sensor topics
        on_message=on_message_received
    )
    
    # Connect and start listening
    subscriber.connect()
    subscriber.start_listening()  # This blocks
    """)


if __name__ == "__main__":
    main()
    
    # Run additional demos
    demo_manual_sensor()
    demo_multiple_sensors()
    demo_batch_logging()
    demo_mqtt_subscriber()
    
    print("\n=== Example completed ===")
    print("Check the generated log files:")
    print("  - sensor_log.csv")
    print("  - batch_data.json")