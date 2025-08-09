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
    // Connect to the Flask-SocketIO server
    const newSocket = io('http://localhost:5000', {
      transports: ['websocket']
    });

    newSocket.on('connect', () => {
      console.log('Connected to server');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setIsConnected(false);
    });

    newSocket.on('message', (data) => {
      console.log('Received:', data);
      setRandomNumber(data.randomNumber);
      setBooleanValue(data.boolean);
    });

    newSocket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setIsConnected(false);
    });

    newSocket.on('button_ack', (data) => {
      console.log('Server acknowledged button toggle:', data);
    });

    newSocket.on('datetime_ack', (data) => {
      console.log('Server acknowledged datetime change:', data);
    });

    setSocket(newSocket);

    // Cleanup on unmount
    return () => {
      newSocket.close();
    };
  }, []);

  const handleButtonToggle = () => {
    const newButtonState = !buttonState;
    setButtonState(newButtonState);
    
    if (socket && isConnected) {
      // Emit the toggle event to the server
      socket.emit('toggle_button', {
        buttonState: newButtonState,
        clientId: clientId,
        timestamp: new Date().toISOString()
      });
      console.log(`Button toggled to: ${newButtonState}`);
    }
  };

  const handleDatetimeChange = (event) => {
    const newDatetimeValue = event.target.value;
    setDatetimeValue(newDatetimeValue);
    
    if (socket && isConnected && newDatetimeValue) {
      // Emit the datetime change event to the server
      socket.emit('datetime_change', {
        datetimeValue: newDatetimeValue,
        clientId: clientId,
        inputType: 'datetime-local',
        timestamp: new Date().toISOString()
      });
      console.log(`Datetime changed to: ${newDatetimeValue}`);
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
            <div className="input-icon">
              <svg className="calendar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
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
            <div>Updates: 2 per second</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;