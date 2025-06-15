#!/usr/bin/env python3
"""
Startup script for WebSocket server - Python 3.8.10 compatible
"""
import sys
import os

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

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    os.system("pip install -r requirements.txt")

def run_development_server():
    """Run the development server"""
    print("Starting development server...")
    from server import app, socketio
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)

def run_production_server():
    """Run with Gunicorn for production"""
    print("Starting production server with Gunicorn...")
    os.system("gunicorn -c gunicorn.conf.py server:app")

if __name__ == "__main__":
    if not check_python_version():
        sys.exit(1)
    
    mode = input("Run in (d)evelopment or (p)roduction mode? [d/p]: ").lower()
    
    if mode.startswith('p'):
        run_production_server()
    else:
        run_development_server()