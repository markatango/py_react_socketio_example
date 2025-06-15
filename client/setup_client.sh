#!/bin/bash
# Setup script for React client - Node 22.16.0 compatible

echo "Setting up WebSocket React Client..."

# Check Node.js version
NODE_VERSION=$(node --version)
echo "Node.js version: $NODE_VERSION"

# Extract major version number
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')

if [ "$NODE_MAJOR" -ge "18" ]; then
    echo "✓ Node.js version is compatible"
else
    echo "✗ Node.js 18+ required for React 18"
    exit 1
fi

# Check if we're in a React app directory
if [ ! -f "package.json" ]; then
    echo "Creating new React app..."
    npx create-react-app websocket-client
    cd websocket-client
else
    echo "Using existing React app directory"
fi

# Install dependencies
echo "Installing dependencies..."
npm install socket.io-client@^4.7.5

# Create src directory if it doesn't exist
mkdir -p src

# Instructions for manual file setup
echo ""
echo "Setup complete! Next steps:"
echo "1. Replace src/App.js with the provided JavaScript component"
echo "2. Replace src/App.css with the provided CSS file"
echo "3. Run 'npm start' to start the development server"
echo ""
echo "The client will be available at: http://localhost:3000"
echo "Make sure the Python server is running on: http://localhost:5000"