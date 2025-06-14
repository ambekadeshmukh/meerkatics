import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    textAlign: 'center',
    padding: '0 20px'
  };

  const headingStyle = {
    fontSize: '6rem',
    margin: '0',
    color: '#4a6cf7'
  };

  const subheadingStyle = {
    fontSize: '1.5rem',
    margin: '10px 0 20px',
    color: '#343a40'
  };

  const textStyle = {
    fontSize: '1rem',
    maxWidth: '500px',
    margin: '0 0 30px',
    color: '#6c757d'
  };

  const buttonStyle = {
    background: '#4a6cf7',
    color: 'white',
    padding: '10px 20px',
    borderRadius: '4px',
    textDecoration: 'none',
    fontSize: '1rem',
    transition: 'background-color 0.3s'
  };

  return (
    <div style={containerStyle}>
      <h1 style={headingStyle}>404</h1>
      <h2 style={subheadingStyle}>Page Not Found</h2>
      <p style={textStyle}>
        The page you are looking for might have been removed, had its name changed, 
        or is temporarily unavailable.
      </p>
      <Link to="/" style={buttonStyle}>
        Return to Dashboard
      </Link>
    </div>
  );
};

export default NotFound;
