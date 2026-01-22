#!/bin/bash
# Run script for direct TCP connection to Ethernet-to-RS485 converter
# No socat needed - connects directly to the converter

cd $(dirname $(readlink -f $0))

# Configuration - modify these values for your setup
TCP_HOST="${TCP_HOST:-192.168.1.100}"  # IP address of your Ethernet-to-RS485 converter
TCP_PORT="${TCP_PORT:-8080}"            # TCP port of your converter

echo "Connecting to Ethernet-to-RS485 converter at: $TCP_HOST:$TCP_PORT"
echo "Set TCP_HOST and TCP_PORT environment variables to override defaults"
echo "Example: TCP_HOST=192.168.1.50 TCP_PORT=9000 ./run_tcp.sh"
echo ""
echo "Additional run arguments: $ARGS $*"

python3 samsung_mqtt_home_assistant.py --serial-host "$TCP_HOST" --serial-port "$TCP_PORT" $ARGS $*
