# IoTKit-Sim - IoT Simulation and Communication Library

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/badge/pypi-iotkit--sim-orange.svg)](https://pypi.org/project/iotkit-sim)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

IoTKit-Sim adalah library Python yang komprehensif untuk simulasi perangkat IoT dan komunikasi data. Library ini dirancang untuk memudahkan pembelajaran dan praktikum IoT dengan menyediakan sensor virtual, komunikasi MQTT, HTTP REST API, dan logging data.

## ✨ Fitur Utama

- **🔬 Sensor Virtual**: Simulasi berbagai jenis sensor dengan mode random atau manual
- **📡 MQTT Communication**: Publisher dan subscriber untuk protokol MQTT
- **🌐 HTTP REST API**: Client untuk mengirim data melalui HTTP/HTTPS
- **⚡ WebSocket Support**: Real-time bidirectional communication dengan WebSocket
- **📊 Data Logging**: Penyimpanan data ke file CSV atau JSON
- **⚙️ Utilities**: Fungsi utilitas untuk validasi, timestamp, dan konfigurasi
- **🔒 Authentication**: Dukungan Bearer Token untuk HTTP
- **📦 Batch Operations**: Operasi batch untuk efisiensi
- **🛡️ Exception Handling**: Penanganan error yang robust

## 📦 Instalasi

### Instalasi dari PyPI
```bash
pip install iotkit-sim
```

### Instalasi dari Source
```bash
# Download source code dan ekstrak ke folder
cd iotkit-sim
pip install -e .
```

### Dependencies
Library ini membutuhkan dependencies berikut:
```bash
pip install paho-mqtt requests PyYAML websockets
```

Atau install dengan extras:
```bash
pip install iotkit-sim[dev]  # Untuk development
```

## 🚀 Quick Start

### Contoh Penggunaan Dasar

```python
from iotkit import Sensor, MQTTPublisher, HTTPPublisher, WebSocketPublisher, DataLogger
import time

# Buat sensor suhu
sensor = Sensor("suhu", min_val=20, max_val=30)

# Setup komunikasi
mqtt_pub = MQTTPublisher(broker="mqtt.eclipse.org", topic="sensor/suhu")
http_pub = HTTPPublisher(url="http://localhost:5000/api/sensor")
ws_pub = WebSocketPublisher("ws://localhost:8765")
logger = DataLogger("sensor_log.csv")

# Loop pengiriman data
while True:
    data = sensor.to_dict()
    
    # Kirim via MQTT
    mqtt_pub.connect()
    mqtt_pub.publish(data)
    
    # Kirim via HTTP
    http_pub.send(data)
    
    # Kirim via WebSocket
    ws_pub.start()
    ws_pub.send(data)
    
    # Log ke file
    logger.log(data)
    
    print("Terkirim:", data)
    time.sleep(2)
```

## 📚 Dokumentasi Lengkap

### Sensor Virtual

#### Membuat Sensor
```python
from iotkit import Sensor

# Sensor dengan nilai random
temp_sensor = Sensor("temperature", min_val=18, max_val=35, mode="random")

# Sensor dengan nilai manual
pressure_sensor = Sensor("pressure", min_val=0, max_val=100, mode="manual")
pressure_sensor.set_value(25.5)
```

#### Membaca Data Sensor
```python
# Baca nilai sensor
value = sensor.read()
print(f"Sensor value: {value}")

# Baca dalam format dictionary (dengan timestamp)
data = sensor.to_dict()
print(data)
# Output: {'name': 'temperature', 'value': 23.5, 'timestamp': '2023-...', ...}
```

#### Koleksi Multi-Sensor
```python
from iotkit import SensorCollection

collection = SensorCollection()
collection.add_sensor(Sensor("temp", 20, 30))
collection.add_sensor(Sensor("humidity", 40, 80))

# Baca semua sensor sekaligus
all_data = collection.read_all()
```

### MQTT Communication

#### MQTT Publisher
```python
from iotkit import MQTTPublisher

# Buat publisher
publisher = MQTTPublisher(
    broker="mqtt.eclipse.org",
    topic="iotkit/sensors",
    port=1883,
    username="user",  # optional
    password="pass"   # optional
)

# Connect dan publish
publisher.connect()
publisher.publish({"temp": 25.5, "timestamp": "2023-..."})
publisher.disconnect()
```

#### MQTT Subscriber
```python
from iotkit import MQTTSubscriber

def on_message_received(topic, data):
    print(f"Received from {topic}: {data}")

# Buat subscriber
subscriber = MQTTSubscriber(
    broker="mqtt.eclipse.org",
    topic="iotkit/sensors",
    on_message=on_message_received
)

# Connect dan listen
subscriber.connect()
subscriber.start_listening()  # Blocking
# atau
subscriber.start_listening_async()  # Non-blocking
```

### WebSocket Real-time Communication

#### WebSocket Publisher
```python
from iotkit import WebSocketPublisher

# Buat WebSocket publisher
ws_publisher = WebSocketPublisher("ws://your-websocket-server.com")

# Start publisher
ws_publisher.start()

# Kirim data
data = {"temperature": 25.5, "timestamp": "2025-01-01T10:00:00Z"}
success = ws_publisher.send(data)

# Stop publisher
ws_publisher.stop()
```

#### WebSocket Subscriber
```python
from iotkit import WebSocketSubscriber

def on_message_received(data):
    print(f"Received: {data}")

# Buat subscriber
ws_subscriber = WebSocketSubscriber(
    uri="ws://your-websocket-server.com",
    on_message=on_message_received
)

# Start listening
ws_subscriber.start()

# Stop subscriber
ws_subscriber.stop()
```

#### WebSocket Server
```python
from iotkit import WebSocketServer

def on_client_message(websocket, data, client_address):
    print(f"Message from {client_address}: {data}")

def on_client_connect(websocket, client_address):
    print(f"Client connected: {client_address}")

# Buat WebSocket server
ws_server = WebSocketServer(
    host="localhost",
    port=8765,
    on_message=on_client_message,
    on_connect=on_client_connect
)

# Start server
ws_server.start()

# Broadcast ke semua client
ws_server.broadcast({"message": "Hello all clients!"})

# Stop server
ws_server.stop()
```

#### WebSocket Bridge
```python
from iotkit import WebSocketBridge

# Buat bridge untuk menghubungkan multiple WebSocket
bridge = WebSocketBridge(server_port=8766)

# Start bridge
bridge.start()

# Tambah publisher eksternal
bridge.add_publisher("external_api", "ws://external-api.com/websocket")

# Tambah subscriber eksternal
bridge.add_subscriber("data_feed", "ws://data-feed.com/stream")

# Cek status bridge
status = bridge.get_status()
print(f"Bridge status: {status}")

# Stop bridge
bridge.stop()
```

#### Streaming Sensor Data via WebSocket
```python
from iotkit import Sensor, WebSocketServer
import threading
import time

# Setup sensors
sensor = Sensor("temperature", 20, 30)

# Setup WebSocket server
ws_server = WebSocketServer("localhost", 8767)
ws_server.start()

def stream_data():
    while True:
        data = sensor.to_dict()
        ws_server.broadcast(data)
        time.sleep(2)

# Start streaming in background
stream_thread = threading.Thread(target=stream_data, daemon=True)
stream_thread.start()
```

### HTTP REST API

#### HTTP Publisher
```python
from iotkit import HTTPPublisher

# Basic HTTP client
http_client = HTTPPublisher(url="https://api.example.com/sensors")

# Dengan authentication
auth_client = HTTPPublisher(
    url="https://api.example.com/sensors",
    auth_token="your-bearer-token"
)

# Kirim data
response = http_client.send({"temp": 25.5})
print(response)
```

#### Batch Sending
```python
# Kirim multiple data sekaligus
batch_data = [
    {"temp": 25.5},
    {"temp": 26.1},
    {"temp": 24.8}
]

results = http_client.send_batch(batch_data)
```

### Data Logging

#### CSV Logger
```python
from iotkit import DataLogger

# Logger CSV
csv_logger = DataLogger("data.csv", format_type="csv")
csv_logger.log({"sensor": "temp", "value": 25.5})
```

#### JSON Logger
```python
# Logger JSON
json_logger = DataLogger("data.json", format_type="json")
json_logger.log({"sensor": "temp", "value": 25.5})
```

#### Batch Logging
```python
# Log multiple data
batch_data = [sensor.to_dict() for _ in range(10)]
success_count = logger.log_batch(batch_data)
```

#### Membaca Data Log
```python
# Baca semua data
all_data = logger.read_data()

# Baca data terbatas
recent_data = logger.read_data(limit=100)

# Statistik file
stats = logger.get_stats()
print(f"Records: {stats['record_count']}, Size: {stats['size_bytes']} bytes")
```

### Multi-Logger
```python
from iotkit import MultiLogger, DataLogger

multi = MultiLogger()
multi.add_logger("csv", DataLogger("data.csv", "csv"))
multi.add_logger("json", DataLogger("data.json", "json"))

# Log ke semua logger sekaligus
results = multi.log({"temp": 25.5})
```

## 🛠️ Utilities

### Validasi Data
```python
from iotkit import validate_data, validate_url, validate_mqtt_topic

# Validasi data sensor
valid_data = validate_data({"name": "temp", "value": 25.5})

# Validasi URL
is_valid = validate_url("https://api.example.com")

# Validasi MQTT topic
is_valid = validate_mqtt_topic("sensors/temperature")
```

### Timestamp dan ID
```python
from iotkit import generate_timestamp, generate_device_id

# Generate timestamp
timestamp = generate_timestamp()  # ISO format
timestamp_unix = generate_timestamp("unix")

# Generate device ID
device_id = generate_device_id("sensor")  # sensor_abc123def
```

### Configuration
```python
from iotkit import config

# Get configuration
mqtt_port = config.get('mqtt.default_port')  # 1883

# Set configuration
config.set('mqtt.default_port', 1884)

# Load dari file
config.load_from_file('config.json')
```

### Buffer untuk Batch Operations
```python
from iotkit import DataBuffer

buffer = DataBuffer(max_size=10)
buffer.add({"temp": 25.5})

if buffer.is_full():
    data = buffer.get_all()  # Get and clear
    # Process batch data
```

## 🔧 Konfigurasi Lanjutan

### Logging Configuration
```python
from iotkit import setup_logging
import logging

# Setup logging level
logger = setup_logging(level="DEBUG")

# Custom format
logger = setup_logging(
    level="INFO",
    format_string="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
```

### Custom Headers HTTP
```python
http_client = HTTPPublisher(
    url="https://api.example.com",
    headers={
        "X-API-Key": "your-api-key",
        "X-Custom-Header": "value"
    }
)

# Update headers
http_client.add_header("Authorization", "Bearer new-token")
http_client.remove_header("X-Custom-Header")
```

### Configuration Management
IoTKit mendukung konfigurasi melalui file YAML atau JSON untuk memudahkan pengelolaan pengaturan aplikasi.

#### Menggunakan Configuration Manager
```python
from iotkit import ConfigManager

# Load konfigurasi dari file
config = ConfigManager("config.yaml")  # atau config.json

# Akses konfigurasi menggunakan dot notation
mqtt_broker = config.get("mqtt.broker")
http_timeout = config.get("http.timeout", 30)  # dengan default value

# Update konfigurasi
config.set("mqtt.port", 1884)
config.set("sensors.default_mode", "manual")

# Simpan perubahan
config.save_config()
```

#### Contoh File Konfigurasi (YAML)
```yaml
# config.yaml
mqtt:
  broker: "mqtt.eclipseprojects.io"
  port: 1883
  topic_prefix: "iotkit"
  
http:
  base_url: "http://localhost:5000/api"
  timeout: 30
  
sensors:
  default_mode: "random"
  reading_interval: 2.0
  temperature:
    min_val: 20.0
    max_val: 30.0
    unit: "°C"
    
logging:
  log_level: "INFO"
  file_format: "csv"
  auto_timestamp: true
```

#### Contoh File Konfigurasi (JSON)
```json
{
  "mqtt": {
    "broker": "mqtt.eclipseprojects.io",
    "port": 1883,
    "topic_prefix": "iotkit"
  },
  "http": {
    "base_url": "http://localhost:5000/api",
    "timeout": 30
  },
  "sensors": {
    "default_mode": "random",
    "reading_interval": 2.0,
    "temperature": {
      "min_val": 20.0,
      "max_val": 30.0,
      "unit": "°C"
    }
  }
}
```

#### Menggunakan Konfigurasi dengan Komponen IoTKit
```python
from iotkit import ConfigManager, Sensor, MQTTPublisher, HTTPPublisher

# Load konfigurasi
config = ConfigManager("config.yaml")

# Buat komponen menggunakan konfigurasi
mqtt_config = config.get_mqtt_config()
mqtt_pub = MQTTPublisher(
    broker=mqtt_config["broker"],
    topic=f"{mqtt_config['topic_prefix']}/sensors",
    port=mqtt_config["port"]
)

http_config = config.get_http_config()
http_pub = HTTPPublisher(
    url=f"{http_config['base_url']}/sensors",
    timeout=http_config["timeout"]
)

# Sensor dengan konfigurasi
sensor_config = config.get("sensors.temperature")
temp_sensor = Sensor(
    "temperature",
    min_val=sensor_config["min_val"],
    max_val=sensor_config["max_val"]
)
```

#### Validasi Konfigurasi
```python
# Validasi konfigurasi sebelum digunakan
try:
    config.validate_config()
    print("Konfigurasi valid!")
except ValueError as e:
    print(f"Konfigurasi tidak valid: {e}")

# Reset ke default jika perlu
config.reset_to_defaults()
```

## 📊 Contoh Aplikasi Lengkap

### Monitoring Sistem Greenhouse
```python
from iotkit import *
import time
import threading

# Setup sensors
sensors = SensorCollection()
sensors.add_sensor(Sensor("temperature", 18, 35))
sensors.add_sensor(Sensor("humidity", 40, 90))
sensors.add_sensor(Sensor("soil_moisture", 20, 80))

# Setup komunikasi
mqtt_pub = MQTTPublisher("mqtt.eclipse.org", "greenhouse/sensors")
http_pub = HTTPPublisher("https://api.greenhouse.com/data", 
                        auth_token="your-token")
ws_pub = WebSocketPublisher("ws://greenhouse-monitor.com/stream")

# Setup logging
csv_logger = DataLogger("greenhouse_data.csv")
json_logger = DataLogger("greenhouse_backup.json", "json")
multi_logger = MultiLogger()
multi_logger.add_logger("csv", csv_logger)
multi_logger.add_logger("json", json_logger)

def collect_and_send():
    while True:
        # Baca semua sensor
        all_data = sensors.read_all()
        
        for sensor_name, data in all_data.items():
            try:
                # Kirim via MQTT
                mqtt_pub.publish(data, topic=f"greenhouse/{sensor_name}")
                
                # Kirim via HTTP
                http_pub.send(data, endpoint=f"sensors/{sensor_name}")
                
                # Kirim via WebSocket
                ws_pub.send(data)
                
                # Log data
                multi_logger.log(data)
                
                print(f"✓ {sensor_name}: {data['value']}")
                
            except Exception as e:
                print(f"✗ Error sending {sensor_name}: {e}")
        
        time.sleep(30)  # Kirim setiap 30 detik

# Jalankan dalam thread
mqtt_pub.connect()
ws_pub.start()
thread = threading.Thread(target=collect_and_send, daemon=True)
thread.start()

# Keep main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping greenhouse monitoring...")
    mqtt_pub.disconnect()
    ws_pub.stop()
```

## ⚠️ Exception Handling

Library ini memiliki exception handling yang robust:

```python
from iotkit import *

try:
    sensor = Sensor("test", 0, 100, mode="manual")
    sensor.read()  # Will raise ValueError (no manual value set)
except ValueError as e:
    print(f"Sensor error: {e}")

try:
    mqtt_pub = MQTTPublisher("invalid-broker", "test")
    mqtt_pub.connect()
except ConnectionError as e:
    print(f"MQTT connection failed: {e}")

try:
    http_pub = HTTPPublisher("invalid-url")
    http_pub.send({"test": "data"})
except ConnectionError as e:
    print(f"HTTP request failed: {e}")
```

## 🧪 Testing

Jalankan contoh penggunaan:
```bash
python example.py
```

## 📁 Struktur Project

```
iotkit/
├── __init__.py          # Main imports dan setup
├── sensor.py            # Virtual sensors
├── mqtt.py              # MQTT communication
├── http.py              # HTTP REST client
├── logger.py            # Data logging
└── utils.py             # Utilities dan helpers

example.py               # Contoh penggunaan
README.md               # Dokumentasi ini
setup.py                # Setup untuk PyPI
requirements.txt        # Dependencies
```

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## �‍💻 Author

**Satria Divo**
- Email: satriadivop354@gmail.com

## �📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙋‍♂️ Support

Jika ada pertanyaan atau masalah:

- Email: satriadivop354@gmail.com

## 🚀 Roadmap

- [x] WebSocket support
- [ ] LoRaWAN integration
- [ ] Real-time dashboard
- [ ] Machine learning integration
- [ ] Cloud platform connectors (AWS IoT, Azure IoT, etc.)
- [ ] Protocol simulation (CoAP, LwM2M)
- [ ] Device management features

---

⭐ Jika project ini membantu, jangan lupa untuk share ke teman-teman!