# Quick Start Guide

This guide will help you quickly get started with the new web interface and serial monitor tools.

## Web Interface - Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test the Web Interface with Mock Data

```bash
# Run the test server (doesn't require NASA hardware)
python3 test_web_interface.py
```

Then open your browser to: **http://localhost:5000**

You'll see:
- Real-time dashboard with NASA values
- Values updating every 3 seconds (mock data)
- Interactive filtering and sorting

### 3. Run with Real NASA Hardware

```bash
# Run the full application with web interface
python3 run_with_web_interface.py \
  --mqtt-host localhost \
  --mqtt-port 1883 \
  --serial-host 127.0.0.1 \
  --serial-port 7001 \
  --web-port 5000
```

Access the interface at: **http://localhost:5000**

### 4. Try the Features

- **Filter values**: Type "temp" in the filter box to show only temperature values
- **Sort values**: Click "Sort by Key" or "Sort by Value"
- **Auto-refresh**: Values update automatically every 2 seconds
- **Visual feedback**: Cards flash yellow when values change

## Serial Monitor - Quick Start

### 1. Basic Monitoring

```bash
# Monitor the serial line with packet parsing
python3 serial_monitor.py --host 127.0.0.1 --port 7001
```

### 2. Raw Data Only

```bash
# Show only raw hex data
python3 serial_monitor.py --host 127.0.0.1 --port 7001 --no-parse
```

### 3. Remote Connection

```bash
# Connect to Ethernet-to-RS485 converter
python3 serial_monitor.py --host 192.168.1.100 --port 8080
```

### 4. Debug Mode

```bash
# Enable detailed logging
python3 serial_monitor.py --host 127.0.0.1 --port 7001 --log-level DEBUG
```

## Common Use Cases

### Monitor NASA Values Locally

Perfect for checking your heat pump status without Home Assistant:

```bash
# Run with web interface
python3 run_with_web_interface.py --mqtt-host localhost --web-port 5000

# Open http://localhost:5000 in your browser
# Filter for "TEMP" to see all temperature values
```

### Debug Communication Issues

Use the serial monitor to see raw communication:

```bash
# Monitor all traffic
python3 serial_monitor.py --host 127.0.0.1 --port 7001

# You'll see:
# - Timestamp for each packet
# - Raw hex data
# - Parsed NASA protocol information
# - Total packet count
```

### Test Before Deploying Changes

Test with mock data before touching real hardware:

```bash
# Run the test server
python3 test_web_interface.py

# Open http://localhost:5000
# Verify the interface looks good
# Mock data updates automatically
```

## Architecture Overview

### Web Interface Components

```
Browser <--> Flask Web API <--> NASA State (shared memory)
                                       ^
                                       |
                         samsung_mqtt_home_assistant.py
```

1. **Flask Web API** (`web_api.py`): REST endpoints + auto-refresh
2. **Web Frontend** (`web_interface/dist/index.html`): Vanilla JavaScript UI
3. **Integration Script** (`run_with_web_interface.py`): Runs both together

### Serial Monitor Components

```
Serial Monitor <--> PacketGateway <--> Serial Device
     (Display)         (TCP/IP)          (RS485)
```

1. **Serial Monitor** (`serial_monitor.py`): Read-only display tool
2. **PacketGateway**: Existing TCP connection handler
3. **NASA Parser**: Existing packet parsing logic

## Configuration Tips

### Change Web Interface Port

```bash
# Use port 8080 instead
python3 run_with_web_interface.py --web-port 8080
```

### Make Web Interface Accessible from Network

By default, the interface is accessible from the local network (0.0.0.0).
To restrict to localhost only:

```bash
python3 run_with_web_interface.py --web-host 127.0.0.1
```

### Adjust Auto-Refresh Rate

Edit `web_interface/dist/index.html` and change:

```javascript
// Change this line (default is 2000ms = 2 seconds)
setInterval(() => this.refresh(), 2000);

// To update every 5 seconds:
setInterval(() => this.refresh(), 5000);
```

## Troubleshooting

### Web Interface Not Loading

1. Check the server is running: `ps aux | grep python`
2. Check the port is not in use: `netstat -an | grep 5000`
3. Try accessing localhost: `http://127.0.0.1:5000`
4. Check browser console for errors (F12)

### Serial Monitor No Data

1. Verify socat is running: `ps aux | grep socat`
2. Check serial device: `ls -la /dev/ttyUSB*`
3. Test connection: `nc -v 127.0.0.1 7001`
4. Enable debug logging: `--log-level DEBUG`

### Values Not Updating

1. Check NASA hardware is connected and powered
2. Verify MQTT broker is running
3. Check serial connection settings (baud rate, parity)
4. Look for errors in the console output

## Next Steps

- Read the full documentation: [WEB_INTERFACE_README.md](WEB_INTERFACE_README.md)
- Learn about NASA test tool: [NASA_TEST_TOOL.md](NASA_TEST_TOOL.md)
- Main project README: [readme.md](readme.md)

## Screenshots

**Web Interface - Full View:**
![Web Interface](https://github.com/user-attachments/assets/7d68ed95-cffb-4f4b-8285-fdc33d28b39c)

**Web Interface - Filtered View:**
![Filtered View](https://github.com/user-attachments/assets/9445fa48-cda1-4761-86e3-e56c456a839d)
