#!/bin/bash
# Fix eventlet compatibility issues for Python 3.8.10

echo "Fixing eventlet compatibility for Python 3.8.10..."

# Uninstall problematic versions
pip uninstall -y eventlet gunicorn

# Install compatible versions
pip install eventlet==0.30.2
pip install gunicorn==20.1.0

# Verify installation
echo "Installed versions:"
python3 -c "import eventlet; print(f'eventlet: {eventlet.__version__}')"
python3 -c "import gunicorn; print(f'gunicorn: {gunicorn.__version__}')"

echo "✓ Eventlet compatibility fix applied"
echo "You can now run the production server"
