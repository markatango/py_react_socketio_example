

"""
Diagnostic script to check WebSocket server setup
"""
import sys

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version OK (3.8+)")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_packages():
    """Check all required packages"""
    packages = [
        ('flask', 'Flask'),
        ('flask_socketio', 'Flask-SocketIO'),
        ('flask_cors', 'Flask-CORS'),
        ('socketio', 'python-socketio'),
        ('engineio', 'python-engineio'),
        ('gunicorn', 'Gunicorn'),
    ]
    
    all_ok = True
    print("\n📦 Checking packages:")
    
    for module_name, display_name in packages:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {display_name}: {version}")
        except ImportError:
            print(f"❌ {display_name}: NOT INSTALLED")
            all_ok = False
    
    return all_ok

def test_server_import():
    """Test if server.py can be imported"""
    print("\n🔧 Testing server import:")
    try:
        from server import app, socketio
        print("✅ Server module imports successfully")
        print(f"   SocketIO async_mode: {socketio.async_mode}")
        return True
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False

def check_port():
    """Check if port 5000 is available"""
    print("\n🔌 Checking port 5000:")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("⚠️  Port 5000 is already in use")
            print("   Either a server is running, or another app is using the port")
            return False
        else:
            print("✅ Port 5000 is available")
            return True
    except Exception as e:
        print(f"⚠️  Could not check port: {e}")
        return True

def check_firewall():
    """Check basic network setup"""
    print("\n🔥 Checking network setup:")
    import socket
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"✅ Hostname: {hostname}")
        print(f"✅ IP Address: {ip}")
        print(f"   Server will be accessible at:")
        print(f"   - http://localhost:5000")
        print(f"   - http://127.0.0.1:5000")
        print(f"   - http://{ip}:5000 (from other devices on network)")
        return True
    except Exception as e:
        print(f"⚠️  Network check warning: {e}")
        return True

def print_recommendations():
    """Print setup recommendations"""
    print("\n💡 Recommendations:")
    print("1. Server: Python 3.10.x (most stable)")
    print("2. Client: Node.js 20.x LTS (recommended)")
    print("3. Install packages: pip install -r requirements-minimal.txt")
    print("4. Start server: python3 simple_run.py")
    print("5. Open browser: http://localhost:5000")
    print("\n📝 If client can't connect:")
    print("- Check server is running: netstat -an | grep 5000")
    print("- Check browser console for errors (F12)")
    print("- Try different browser (Chrome recommended)")
    print("- Disable browser extensions that might block WebSocket")
    print("- Check if antivirus/firewall is blocking localhost connections")

if __name__ == "__main__":
    print("=" * 50)
    print("WebSocket Server Diagnostic Tool")
    print("=" * 50)
    
    results = []
    results.append(("Python Version", check_python_version()))
    results.append(("Required Packages", check_packages()))
    results.append(("Server Import", test_server_import()))
    results.append(("Port Availability", check_port()))
    results.append(("Network Setup", check_firewall()))
    
    print("\n" + "=" * 50)
    print("Diagnostic Summary")
    print("=" * 50)
    
    for name, status in results:
        status_str = "✅ PASS" if status else "❌ FAIL"
        print(f"{name:.<30} {status_str}")
    
    all_pass = all(status for _, status in results)
    
    if all_pass:
        print("\n🎉 All checks passed! Your system is ready.")
        print("Run: python3 simple_run.py")
    else:
        print("\n⚠️  Some checks failed. See recommendations below.")
    
    print_recommendations()










