
// App.js
import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import './App.css';



function App() {
  const [randomNumber, setRandomNumber] = useState(0);
  const [booleanValue, setBooleanValue] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState(null);
  const [buttonState, setButtonState] = useState(false);
  const [clientId] = useState(() => Math.random().toString(36).substr(2, 9));
  const [datetimeValue, setDatetimeValue] = useState('');

  useEffect(() => {
    console.log('Initializing Socket.IO connection...');
    
    // Connect with proper Socket.IO client options for Flask-SocketIO
    // If not reverse proxied:
    // const SERVER_URL = process.env.REACT_APP_SERVER_URL+":"+process.env.REACT_APP_SERVER_PORT || 'http://localhost:5000';

    // If reverse proxied:
    const SERVER_URL = process.env.REACT_APP_SERVER_URL;

    console.log(SERVER_URL)

    const newSocket = io(SERVER_URL, {
      path: "/py_react_socketio_example/socket.io/",
      transports: ['polling', 'websocket'], // Try polling first
      upgrade: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      timeout: 20000
    });

    newSocket.on('connect', () => {
      console.log('✅ Connected to server');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('❌ Disconnected from server');
      setIsConnected(false);
    });

    newSocket.on('message', (data) => {
      console.log('📨 Received message:', data);
      setRandomNumber(data.randomNumber);
      setBooleanValue(data.boolean);
    });

    newSocket.on('connect_error', (error) => {
      console.error('❌ Connection error:', error.message);
      setIsConnected(false);
    });

    newSocket.on('button_ack', (data) => {
      console.log('✅ Button acknowledged:', data);
    });

    newSocket.on('datetime_ack', (data) => {
      console.log('✅ DateTime acknowledged:', data);
    });

    setSocket(newSocket);

    return () => {
      console.log('🔌 Cleaning up socket connection');
      newSocket.close();
    };
  }, []);

  const handleButtonToggle = () => {
    const newButtonState = !buttonState;
    setButtonState(newButtonState);
    
    if (socket && isConnected) {
      socket.emit('toggle_button', {
        buttonState: newButtonState,
        clientId: clientId,
        timestamp: new Date().toISOString()
      });
      console.log(`📤 Button toggled to: ${newButtonState}`);
    }
  };

  const handleDatetimeChange = (event) => {
    const newDatetimeValue = event.target.value;
    setDatetimeValue(newDatetimeValue);
    
    if (socket && isConnected && newDatetimeValue) {
      socket.emit('datetime_change', {
        datetimeValue: newDatetimeValue,
        clientId: clientId,
        inputType: 'datetime-local',
        timestamp: new Date().toISOString()
      });
      console.log(`📤 Datetime changed to: ${newDatetimeValue}`);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <h1 className="title">WebSocket Client</h1>
        
        {/* Connection Status */}
        <div className="connection-status">
          <span className={`status-badge ${isConnected ? 'connected' : 'disconnected'}`}>
            <div className={`status-dot ${isConnected ? 'green' : 'red'}`}></div>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        {/* Random Number Field */}
        <div className="section">
          <label className="label">Random Number</label>
          <div className="input-container">
            <input
              type="text"
              value={randomNumber.toFixed(6)}
              readOnly
              className="number-input"
            />
            <div className="input-indicator">
              <div className="pulse-dot"></div>
            </div>
          </div>
        </div>

        {/* Boolean Indicator */}
        <div className="section indicator-section">
          <label className="label">Status Indicator</label>
          <div className="indicator-container">
            <div className={`status-circle ${booleanValue ? 'active' : 'inactive'} ${booleanValue ? 'pulse' : ''}`}>
              <span className="status-text">
                {booleanValue ? 'ON' : 'OFF'}
              </span>
            </div>
          </div>
          <p className={`status-label ${booleanValue ? 'active-text' : 'inactive-text'}`}>
            {booleanValue ? 'Active' : 'Inactive'}
          </p>
        </div>

        {/* Date and Time Input */}
        <div className="section">
          <label className="label">Date and Time</label>
          <div className="input-container">
            <input
              type="datetime-local"
              value={datetimeValue}
              onChange={handleDatetimeChange}
              disabled={!isConnected}
              className={`datetime-input ${!isConnected ? 'disabled' : ''}`}
            />
          </div>
          {datetimeValue && (
            <p className="datetime-display">
              Selected: {new Date(datetimeValue).toLocaleString()}
            </p>
          )}
        </div>

        {/* Toggle Button */}
        <div className="section button-section">
          <label className="label">Client Control</label>
          <button
            onClick={handleButtonToggle}
            disabled={!isConnected}
            className={`toggle-button ${!isConnected ? 'disabled' : buttonState ? 'active' : 'inactive'}`}
          >
            {buttonState ? 'Turn OFF' : 'Turn ON'}
          </button>
          <p className={`button-state ${buttonState ? 'active-text' : 'inactive-text'}`}>
            Button State: {buttonState ? 'TRUE' : 'FALSE'}
          </p>
        </div>

        {/* Debug Info */}
        <div className="debug-section">
          <h3 className="debug-title">Debug Info</h3>
          <div className="debug-info">
            <div>Connection: {isConnected ? '✓ Connected' : '✗ Disconnected'}</div>
            <div>Random: {randomNumber.toFixed(6)}</div>
            <div>Server Boolean: {booleanValue.toString()}</div>
            <div>Client Button: {buttonState.toString()}</div>
            <div>DateTime: {datetimeValue || 'Not selected'}</div>
            <div>Client ID: {clientId}</div>
            <div>Transport: Socket.IO (polling + websocket)</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

