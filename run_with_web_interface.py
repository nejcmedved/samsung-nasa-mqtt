#!/usr/bin/env python3
"""
Samsung NASA MQTT with Web Interface

This script runs the samsung_mqtt_home_assistant.py with an integrated web interface
for monitoring NASA state in real-time.

Usage:
    python run_with_web_interface.py [samsung_mqtt_home_assistant.py arguments] --web-port 5000
"""

import sys
import os
import threading
import argparse

# Parse web-specific arguments first
temp_parser = argparse.ArgumentParser(add_help=False)
temp_parser.add_argument('--web-port', type=int, default=5000, help='Port for web interface (default: 5000)')
temp_parser.add_argument('--web-host', default='0.0.0.0', help='Host for web interface (default: 0.0.0.0)')
temp_parser.add_argument('--no-web', action='store_true', help='Disable web interface')

# Parse known args to extract web settings
web_args, remaining_args = temp_parser.parse_known_args()

# Now import and set up the main application
# We need to intercept the argument parsing to inject our web args
original_argv = sys.argv.copy()
sys.argv = [sys.argv[0]] + remaining_args

# Import the main application module - this will parse the remaining args
import samsung_mqtt_home_assistant

# Restore original argv
sys.argv = original_argv

# Import our web API
from web_api import init_api, run_api

def start_web_interface():
    """Start the web interface in a separate thread"""
    # Initialize the API with references to NASA state
    init_api(samsung_mqtt_home_assistant.nasa_state, samsung_mqtt_home_assistant.mqtt_published_vars)
    
    # Run the API server (this blocks)
    print(f"\n{'='*80}")
    print(f"Web Interface starting on http://{web_args.web_host}:{web_args.web_port}")
    print(f"Open this URL in your browser to view the NASA state monitor")
    print(f"{'='*80}\n")
    
    run_api(host=web_args.web_host, port=web_args.web_port)

if __name__ == '__main__':
    if not web_args.no_web:
        # Start web interface in a separate thread
        web_thread = threading.Thread(target=start_web_interface, daemon=True)
        web_thread.start()
        
        # Give the web server a moment to start
        import time
        time.sleep(2)
    
    # The main samsung_mqtt_home_assistant logic is already running from the import
    # We just need to keep this script alive
    try:
        # Keep the main thread alive
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
