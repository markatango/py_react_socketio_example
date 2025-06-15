from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
import random
import logging

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with eventlet for Python 3.8 compatibility
socketio = SocketIO(app, 
                   cors_allowed_origins="*", 
                   async_mode='eventlet',
                   logger=True, 
                   engineio_logger=True)

# Global state for alternating boolean
bool_state = True
running = False
message_thread = None
thread_lock = threading.Lock()

def emit_messages():
    """Background task that emits messages twice per second"""
    global bool_state, running
    print("Starting message emission thread...")
    
    while running:
        try:
            # Generate random number between 0 and 1
            random_number = random.random()
            
            # Create message data
            data = {
                'randomNumber': random_number,
                'boolean': bool_state
            }
            
            # Emit to all connected clients
            socketio.emit('message', data)
            
            print(f"Emitted: random={random_number:.6f}, boolean={bool_state}")
            
            # Toggle boolean for next message
            bool_state = not bool_state
            
            # Wait 500ms (twice per second)
            socketio.sleep(0.5)  # Use socketio.sleep for eventlet compatibility
            
        except Exception as e:
            print(f"Error in emit_messages: {e}")
            break
    
    print("Message emission thread stopped.")

@socketio.on('connect')
def handle_connect():
    global running, message_thread
    print(f'Client connected: {request.sid if "request" in globals() else "unknown"}')
    
    # Start the message emission thread if not already running
    with thread_lock:
        if not running:
            running = True
            message_thread = socketio.start_background_task(target=emit_messages)
            print("Started background message emission task")

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid if "request" in globals() else "unknown"}')

@socketio.on('toggle_button')
def handle_toggle_button(data):
    """Handle toggle button click from client"""
    button_state = data.get('buttonState', False)
    client_id = data.get('clientId', 'Unknown')
    
    print(f"📱 Button toggled by client {client_id}: {button_state}")
    
    # Optionally send acknowledgment back to client
    emit('button_ack', {'received': True, 'state': button_state})

@socketio.on('datetime_change')
def handle_datetime_change(data):
    """Handle datetime input change from client"""
    datetime_value = data.get('datetimeValue', '')
    client_id = data.get('clientId', 'Unknown')
    input_type = data.get('inputType', 'datetime')
    
    print(f"🕒 User changed {input_type} - Client {client_id}: {datetime_value}")
    
    # Send acknowledgment back to client
    emit('datetime_ack', {'received': True, 'value': datetime_value, 'type': input_type})

@app.route('/')
def index():
    return "WebSocket server is running. Connect your React client to receive messages."

if __name__ == '__main__':
    # Import request for session ID tracking
    try:
        from flask import request
        globals()['request'] = request
    except ImportError:
        pass
    
    print("Starting Flask-SocketIO server...")
    print("Server will be available at: http://localhost:5000")
    print("Python version compatibility: 3.8+")
    
    # For development - use eventlet for Python 3.8 compatibility
    socketio.run(app, 
                debug=True, 
                host='0.0.0.0', 
                port=5000,
                use_reloader=False)  # Disable reloader to prevent threading issues