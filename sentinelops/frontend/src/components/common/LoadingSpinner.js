import React from 'react';

const LoadingSpinner = () => {
  const spinnerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    width: '100%'
  };

  const spinner = {
    width: '50px',
    height: '50px',
    border: '5px solid rgba(0, 0, 0, 0.1)',
    borderTopColor: '#4a6cf7',
    borderRadius: '50%',
    animation: 'spin 1s ease-in-out infinite'
  };

  return (
    <div style={spinnerStyle}>
      <style>
        {`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}
      </style>
      <div style={spinner}></div>
    </div>
  );
};

export default LoadingSpinner;
