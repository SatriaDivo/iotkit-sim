# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-06

### Added
- **Core IoT Simulation Framework**
  - Virtual sensor system with random and manual modes
  - Sensor collections for batch operations
  - Comprehensive data validation and utilities

- **Communication Protocols**
  - MQTT Publisher and Subscriber with auto-reconnection
  - HTTP REST API client with authentication support
  - **WebSocket Support** for real-time bidirectional communication
    - WebSocketPublisher for sending data
    - WebSocketSubscriber for receiving data  
    - WebSocketServer for hosting WebSocket endpoints
    - WebSocketBridge for connecting multiple endpoints

- **Data Logging System**
  - CSV and JSON format support
  - Multi-logger for simultaneous logging
  - Batch operations and data statistics

- **Configuration Management**
  - YAML and JSON configuration file support
  - Environment-based configuration
  - Configuration validation and defaults

- **Utilities and Tools**
  - Timestamp generation (ISO, Unix formats)
  - Device ID generation
  - Data validation and sanitization
  - URL and MQTT topic validation
  - Retry mechanisms and error handling

- **Examples and Documentation**
  - Comprehensive examples for all features
  - WebSocket real-time streaming examples
  - Configuration management examples
  - Complete README with usage guides

### Technical Details
- **Python 3.8+ Support** - Compatible with modern Python versions
- **Async/Threading Support** - Non-blocking operations for real-time applications
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Comprehensive Error Handling** - Robust exception handling throughout
- **Type Hints** - Full type annotation support
- **Logging Integration** - Built-in logging for debugging and monitoring

### Dependencies
- `paho-mqtt>=1.6.0` - MQTT communication
- `requests>=2.25.0` - HTTP client functionality  
- `PyYAML>=6.0` - YAML configuration support
- `websockets>=11.0` - WebSocket real-time communication

### Package Structure
```
iotkit-sim/
├── iotkit/
│   ├── __init__.py          # Main package exports
│   ├── sensor.py            # Virtual sensor implementations
│   ├── mqtt.py              # MQTT communication
│   ├── http.py              # HTTP REST client
│   ├── websocket.py         # WebSocket communication (NEW)
│   ├── logger.py            # Data logging system
│   ├── config.py            # Configuration management
│   └── utils.py             # Utilities and helpers
├── examples/
│   ├── example.py           # Basic usage example
│   ├── example_config.py    # Configuration example
│   └── example_websocket.py # WebSocket examples
├── README.md                # Comprehensive documentation
├── setup.py                 # Package setup
└── requirements.txt         # Dependencies
```

### Breaking Changes
- None (initial release)

### Migration Guide
- This is the initial release, no migration needed

### Known Issues
- WebSocket connections may need manual reconnection in some network environments
- Large batch operations may require memory optimization for very large datasets

### Contributors
- Satria Divo (satriadivop354@gmail.com) - Lead Developer

---

## Release Notes

### v1.0.0 Highlights

🎉 **Initial Release of IoTKit-Sim** - A comprehensive IoT simulation and communication library!

**Key Features:**
- 🔬 **Virtual Sensors** - Simulate any IoT sensor with random or manual data
- 📡 **MQTT Integration** - Full publisher/subscriber support  
- 🌐 **HTTP REST API** - Easy integration with web services
- ⚡ **WebSocket Support** - Real-time bidirectional communication
- 📊 **Data Logging** - CSV/JSON logging with batch operations
- ⚙️ **Configuration Management** - YAML/JSON config support
- 🛡️ **Error Handling** - Robust exception handling throughout

**Perfect for:**
- IoT prototyping and development
- Educational IoT projects
- Testing IoT applications
- Real-time data simulation
- Learning IoT concepts

**Get Started:**
```bash
pip install iotkit-sim
```

```python
from iotkit import Sensor, WebSocketServer
sensor = Sensor("temperature", 20, 30)
ws_server = WebSocketServer("localhost", 8765)
ws_server.start()
ws_server.broadcast(sensor.to_dict())
```