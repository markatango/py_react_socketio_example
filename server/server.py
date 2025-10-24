"""
Flask-SocketIO WebSocket Server - Python 3.8.10 Compatible
Recursion-free implementation with proper shutdown handling
"""
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import random
import logging
import sys
import signal
import os

# Disable excessive logging to prevent recursion
logging.getLogger('socketio').setLevel(logging.WARNING)
logging.getLogger('engineio').setLevel(logging.WARNING)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DEBUG'] = False  # Disable debug mode

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO without eventlet to avoid recursion
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='threading',  # Use threading instead of eventlet
                   logger=False,
                   engineio_logger=False,
                   ping_timeout=60,
                   ping_interval=25)

# Global state
bool_state = True
running = False
clients_connected = 0
port = os.getenv("REACT_SOCKETIO_SERVER_PORT",5000)
def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global running
    print(f'\n🛑 Received signal {sig}, shutting down gracefully...')
    running = False
    print('✅ Server shutdown complete')
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl-C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

def background_thread():
    """Emit random numbers and boolean values twice per second"""
    global bool_state, running
    print("Background thread started - emitting messages twice per second")
    
    count = 0
    while running:
        try:
            # Generate random number
            random_number = random.random()
            
            # Create message
            data = {
                'randomNumber': random_number,
                'boolean': bool_state
            }
            
            # Emit to all clients
            socketio.emit('message', data, namespace='/')
            
            print(f"Emit #{count}: random={random_number:.6f}, boolean={bool_state}")
            
            # Toggle boolean
            bool_state = not bool_state
            count += 1
            
            # Sleep for 500ms (2 times per second)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Background thread error: {e}")
            if running:  # Only sleep and retry if still supposed to be running
                time.sleep(1)
            else:
                break
    
    print("Background thread stopped")

@socketio.on('connect')
def handle_connect():
    global running, clients_connected
    clients_connected += 1
    print(f'Client connected. Total clients: {clients_connected}')
    
    # Start background thread when first client connects
    if not running:
        running = True
        socketio.start_background_task(target=background_thread)
        print("Started background message emission")
    
    # Send welcome message
    emit('message', {
        'randomNumber': random.random(),
        'boolean': bool_state
    })

@socketio.on('disconnect')
def handle_disconnect():
    global clients_connected
    clients_connected -= 1
    print(f'Client disconnected. Total clients: {clients_connected}')

@socketio.on('toggle_button')
def handle_toggle_button(data):
    """Handle button toggle from client"""
    try:
        button_state = data.get('buttonState', False)
        client_id = data.get('clientId', 'Unknown')
        
        print(f"📱 Button toggled by client {client_id}: {button_state}")
        
        # Send acknowledgment
        emit('button_ack', {
            'received': True, 
            'state': button_state,
            'timestamp': time.time()
        })
        
    except Exception as e:
        print(f"Error handling button toggle: {e}")

@socketio.on('datetime_change')
def handle_datetime_change(data):
    """Handle datetime change from client"""
    try:
        datetime_value = data.get('datetimeValue', '')
        client_id = data.get('clientId', 'Unknown')
        input_type = data.get('inputType', 'datetime')
        
        print(f"🕒 User changed {input_type} - Client {client_id}: {datetime_value}")
        
        # Send acknowledgment
        emit('datetime_ack', {
            'received': True, 
            'value': datetime_value, 
            'type': input_type,
            'timestamp': time.time()
        })
        
    except Exception as e:
        print(f"Error handling datetime change: {e}")

@app.route('/')
def index():
    return """
    <h1>WebSocket Server Running</h1>
    <p>Server is running and ready for WebSocket connections.</p>
    <p>Connect your React client to: <code>http://localhost:5000</code></p>
    <p>Server mode: Threading (recursion-free)</p>
    <p>Press Ctrl-C to stop the server</p>
    """

@app.route('/health')
def health():
    return {
        'status': 'running',
        'clients': clients_connected,
        'background_thread': running,
        'async_mode': socketio.async_mode
    }

if __name__ == '__main__':
    print("=" * 50)
    print("WebSocket Server - Recursion-Free Version")
    print("Python version:", sys.version)
    print("Async mode: threading")
    print("Server will be available at: http://localhost:"+str(port))
    print("Press Ctrl-C to stop the server")
    print("=" * 50)
    
    try:
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=port,
                    debug=False,
                    use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user (Ctrl-C)")
        running = False
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        running = False
        print("👋 Server shutdown complete")
        
