#!/usr/bin/env python3
"""
Test script for web interface with mock data
This demonstrates the web interface without needing a real NASA device
"""

import time
import random
from web_api import init_api, run_api

# Create mock NASA state
nasa_state = {
    "NASA_ZONE1_TEMP": 215,  # 21.5°C
    "NASA_ZONE2_TEMP": 220,  # 22.0°C
    "NASA_OUTDOOR_TEMP": 85,  # 8.5°C
    "NASA_WATER_TEMP": 450,  # 45.0°C
    "NASA_OP_MODE_HEATING": 1,
    "NASA_POWER_STATE": 1,
    "NASA_DHW_ENABLED": 1,
    "master_address": b'\x20\x00\x00',
    "0x406f": 215,
    "0x4076": 220,
    "0x420c": 85,
    "0x4238": 450,
    "0x4000": 1,
    "0x4052": 1,
}

# Mock MQTT published vars
mqtt_published_vars = {
    "NASA_ZONE1_TEMP": [],
    "NASA_ZONE2_TEMP": [],
    "NASA_OUTDOOR_TEMP": [],
    "NASA_WATER_TEMP": [],
}

def update_mock_data():
    """Periodically update mock data to simulate real changes"""
    import threading
    
    def updater():
        while True:
            time.sleep(3)
            # Randomly update some values
            nasa_state["NASA_ZONE1_TEMP"] = 210 + random.randint(0, 20)
            nasa_state["NASA_ZONE2_TEMP"] = 215 + random.randint(0, 20)
            nasa_state["NASA_OUTDOOR_TEMP"] = 80 + random.randint(0, 30)
            nasa_state["NASA_WATER_TEMP"] = 440 + random.randint(0, 30)
            
            # Update hex values too
            nasa_state["0x406f"] = nasa_state["NASA_ZONE1_TEMP"]
            nasa_state["0x4076"] = nasa_state["NASA_ZONE2_TEMP"]
            nasa_state["0x420c"] = nasa_state["NASA_OUTDOOR_TEMP"]
            nasa_state["0x4238"] = nasa_state["NASA_WATER_TEMP"]
    
    thread = threading.Thread(target=updater, daemon=True)
    thread.start()

if __name__ == '__main__':
    print("Starting web interface with mock NASA data...")
    print("Open http://localhost:5000 in your browser")
    print("Mock data will update every 3 seconds")
    
    # Initialize API with mock data
    init_api(nasa_state, mqtt_published_vars)
    
    # Start mock data updater
    update_mock_data()
    
    # Run the API server
    run_api(host='0.0.0.0', port=5000)
