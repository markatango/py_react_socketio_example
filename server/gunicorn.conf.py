# Gunicorn configuration file for Python 3.8.10 compatibility
bind = "0.0.0.0:5000"
workers = 1
worker_class = "eventlet"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True  # Changed to True to prevent recursion

# Disable detailed logging to prevent recursion issues
loglevel = "warning"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s'

# Fix for eventlet compatibility issues
import eventlet
eventlet.monkey_patch()