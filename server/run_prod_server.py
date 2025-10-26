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
port = os.getenv("REACT_SOCKETIO_SERVER_PORT",5000)
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


if __name__ == "__main__":
    
    try:
        run_production_threading()
    except Exception as e:
        print(f"❌ Startup error: {e}")
        if server_process:
            signal_handler(signal.SIGINT, None)
