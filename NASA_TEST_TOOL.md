# NASA Protocol Test Tool

A command-line tool for testing and debugging Samsung NASA protocol communication over TCP/IP. This tool is useful for:
- Testing communication with NASA-compatible devices
- Debugging protocol issues
- Exploring NASA protocol messages
- Developing and testing new features

## Features

- **TCP/IP Communication**: Connect to devices via direct TCP or through socat bridges
- **Interactive Mode**: Send commands interactively through a console interface
- **Command-Line Operations**: Execute single commands for automation
- **Packet Monitoring**: View all received packets in human-readable format
- **Protocol Support**: Full support for NASA protocol packet types

## Requirements

- Python 3.x
- Dependencies from `requirements.txt`:
  - paho-mqtt<2.0.0
  - ConfigArgParse

## Installation

No special installation required. The tool uses the existing NASA protocol implementation in this repository.

```bash
# Ensure dependencies are installed
pip install -r requirements.txt
```

## Usage

### Basic Usage

Connect and listen for packets:
```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001
```

### Interactive Mode

Launch interactive mode for manual testing:
```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --interactive
```

In interactive mode, you can use these commands:
- `read 0x406f` - Send a read request for message number 0x406f
- `write 0x4013 16` - Write value 16 to message 0x4013
- `raw 500000b0ffffc014a101` - Send raw hex packet
- `zone1 21.5` - Set zone 1 temperature to 21.5°C
- `zone2 22.0` - Set zone 2 temperature to 22.0°C
- `poke` - Send a PNP poke packet to detect nodes
- `quit` or `exit` - Exit the tool

### Command-Line Operations

Send a single read request:
```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --send-read 0x406f
```

Send a write request:
```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --send-write 0x4013 16
```

Set zone temperature:
```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --zone1-temp 21.5
```

Send raw packet:
```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --send-raw 500000b0ffffc014a101
```

Send PNP poke:
```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --send-poke
```

### Listen Mode

Listen for packets for a specific duration:
```bash
# Listen for 30 seconds
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --listen 30

# Listen forever (until Ctrl+C)
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --listen 0
```

## Connection Methods

### Method 1: Via socat Bridge (Local USB-to-RS485)

If you're using a USB-to-RS485 adapter (like the F3/F4 adapter), set up socat first:

```bash
socat /dev/ttyUSB0,raw,echo=0,nonblock,min=0,b9600,parenb tcp-listen:7001,reuseaddr &
python nasa_test_tool.py --host 127.0.0.1 --port 7001
```

### Method 2: Direct TCP (Ethernet-to-RS485 Converter)

If you have an Ethernet-to-RS485 converter:

```bash
python nasa_test_tool.py --host 192.168.1.100 --port 8080
```

## Command-Line Options

```
Connection:
  --host HOST          Host/IP address to connect to (default: 127.0.0.1)
  --port PORT          TCP port to connect to (default: 7001)
  --source SOURCE      Source address for NASA packets (default: 500000)

Operation Modes:
  --interactive, -i    Run in interactive mode
  --listen SECONDS     Listen for packets (0 = forever)

Commands:
  --send-read MSG_NUM           Send read request for message number
  --send-write MSG_NUM VALUE    Send write request
  --send-raw HEX_DATA           Send raw packet (hex string)
  --zone1-temp TEMP             Set zone 1 temperature
  --zone2-temp TEMP             Set zone 2 temperature
  --send-poke                   Send PNP poke packet

Logging:
  --log-level LEVEL    Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
```

## Examples

### Example 1: Test Communication

Check if you can communicate with the device:
```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --send-poke --listen 5
```

### Example 2: Read Indoor Temperature

```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --send-read 0x406f --listen 5
```

### Example 3: Interactive Session

```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --interactive

# Then in the interactive prompt:
nasa> poke
nasa> read 0x406f
nasa> read 0x4076
nasa> zone1 21.5
nasa> quit
```

### Example 4: Debug Mode

Enable debug logging to see detailed packet information:
```bash
python nasa_test_tool.py --host 127.0.0.1 --port 7001 --log-level DEBUG --interactive
```

## NASA Protocol Basics

### Packet Structure

NASA packets consist of:
- **Start Byte**: 0x32
- **Length**: 2 bytes (packet length excluding start/end bytes)
- **Source Address**: 3 bytes
- **Destination Address**: 3 bytes
- **Control Byte**: 1 byte (protocol info)
- **Instruction**: 1 byte (packet type and payload type)
- **Packet Number**: 1 byte (sequence number)
- **Data Count**: 1 byte
- **Data Sets**: Variable length
- **CRC**: 2 bytes
- **End Byte**: 0x34

### Common Message Numbers

Some commonly used message numbers:
- `0x406f` - Indoor temperature (zone 1)
- `0x4076` - Indoor temperature (zone 2)
- `0x423a` - Target temperature zone 1
- `0x42da` - Target temperature zone 2
- `0x4052` - Power state
- `0x4013` - Operation mode

Refer to `nasa_messages.py` for a complete list of message numbers.

### Packet Types

- **Standby** (0x0): Device in standby
- **Normal** (0x1): Normal operation
- **Gathering** (0x2): Information gathering
- **Install** (0x3): Installation mode
- **Download** (0x4): Download mode

### Payload Types

- **Read** (0x1): Read request
- **Write** (0x2): Write request
- **Request** (0x3): General request
- **Notification** (0x4): Notification message
- **Response** (0x5): Response to request
- **ACK** (0x6): Acknowledgment
- **NACK** (0x7): Negative acknowledgment

## Troubleshooting

### Connection Issues

If you can't connect:
1. Check that the host and port are correct
2. Ensure your USB-to-RS485 adapter is connected (if using socat)
3. Verify socat is running: `ps aux | grep socat`
4. Check serial port: `ls -la /dev/ttyUSB*`

### No Packets Received

If you're not receiving packets:
1. Use `--log-level DEBUG` to see detailed information
2. Try sending a poke packet: `--send-poke`
3. Verify the device is powered on and connected
4. Check RS485 wiring polarity

### Packet Parsing Errors

If packets fail to parse:
1. Use `--send-raw` to send known good packets
2. Compare with sample packets in `samples/` directory
3. Check CRC calculation
4. Verify packet format matches NASA protocol specification

## See Also

- Main application: `samsung_mqtt_home_assistant.py`
- Protocol implementation: `nasa_messages.py`
- Packet gateway: `packetgateway.py`
- Sample scripts: `samples/` directory
- NASA Protocol Wiki: https://wiki.myehs.eu/wiki/NASA_Protocol
