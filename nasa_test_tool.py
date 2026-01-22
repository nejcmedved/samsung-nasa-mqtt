#!/usr/bin/env python3
"""
NASA Protocol Test Tool

A command-line tool for testing Samsung NASA protocol communication over TCP/IP.
This tool allows you to send and receive NASA protocol packets, useful for
debugging and testing your NASA-compatible devices.

Usage:
    python nasa_test_tool.py --host 127.0.0.1 --port 7001
    python nasa_test_tool.py --host 192.168.1.100 --port 8080 --interactive
    python nasa_test_tool.py --host 127.0.0.1 --port 7001 --send-read 0x406f
"""

import argparse
import sys
import time
import logging
import signal
import tools
import packetgateway
from nasa_messages import (
    NasaPacketParser,
    nasa_log_packet,
    nasa_forge,
    nasa_set_attributed_address,
    nasa_set_zone1_temperature,
    nasa_set_zone2_temperature,
    nasa_poke,
    getnonce
)

# Set up logging
LOGFORMAT = '%(asctime)s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(format=LOGFORMAT)
log = logging.getLogger("nasa_test_tool")

class NasaTestTool:
    """NASA Protocol Test Tool for communicating with NASA devices via TCP/IP"""
    
    def __init__(self, host, port, source_address="500000"):
        self.host = host
        self.port = port
        self.source_address = source_address
        self.parser = NasaPacketParser()
        self.gateway = None
        self.running = False
        
        # Set the attributed address for NASA messages
        nasa_set_attributed_address(source_address)
        
    def rx_event_handler(self, p):
        """Handle received NASA packets"""
        log.info("=== Packet Received ===")
        log.info("Raw: " + tools.bin2hex(p))
        try:
            self.parser.parse_nasa(p, self.nasa_packet_handler)
        except Exception as e:
            log.error(f"Failed to parse packet: {e}", exc_info=True)
    
    def nasa_packet_handler(self, **kwargs):
        """Handler for parsed NASA packets"""
        source = kwargs.get("source")
        dest = kwargs.get("dest")
        packetType = kwargs.get("packetType")
        payloadType = kwargs.get("payloadType")
        packetNumber = kwargs.get("packetNumber")
        dataSets = kwargs.get("dataSets")
        
        nasa_log_packet(log, source, dest, packetType, payloadType, packetNumber, dataSets)
        log.info("=" * 40)
    
    def connect(self):
        """Connect to the NASA device"""
        log.info(f"Connecting to {self.host}:{self.port}")
        self.gateway = packetgateway.PacketGateway(
            host=self.host,
            port=self.port,
            rx_event=self.rx_event_handler
        )
        self.gateway.start()
        time.sleep(1)  # Give the gateway time to connect
        log.info("Connected and listening for packets")
        self.running = True
    
    def send_packet(self, packet_data):
        """Send a raw NASA packet (hex string or bytes)"""
        if isinstance(packet_data, str):
            packet_data = tools.hex2bin(packet_data)
        
        log.info("=== Sending Packet ===")
        log.info("Raw: " + tools.bin2hex(packet_data))
        result = self.gateway.packet_tx(packet_data)
        log.info("=" * 40)
        return result
    
    def send_read_request(self, message_number, dest="200000"):
        """Send a read request for a specific message number"""
        log.info(f"Sending read request for message {hex(message_number)}")
        packet = nasa_forge(
            instruction=0x11,  # normal mode, read
            msg_value={message_number: 0x05A5A5A5},  # Dummy value for read request
            dest=dest
        )
        return self.send_packet(packet)
    
    def send_write_request(self, message_number, value, dest="200000"):
        """Send a write request for a specific message number"""
        log.info(f"Sending write request for message {hex(message_number)} with value {value}")
        packet = nasa_forge(
            instruction=0x12,  # normal mode, write
            msg_value={message_number: value},
            dest=dest
        )
        return self.send_packet(packet)
    
    def send_poke(self):
        """Send a PNP poke packet to detect other nodes"""
        log.info("Sending PNP poke packet")
        packet = nasa_poke()
        return self.send_packet(packet)
    
    def send_zone1_temp(self, temperature):
        """Set zone 1 temperature"""
        log.info(f"Setting zone 1 temperature to {temperature}°C")
        packet = nasa_set_zone1_temperature(temperature)
        return self.send_packet(packet)
    
    def send_zone2_temp(self, temperature):
        """Set zone 2 temperature"""
        log.info(f"Setting zone 2 temperature to {temperature}°C")
        packet = nasa_set_zone2_temperature(temperature)
        return self.send_packet(packet)
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("\n" + "=" * 60)
        print("NASA Protocol Test Tool - Interactive Mode")
        print("=" * 60)
        print("\nAvailable commands:")
        print("  read <msg_number>        - Send read request (e.g., read 0x406f)")
        print("  write <msg_number> <val> - Send write request (e.g., write 0x4013 16)")
        print("  raw <hex_data>           - Send raw packet (e.g., raw 500000b0ffffc014a101)")
        print("  zone1 <temp>             - Set zone 1 temperature (e.g., zone1 21.5)")
        print("  zone2 <temp>             - Set zone 2 temperature (e.g., zone2 22.0)")
        print("  poke                     - Send PNP poke packet")
        print("  quit / exit              - Exit the tool")
        print("=" * 60 + "\n")
        
        while self.running:
            try:
                cmd = input("nasa> ").strip()
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0].lower()
                
                if command in ['quit', 'exit']:
                    print("Exiting...")
                    self.running = False
                    break
                
                elif command == 'read' and len(parts) == 2:
                    try:
                        msg_num = int(parts[1], 0)  # Supports hex (0x...) or decimal
                        self.send_read_request(msg_num)
                    except ValueError:
                        print(f"Invalid message number: {parts[1]}")
                
                elif command == 'write' and len(parts) == 3:
                    try:
                        msg_num = int(parts[1], 0)
                        value = int(parts[2], 0)
                        self.send_write_request(msg_num, value)
                    except ValueError:
                        print(f"Invalid message number or value")
                
                elif command == 'raw' and len(parts) == 2:
                    try:
                        self.send_packet(parts[1])
                    except Exception as e:
                        print(f"Error sending raw packet: {e}")
                
                elif command == 'zone1' and len(parts) == 2:
                    try:
                        temp = float(parts[1])
                        self.send_zone1_temp(temp)
                    except ValueError:
                        print(f"Invalid temperature: {parts[1]}")
                
                elif command == 'zone2' and len(parts) == 2:
                    try:
                        temp = float(parts[1])
                        self.send_zone2_temp(temp)
                    except ValueError:
                        print(f"Invalid temperature: {parts[1]}")
                
                elif command == 'poke':
                    self.send_poke()
                
                else:
                    print(f"Unknown command or invalid arguments: {cmd}")
                    print("Type a command from the list above.")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                self.running = False
                break
            except EOFError:
                print("\nExiting...")
                self.running = False
                break
            except Exception as e:
                log.error(f"Error in interactive mode: {e}", exc_info=True)
    
    def listen_mode(self, duration=None):
        """Just listen for packets"""
        log.info("Listening for packets...")
        if duration:
            log.info(f"Will listen for {duration} seconds")
            time.sleep(duration)
        else:
            log.info("Press Ctrl+C to stop")
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                log.info("Stopped by user")
    
    def stop(self):
        """Stop the test tool"""
        self.running = False
        log.info("Test tool stopped")


def main():
    parser = argparse.ArgumentParser(
        description='NASA Protocol Test Tool - Test and debug NASA protocol communication',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Listen to packets from a local socat bridge
  %(prog)s --host 127.0.0.1 --port 7001
  
  # Connect to an Ethernet-to-RS485 converter
  %(prog)s --host 192.168.1.100 --port 8080
  
  # Interactive mode for sending commands
  %(prog)s --host 127.0.0.1 --port 7001 --interactive
  
  # Send a read request for a specific message
  %(prog)s --host 127.0.0.1 --port 7001 --send-read 0x406f
  
  # Set zone 1 temperature
  %(prog)s --host 127.0.0.1 --port 7001 --zone1-temp 21.5
  
  # Send raw hex packet
  %(prog)s --host 127.0.0.1 --port 7001 --send-raw 500000b0ffffc014a101
        """
    )
    
    # Connection parameters
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host/IP address to connect to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=7001,
                        help='TCP port to connect to (default: 7001)')
    parser.add_argument('--source', type=str, default='500000',
                        help='Source address for NASA packets (default: 500000)')
    
    # Operation modes
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode')
    parser.add_argument('--listen', type=int, metavar='SECONDS',
                        help='Listen for packets for specified seconds (0 = forever)')
    
    # Single command operations
    parser.add_argument('--send-read', type=str, metavar='MSG_NUM',
                        help='Send a read request for message number (hex or decimal)')
    parser.add_argument('--send-write', nargs=2, metavar=('MSG_NUM', 'VALUE'),
                        help='Send a write request for message number with value')
    parser.add_argument('--send-raw', type=str, metavar='HEX_DATA',
                        help='Send a raw packet (hex string)')
    parser.add_argument('--zone1-temp', type=float, metavar='TEMP',
                        help='Set zone 1 temperature')
    parser.add_argument('--zone2-temp', type=float, metavar='TEMP',
                        help='Set zone 2 temperature')
    parser.add_argument('--send-poke', action='store_true',
                        help='Send a PNP poke packet')
    
    # Logging
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Set up logging level
    log.setLevel(args.log_level)
    
    # Create test tool
    tool = NasaTestTool(args.host, args.port, args.source)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        log.info("\nShutting down...")
        tool.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Connect to the device
    tool.connect()
    
    # Execute based on arguments
    try:
        # Track if any command was executed
        command_executed = False
        
        if args.send_read:
            msg_num = int(args.send_read, 0)
            tool.send_read_request(msg_num)
            command_executed = True
        
        if args.send_write:
            msg_num = int(args.send_write[0], 0)
            value = int(args.send_write[1], 0)
            tool.send_write_request(msg_num, value)
            command_executed = True
        
        if args.send_raw:
            tool.send_packet(args.send_raw)
            command_executed = True
        
        if args.zone1_temp is not None:
            tool.send_zone1_temp(args.zone1_temp)
            command_executed = True
        
        if args.zone2_temp is not None:
            tool.send_zone2_temp(args.zone2_temp)
            command_executed = True
        
        if args.send_poke:
            tool.send_poke()
            command_executed = True
        
        # Interactive mode
        if args.interactive:
            tool.interactive_mode()
        
        # Listen mode
        elif args.listen is not None:
            duration = args.listen if args.listen > 0 else None
            tool.listen_mode(duration)
        
        # If commands were executed, listen briefly for responses then exit
        elif command_executed:
            log.info("Listening for responses for 3 seconds...")
            tool.listen_mode(3)
        
        # If no specific command was given, just listen for a bit
        else:
            log.info("No specific command given. Listening for 10 seconds...")
            log.info("Use --interactive for interactive mode or --help for more options")
            tool.listen_mode(10)
    
    except Exception as e:
        log.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        tool.stop()


if __name__ == '__main__':
    main()
