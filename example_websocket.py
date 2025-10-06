#!/usr/bin/env python3
"""
IoTKit WebSocket Example

This example demonstrates how to use WebSocket functionality with IoTKit library
for real-time IoT data communication.
"""

import time
import threading
import logging
from iotkit import (
    Sensor, SensorCollection, DataLogger,
    WebSocketPublisher, WebSocketSubscriber, WebSocketServer, WebSocketBridge
)

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)

def basic_websocket_publisher_example():
    """Basic WebSocket publisher example."""
    print("=== WebSocket Publisher Example ===")
    
    # Create sensor
    sensor = Sensor("temperature", min_val=20, max_val=30, mode="random")
    
    # Create WebSocket publisher (connect to a WebSocket server)
    # For this example, we'll use a test WebSocket server
    # In practice, replace with your actual WebSocket server URL
    ws_publisher = WebSocketPublisher("ws://echo.websocket.org")
    
    try:
        # Start publisher
        ws_publisher.start()
        
        # Wait for connection
        time.sleep(2)
        
        if ws_publisher.is_connected():
            print("✓ Connected to WebSocket server")
            
            # Send sensor data
            for i in range(5):
                data = sensor.to_dict()
                success = ws_publisher.send(data)
                
                if success:
                    print(f"✓ Sent data: {data['value']}°C")
                else:
                    print("✗ Failed to send data")
                
                time.sleep(2)
        else:
            print("✗ Failed to connect to WebSocket server")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        ws_publisher.stop()


def basic_websocket_server_example():
    """Basic WebSocket server example."""
    print("\n=== WebSocket Server Example ===")
    
    def on_message_received(websocket, data, client_address):
        """Handle received messages."""
        print(f"Received from {client_address}: {data}")
        
        # Echo the message back
        response = {
            "echo": data,
            "server_timestamp": time.time(),
            "message": "Hello from IoTKit WebSocket Server!"
        }
        # Note: You would typically send response back through websocket
        # but for this example, we'll just print it
        print(f"Would send back: {response}")
    
    def on_client_connect(websocket, client_address):
        """Handle client connections."""
        print(f"✓ Client connected: {client_address}")
    
    def on_client_disconnect(websocket, client_address):
        """Handle client disconnections."""
        print(f"✗ Client disconnected: {client_address}")
    
    # Create WebSocket server
    ws_server = WebSocketServer(
        host="localhost",
        port=8765,
        on_message=on_message_received,
        on_connect=on_client_connect,
        on_disconnect=on_client_disconnect
    )
    
    try:
        # Start server
        ws_server.start()
        print("✓ WebSocket server started on localhost:8765")
        print("You can connect to it using: ws://localhost:8765")
        
        # Keep server running for demonstration
        print("Server running for 30 seconds...")
        time.sleep(30)
        
    except Exception as e:
        print(f"Server error: {e}")
    
    finally:
        ws_server.stop()
        print("✓ WebSocket server stopped")


def websocket_bridge_example():
    """WebSocket bridge example - connects multiple WebSocket endpoints."""
    print("\n=== WebSocket Bridge Example ===")
    
    # Create bridge
    bridge = WebSocketBridge(server_port=8766)
    
    try:
        # Start bridge server
        bridge.start()
        print("✓ WebSocket bridge started on localhost:8766")
        
        # Add external WebSocket connections (examples)
        # bridge.add_publisher("external_api", "ws://external-api.example.com/websocket")
        # bridge.add_subscriber("data_feed", "ws://data-feed.example.com/stream")
        
        print("Bridge running for 20 seconds...")
        print("Connect clients to: ws://localhost:8766")
        
        # Simulate sending data through bridge
        for i in range(3):
            test_data = {
                "sensor": "bridge_test",
                "value": 25.5 + i,
                "timestamp": time.time()
            }
            bridge.server.broadcast(test_data)
            print(f"✓ Broadcasted test data: {test_data}")
            time.sleep(5)
        
        # Show bridge status
        status = bridge.get_status()
        print(f"Bridge status: {status}")
        
    except Exception as e:
        print(f"Bridge error: {e}")
    
    finally:
        bridge.stop()
        print("✓ WebSocket bridge stopped")


def sensor_data_streaming_example():
    """Example of streaming sensor data via WebSocket."""
    print("\n=== Sensor Data Streaming Example ===")
    
    # Create multiple sensors
    sensors = SensorCollection()
    sensors.add_sensor(Sensor("temperature", 18, 35))
    sensors.add_sensor(Sensor("humidity", 40, 90))
    sensors.add_sensor(Sensor("pressure", 1000, 1100))
    
    # Create data logger
    logger = DataLogger("websocket_sensor_data.json", format_type="json")
    
    # WebSocket server for streaming data
    def on_client_message(websocket, data, client_address):
        print(f"Client {client_address} sent: {data}")
    
    ws_server = WebSocketServer(
        host="localhost",
        port=8767,
        on_message=on_client_message
    )
    
    def data_streaming_loop():
        """Continuous data streaming loop."""
        while True:
            try:
                # Read all sensors
                all_data = sensors.read_all()
                
                # Create streaming packet
                stream_data = {
                    "timestamp": time.time(),
                    "device_id": "iotkit_demo_device",
                    "sensors": all_data
                }
                
                # Log data
                logger.log(stream_data)
                
                # Broadcast to WebSocket clients
                ws_server.broadcast(stream_data)
                
                print(f"✓ Streamed sensor data to {ws_server.get_connected_clients_count()} clients")
                
                time.sleep(3)  # Stream every 3 seconds
                
            except Exception as e:
                print(f"Streaming error: {e}")
                break
    
    try:
        # Start WebSocket server
        ws_server.start()
        print("✓ Sensor streaming server started on localhost:8767")
        
        # Start data streaming in background thread
        stream_thread = threading.Thread(target=data_streaming_loop, daemon=True)
        stream_thread.start()
        
        print("Streaming sensor data for 25 seconds...")
        print("Connect to: ws://localhost:8767")
        time.sleep(25)
        
    except Exception as e:
        print(f"Streaming error: {e}")
    
    finally:
        ws_server.stop()
        print("✓ Sensor streaming stopped")


def websocket_subscriber_example():
    """WebSocket subscriber example."""
    print("\n=== WebSocket Subscriber Example ===")
    
    def on_data_received(data):
        """Handle received WebSocket data."""
        print(f"Subscriber received: {data}")
        
        # You could process the data here, e.g.:
        # - Save to database
        # - Forward to another system
        # - Trigger alerts based on values
    
    # Create WebSocket subscriber
    # For this example, we'll try to connect to a test WebSocket
    ws_subscriber = WebSocketSubscriber(
        uri="ws://echo.websocket.org",
        on_message=on_data_received
    )
    
    try:
        # Start subscriber
        ws_subscriber.start()
        print("✓ WebSocket subscriber started")
        
        # Wait for connection
        time.sleep(2)
        
        if ws_subscriber.is_connected():
            print("✓ Connected to WebSocket server")
            print("Listening for messages for 15 seconds...")
            time.sleep(15)
        else:
            print("✗ Failed to connect to WebSocket server")
    
    except Exception as e:
        print(f"Subscriber error: {e}")
    
    finally:
        ws_subscriber.stop()
        print("✓ WebSocket subscriber stopped")


def main():
    """Main function to run all examples."""
    print("🚀 IoTKit WebSocket Examples")
    print("=" * 50)
    
    try:
        # Run examples one by one
        basic_websocket_publisher_example()
        
        # Note: Server examples need to run separately or they'll block each other
        # Uncomment one at a time to test:
        
        # basic_websocket_server_example()
        # websocket_bridge_example()
        # sensor_data_streaming_example()
        # websocket_subscriber_example()
        
        print("\n" + "=" * 50)
        print("✅ WebSocket examples completed!")
        print("\nTo test server examples:")
        print("1. Uncomment one server example at a time")
        print("2. Run this script")
        print("3. Connect using WebSocket client (browser, curl, etc.)")
        print("\nExample WebSocket clients:")
        print("- Browser: Use browser developer tools")
        print("- curl: curl --include --no-buffer --header 'Connection: Upgrade' --header 'Upgrade: websocket' --header 'Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==' --header 'Sec-WebSocket-Version: 13' http://localhost:8765/")
        print("- Python: Use websockets library client")
        
    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()