# Web Interface and Serial Monitor

This directory contains additional tools for monitoring Samsung NASA protocol communication.

## Web Interface

A Vue.js-based web interface for real-time monitoring of NASA state values.

### Features

- **Real-time Updates**: WebSocket-based live updates of NASA state values
- **Interactive Dashboard**: Modern, responsive UI with card-based layout
- **Filtering**: Search and filter values by key or value
- **Sorting**: Sort values by key or value
- **Visual Feedback**: Animated highlights when values change
- **Connection Status**: Real-time connection status indicator

### Running the Web Interface

#### Option 1: Integrated with samsung_mqtt_home_assistant.py

Run the main application with the web interface enabled:

```bash
python3 run_with_web_interface.py --mqtt-host localhost --mqtt-port 1883 --web-port 5000
```

Then open your browser to: http://localhost:5000

#### Option 2: Standalone API Server

If you want to run just the web API without the full MQTT integration:

```bash
python3 web_api.py
```

### Command-Line Options

When using `run_with_web_interface.py`:

- `--web-port PORT`: Port for web interface (default: 5000)
- `--web-host HOST`: Host for web interface (default: 0.0.0.0, accessible from network)
- `--no-web`: Disable web interface

All other arguments are passed through to `samsung_mqtt_home_assistant.py`.

### API Endpoints

The web interface provides REST API endpoints:

- `GET /`: Serve the Vue.js web interface
- `GET /api/state`: Get current NASA state as JSON
- `GET /api/mqtt_vars`: Get list of published MQTT variables
- WebSocket: Real-time state updates via Socket.IO

### Example API Usage

```bash
# Get current state
curl http://localhost:5000/api/state

# Get MQTT variables
curl http://localhost:5000/api/mqtt_vars
```

## Serial Monitor Tool

A simple read-only tool for monitoring serial line communication.

### Features

- **Read-only Monitoring**: Safely monitor the serial line without sending any data
- **Raw Data Display**: Show raw hex data with formatted hex dump
- **NASA Packet Parsing**: Automatically parse and decode NASA protocol packets
- **Packet Counter**: Track number of packets received
- **Flexible Display**: Choose between raw data, parsed data, or both

### Usage

#### Basic Monitoring

Monitor the serial line and parse NASA packets:

```bash
python3 serial_monitor.py --host 127.0.0.1 --port 7001
```

#### Raw Data Only

Show only raw hex data without parsing:

```bash
python3 serial_monitor.py --host 127.0.0.1 --port 7001 --no-parse
```

#### Remote Connection

Connect to an Ethernet-to-RS485 converter:

```bash
python3 serial_monitor.py --host 192.168.1.100 --port 8080
```

### Command-Line Options

- `--host HOST`: Host/IP address to connect to (default: 127.0.0.1)
- `--port PORT`: TCP port to connect to (default: 7001)
- `--no-parse`: Disable NASA packet parsing, show raw data only
- `--raw-only`: Show only raw hex data without hex dump
- `--log-level LEVEL`: Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)

### Example Output

```
================================================================================
[2026-01-23 12:34:56] Packet #1
================================================================================
RAW: 320029200000b0ffff40144a0104000100010101140242080003

HEX DUMP:
  0000:  32 00 29 20 00 00 b0 ff ff 40 14 4a 01 04 00 01  2.) .....@.J....
  0010:  00 01 01 01 14 02 42 08 00 03                    ......B...

PARSED NASA PACKET:
  Source: 200000
  Destination: b0ffff
  Packet Type: normal
  Payload Type: notification
  Packet Number: 74
  Data Sets (1):
    [1] NASA_OP_MODE_HEATING (0x4000): 1
================================================================================
```

### Use Cases

1. **Debugging Communication**: Monitor the serial line to debug communication issues
2. **Protocol Analysis**: Analyze NASA protocol packets to understand the communication
3. **Development**: Test new features without risking data corruption
4. **Troubleshooting**: Verify that the serial connection is working correctly

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Dependencies

- `flask>=2.3.0`: Web framework for the API server
- `flask-cors>=4.0.0`: CORS support for API
- `flask-socketio>=5.3.0`: WebSocket support for real-time updates
- `python-socketio>=5.9.0`: Socket.IO Python implementation

All other dependencies are already part of the main application.

## Architecture

### Web Interface Architecture

```
┌─────────────────────────────────────────┐
│  Browser (Vue.js Frontend)              │
│  - Real-time dashboard                  │
│  - WebSocket client                     │
└─────────────┬───────────────────────────┘
              │
              │ HTTP/WebSocket
              │
┌─────────────▼───────────────────────────┐
│  Flask Web API (web_api.py)             │
│  - REST API endpoints                   │
│  - WebSocket server (Socket.IO)         │
│  - State monitor thread                 │
└─────────────┬───────────────────────────┘
              │
              │ Shared memory reference
              │
┌─────────────▼───────────────────────────┐
│  samsung_mqtt_home_assistant.py         │
│  - NASA protocol handler                │
│  - MQTT client                          │
│  - nasa_state dictionary                │
└─────────────────────────────────────────┘
```

### Serial Monitor Architecture

```
┌─────────────────────────────────────────┐
│  serial_monitor.py                      │
│  - Console output                       │
│  - Packet counter                       │
└─────────────┬───────────────────────────┘
              │
              │ Read-only mode
              │
┌─────────────▼───────────────────────────┐
│  PacketGateway (packetgateway.py)       │
│  - TCP socket connection                │
│  - RX event handler                     │
└─────────────┬───────────────────────────┘
              │
              │ TCP/IP
              │
┌─────────────▼───────────────────────────┐
│  Serial Device / socat / Ethernet       │
│  - F3/F4 USB adapter                    │
│  - Ethernet-to-RS485 converter          │
└─────────────────────────────────────────┘
```

## Troubleshooting

### Web Interface Issues

**Web interface not accessible:**
- Check that the port is not blocked by firewall
- Verify the web server is running: check console output
- Try accessing from localhost first: http://localhost:5000

**No data showing:**
- Ensure samsung_mqtt_home_assistant.py is receiving NASA packets
- Check the browser console for JavaScript errors
- Verify the API endpoint works: `curl http://localhost:5000/api/state`

**WebSocket not connecting:**
- Check browser console for WebSocket errors
- Verify Socket.IO is installed: `pip list | grep socketio`
- The interface will fall back to polling if WebSocket fails

### Serial Monitor Issues

**Connection failed:**
- Verify the host and port are correct
- Check that socat is running (if using USB adapter)
- Test with: `nc -v <host> <port>`

**No packets received:**
- Ensure the NASA device is powered on and communicating
- Verify the serial connection (check wiring)
- Try increasing log level: `--log-level DEBUG`

**Parsing errors:**
- Some non-NASA data may appear on the line
- Use `--no-parse` to see raw data only
- Check packet format matches NASA protocol specification

## Security Considerations

- The web interface is accessible from the network by default (0.0.0.0)
- Consider using a reverse proxy with authentication for production use
- The serial monitor is read-only and safe to use for monitoring
- No authentication is implemented - suitable for local network only

## Future Enhancements

Potential improvements for future versions:

- Authentication and authorization for web interface
- Historical data logging and charts
- Configurable alerts and notifications
- Mobile-responsive improvements
- Dark mode support
- Export data to CSV/JSON
- Custom dashboards and widgets
