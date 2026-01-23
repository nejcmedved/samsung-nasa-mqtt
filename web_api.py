#!/usr/bin/env python3
"""
NASA MQTT Web API
Provides a REST API and WebSocket interface for monitoring NASA state in real-time
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import threading
import time
import json
import os

# Configuration constants
UPDATE_INTERVAL = 1  # seconds between state updates
ERROR_RETRY_INTERVAL = 5  # seconds to wait after error

app = Flask(__name__, static_folder='web_interface/dist', static_url_path='')
# Note: CORS is set to allow all origins for ease of local development
# In production, replace '*' with specific allowed origins
CORS(app)
# Note: cors_allowed_origins="*" is used for local development
# In production, specify allowed origins explicitly
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state that will be shared with samsung_mqtt_home_assistant.py
nasa_state_ref = None
mqtt_published_vars_ref = None

def init_api(nasa_state, mqtt_published_vars):
    """Initialize the API with references to NASA state"""
    global nasa_state_ref, mqtt_published_vars_ref
    nasa_state_ref = nasa_state
    mqtt_published_vars_ref = mqtt_published_vars

@app.route('/')
def index():
    """Serve the Vue.js application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/state')
def get_state():
    """Get current NASA state"""
    if nasa_state_ref is None:
        return jsonify({"error": "NASA state not initialized"}), 503
    
    # Convert state to JSON-serializable format
    state = {}
    for key, value in nasa_state_ref.items():
        if isinstance(value, (int, float, str)):
            state[key] = value
        elif isinstance(value, bytes):
            state[key] = value.hex()
        else:
            state[key] = str(value)
    
    return jsonify(state)

@app.route('/api/mqtt_vars')
def get_mqtt_vars():
    """Get information about published MQTT variables"""
    if mqtt_published_vars_ref is None:
        return jsonify({"error": "MQTT vars not initialized"}), 503
    
    # Get list of published variable names
    vars_list = list(mqtt_published_vars_ref.keys())
    return jsonify(vars_list)

def state_monitor_thread():
    """Monitor state changes and emit via WebSocket"""
    last_state = {}
    while True:
        try:
            if nasa_state_ref is not None:
                current_state = {}
                for key, value in nasa_state_ref.items():
                    if isinstance(value, (int, float, str)):
                        current_state[key] = value
                    elif isinstance(value, bytes):
                        current_state[key] = value.hex()
                    else:
                        current_state[key] = str(value)
                
                # Check for changes
                if current_state != last_state:
                    socketio.emit('state_update', current_state)
                    last_state = current_state.copy()
            
            time.sleep(UPDATE_INTERVAL)
        except Exception as e:
            print(f"Error in state monitor: {e}")
            time.sleep(ERROR_RETRY_INTERVAL)

def run_api(host='0.0.0.0', port=5000):
    """Run the API server
    
    Note: This uses allow_unsafe_werkzeug=True for development convenience.
    For production deployments, use a proper WSGI server like gunicorn or waitress.
    """
    # Start state monitor thread
    monitor = threading.Thread(target=state_monitor_thread, daemon=True)
    monitor.start()
    
    # Run the Flask app with SocketIO
    # Note: allow_unsafe_werkzeug=True is for development only
    # For production, use: gunicorn --worker-class eventlet -w 1 web_api:app
    socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)

