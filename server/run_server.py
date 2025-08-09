#!/usr/bin/env python3
"""
Startup script for WebSocket server - Threading-only version with proper shutdown
"""
import sys
import os
import signal
import subprocess
import time

# Global variable to track server process
server_process = None

def signal_handler(sig, frame):
    """Handle Ctrl-C signal and terminate server gracefully"""
    global server_process
    print('\n🛑 Received interrupt signal (Ctrl-C)')
    
    if server_process:
        print('📡 Terminating server process...')
        try:
            # First try SIGINT (Ctrl-C equivalent)
            server_process.send_signal(signal.SIGINT)
            
            # Wait for graceful shutdown (shorter timeout)
            print('⏳ Waiting for graceful shutdown (5 seconds)...')
            try:
                server_process.wait(timeout=5)
                print('✅ Server terminated gracefully')
                return
            except subprocess.TimeoutExpired:
                print('⚠️  SIGINT timeout, trying SIGTERM...')
            
            # Try SIGTERM
            server_process.terminate()
            try:
                server_process.wait(timeout=3)
                print('✅ Server terminated with SIGTERM')
                return
            except subprocess.TimeoutExpired:
                print('⚠️  SIGTERM timeout, forcing termination...')
            
            # Force kill as last resort
            server_process.kill()
            server_process.wait()
            print('🔨 Server force-terminated')
            
        except Exception as e:
            print(f'❌ Error terminating server: {e}')
            # Try to kill the process group as backup
            try:
                if hasattr(server_process, 'pid'):
                    os.kill(server_process.pid, signal.SIGKILL)
                    print('🔨 Process killed directly')
            except:
                pass
    
    print('👋 Goodbye!')
    sys.exit(0)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.8+ required")
        return False

def run_development_server():
    """Run the development server directly"""
    global server_process
    print("Starting development server (threading mode)...")
    print("Press Ctrl-C to stop the server")
    
    try:
        # Import and run directly with proper signal handling
        from server import app, socketio
        
        # Register signal handler for development mode
        signal.signal(signal.SIGINT, signal_handler)
        
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=5000, 
                    debug=True, 
                    use_reloader=False,
                    allow_unsafe_werkzeug=True)
                    
    except KeyboardInterrupt:
        print("\n🛑 Development server stopped by user")
    except Exception as e:
        print(f"❌ Development server error: {e}")

def run_production_threading():
    """Run production server with threading worker and proper shutdown"""
    global server_process
    print("Starting production server (threading worker)...")
    print("Press Ctrl-C to stop the server")
    
    cmd = [
        "gunicorn", 
        "-c", "gunicorn.conf.py",
        "server:app"
    ]
    
    try:
        # Start server process without process group (simpler approach)
        server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print(f"🚀 Gunicorn server started with PID: {server_process.pid}")
        
        # Register signal handler
        signal.signal(signal.SIGINT, signal_handler)
        
        # Read server output with timeout to allow signal handling
        print("📡 Server starting... (waiting for ready message)")
        
        # Start a thread to read output so we can handle signals
        import threading
        
        def read_output():
            try:
                for line in server_process.stdout:
                    print(f"[SERVER] {line.strip()}")
            except:
                pass
        
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        
        # Wait for process with periodic checks to allow signal handling
        while server_process.poll() is None:
            time.sleep(0.5)  # Check every 500ms
        
        print("🛑 Server process ended")
        
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        print(f"❌ Production server error: {e}")
        if server_process:
            signal_handler(signal.SIGINT, None)

def run_direct_server():
    """Run server directly (no gunicorn) with proper shutdown"""
    print("Starting server directly (no gunicorn)...")
    print("Press Ctrl-C to stop the server")
    
    try:
        # Register signal handler
        signal.signal(signal.SIGINT, signal_handler)
        
        # Run server directly
        os.system("python3 server.py")
        
    except KeyboardInterrupt:
        print("\n🛑 Direct server stopped by user")

def test_imports():
    """Test if all imports work without recursion"""
    print("Testing imports...")
    try:
        import flask
        print(f"✓ Flask {flask.__version__}")
        
        import flask_socketio
        # Try to get version, but don't fail if it doesn't exist
        try:
            version = flask_socketio.__version__
            print(f"✓ Flask-SocketIO {version}")
        except AttributeError:
            print("✓ Flask-SocketIO imported (version not available)")
        
        import flask_cors
        print("✓ Flask-CORS imported")
        
        # Test that SocketIO can be instantiated
        from flask import Flask
        test_app = Flask(__name__)
        test_socketio = flask_socketio.SocketIO(test_app, logger=False, engineio_logger=False)
        print("✓ SocketIO instantiation test passed")
        
        print("✓ All imports successful - no async conflicts")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == "__main__":
    if not check_python_version():
        sys.exit(1)
    
    if not test_imports():
        print("Please fix import issues before continuing")
        sys.exit(1)
    
    print("\nSelect server mode:")
    print("(d) Development mode (Flask dev server)")
    print("(p) Production mode (Gunicorn + threading)")
    print("(s) Direct server (no Gunicorn)")
    print("(i) Test imports only")
    
    mode = input("Enter choice [d/p/s/i]: ").lower()
    
    try:
        if mode.startswith('d'):
            run_development_server()
        elif mode.startswith('p'):
            run_production_threading()
        elif mode.startswith('s'):
            run_direct_server()
        elif mode.startswith('i'):
            print("Import test completed successfully!")
        else:
            print("Invalid choice, starting development server...")
            run_development_server()
    except Exception as e:
        print(f"❌ Startup error: {e}")
        if server_process:
            signal_handler(signal.SIGINT, None)