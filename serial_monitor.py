#!/usr/bin/env python3
"""
Serial Line Monitor Tool

A read-only serial line monitoring tool for NASA protocol communication with
detailed packet structure analysis.

This tool displays all NASA packet fields according to the protocol specification:
- Packet start/end markers (0x32/0x34)
- Source/Destination addressing (Address Class, Channel, Address)
- Packet information (Protocol Version, Retry Count)
- Packet Type (StandBy, Normal, Gathering, Install, Download)
- Data Type (Read, Write, Request, Notification, Response, Ack, Nack)
- Message payload with type classification (1-byte, 2-byte, 4-byte, structure)

Usage:
    python serial_monitor.py --host 127.0.0.1 --port 7001
    python serial_monitor.py --host 192.168.1.100 --port 8080
    python serial_monitor.py --host 127.0.0.1 --port 7001 --no-parse
    python serial_monitor.py --host 127.0.0.1 --port 7001 --log-level DEBUG
"""

import argparse
import sys
import time
import logging
import signal
import tools
import packetgateway
from nasa_messages import NasaPacketParser

# Set up logging
LOGFORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=LOGFORMAT)
log = logging.getLogger("serial_monitor")

class SerialMonitor:
    """Simple read-only serial line monitor"""
    
    def __init__(self, host, port, parse_packets=True, show_raw=True):
        self.host = host
        self.port = port
        self.parse_packets = parse_packets
        self.show_raw = show_raw
        self.parser = NasaPacketParser() if parse_packets else None
        self.gateway = None
        self.running = False
        self.packet_count = 0
        
    def rx_event_handler(self, packet):
        """Handle received data from serial line"""
        self.packet_count += 1
        
        # Always show timestamp and packet count
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*80}")
        print(f"[{timestamp}] Packet #{self.packet_count}")
        print(f"{'='*80}")
        
        # Show raw data if requested
        if self.show_raw:
            hex_data = tools.bin2hex(packet)
            print(f"RAW: {hex_data}")
            
            # Format as hex dump
            bytes_data = bytes(packet)
            print("\nHEX DUMP:")
            for i in range(0, len(bytes_data), 16):
                chunk = bytes_data[i:i+16]
                hex_part = ' '.join(f'{b:02x}' for b in chunk)
                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                print(f"  {i:04x}:  {hex_part:<48}  {ascii_part}")
        
        # Try to parse as NASA packet if requested
        if self.parse_packets:
            try:
                print("\nPARSED NASA PACKET:")
                self.parser.parse_nasa(packet, self.nasa_packet_handler)
            except Exception as e:
                print(f"  (Could not parse as NASA packet: {e})")
        
        print(f"{'='*80}\n")
        sys.stdout.flush()
    
    def nasa_packet_handler(self, **kwargs):
        """Handler for parsed NASA packets"""
        source = kwargs.get("source")
        dest = kwargs.get("dest")
        packetType = kwargs.get("packetType")
        payloadType = kwargs.get("payloadType")
        packetNumber = kwargs.get("packetNumber")
        dataSets = kwargs.get("dataSets")
        isInfo = kwargs.get("isInfo")
        protocolVersion = kwargs.get("protocolVersion")
        retryCounter = kwargs.get("retryCounter")
        packet = kwargs.get("packet")
        
        # Address Class mapping based on NASA protocol specification
        address_class_map = {
            0x10: "Outdoor",
            0x11: "HTU", 
            0x20: "Indoor",
            0x30: "ERV",
            0x35: "Diffuser",
            0x38: "MCU",
            0x40: "RMC",
            0x50: "WiredRemote",
            0x51: "WiredRemote",  # Alternative wired remote address
            0x58: "PIM",
            0x59: "SIM",
            0x5A: "Peak",
            0x5B: "PowerDivider",
            0xB0: "EHS",
        }
        
        # Parse source and destination addresses
        if len(source) >= 3:
            src_class = source[0]
            src_channel = source[1]
            src_address = source[2]
            src_class_name = address_class_map.get(src_class, f"Unknown(0x{src_class:02x})")
            print(f"  Source: {tools.bin2hex(source)}")
            print(f"    - Address Class: {src_class_name} (0x{src_class:02x})")
            print(f"    - Channel: 0x{src_channel:02x}")
            print(f"    - Address: 0x{src_address:02x}")
        
        if len(dest) >= 3:
            dst_class = dest[0]
            dst_channel = dest[1]
            dst_address = dest[2]
            dst_class_name = address_class_map.get(dst_class, f"Unknown(0x{dst_class:02x})")
            print(f"  Destination: {tools.bin2hex(dest)}")
            print(f"    - Address Class: {dst_class_name} (0x{dst_class:02x})")
            print(f"    - Channel: 0x{dst_channel:02x}")
            print(f"    - Address: 0x{dst_address:02x}")
        
        # Display packet information
        print(f"  Packet Information:")
        print(f"    - Packet Info Flag: {isInfo}")
        print(f"    - Protocol Version: {protocolVersion}")
        print(f"    - Retry Count: {retryCounter}")
        
        # Display packet type and data type with their numeric values
        packet_type_map = {
            0: "StandBy",
            1: "Normal",
            2: "Gathering", 
            3: "Install",
            4: "Download"
        }
        
        data_type_map = {
            0: "Undefined",
            1: "Read",
            2: "Write",
            3: "Request",
            4: "Notification",
            5: "Response",
            6: "Ack",
            7: "Nack"
        }
        
        print(f"  Packet Type: {packetType}")
        print(f"  Data Type: {payloadType}")
        print(f"  Packet Number: {packetNumber}")
        
        # Display message count (capacity) - field at index 9 in NASA packet structure
        if dataSets and packet and len(packet) > 9:
            capacity = packet[9]  # Capacity field per NASA protocol spec
            print(f"  Capacity (Number of Messages): {capacity}")
        
        if dataSets:
            print(f"  Messages ({len(dataSets)}):")
            for i, ds in enumerate(dataSets):
                msgnum = ds[0]
                msgname = ds[1]
                msgvalue = ds[2]
                
                # Determine message type from message number (bits 9-10)
                msg_type = (msgnum & 0x600) >> 9
                # msg_type is always 0-3 per NASA protocol: 0=1byte, 1=2bytes, 2=4bytes, 3=structure
                msg_type_desc = ["1 byte", "2 bytes", "4 bytes", "structure"][msg_type]
                
                # Display with type information
                print(f"    [{i+1}] Message Number: 0x{msgnum:04x}")
                print(f"        Name: {msgname}")
                print(f"        Type: {msg_type_desc} payload")
                print(f"        Value: {msgvalue}")
    
    def connect(self):
        """Connect to the serial line"""
        log.info(f"Connecting to {self.host}:{self.port}")
        print(f"\n{'='*80}")
        print(f"Serial Line Monitor - Connected to {self.host}:{self.port}")
        print(f"{'='*80}")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            self.gateway = packetgateway.PacketGateway(
                host=self.host,
                port=self.port,
                rx_event=self.rx_event_handler,
                rxonly=True  # Read-only mode
            )
            self.gateway.start()
            self.running = True
            log.info("Connected and monitoring serial line")
        except Exception as e:
            log.error(f"Failed to connect: {e}")
            raise
    
    def run(self):
        """Run the monitor (blocking)"""
        try:
            self.connect()
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
            log.info("Monitoring stopped by user")
        except Exception as e:
            log.error(f"Error: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop the monitor"""
        self.running = False
        if self.gateway:
            self.gateway.stop()
        log.info(f"Total packets received: {self.packet_count}")
        print(f"\nTotal packets received: {self.packet_count}")

def main():
    parser = argparse.ArgumentParser(
        description='Serial Line Monitor - Read-only NASA protocol monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --host 127.0.0.1 --port 7001
  %(prog)s --host 192.168.1.100 --port 8080 --no-parse
  %(prog)s --host 127.0.0.1 --port 7001 --raw-only
        '''
    )
    
    parser.add_argument('--host', default='127.0.0.1',
                        help='Host/IP address to connect to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=7001,
                        help='TCP port to connect to (default: 7001)')
    parser.add_argument('--no-parse', action='store_true',
                        help='Disable NASA packet parsing, show raw data only')
    parser.add_argument('--raw-only', action='store_true',
                        help='Show only raw hex data without hex dump')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Set log level
    log.setLevel(getattr(logging, args.log_level))
    
    # Create and run monitor
    monitor = SerialMonitor(
        host=args.host,
        port=args.port,
        parse_packets=not args.no_parse,
        show_raw=not args.raw_only
    )
    
    monitor.run()

if __name__ == '__main__':
    main()
