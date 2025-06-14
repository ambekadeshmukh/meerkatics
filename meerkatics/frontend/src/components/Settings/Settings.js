import React, { useState } from 'react';

const Settings = () => {
  const [settings, setSettings] = useState({
    apiKey: localStorage.getItem('api_key') || '',
    apiUrl: localStorage.getItem('api_url') || 'http://localhost:8000',
    theme: localStorage.getItem('theme') || 'light',
    refreshInterval: localStorage.getItem('refresh_interval') || '30'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSettings({
      ...settings,
      [name]: value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Save settings to localStorage
    localStorage.setItem('api_key', settings.apiKey);
    localStorage.setItem('api_url', settings.apiUrl);
    localStorage.setItem('theme', settings.theme);
    localStorage.setItem('refresh_interval', settings.refreshInterval);
    
    alert('Settings saved successfully');
  };

  return (
    <div className="settings-container">
      <h1>Settings</h1>
      
      <div className="settings-card">
        <h2>API Configuration</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="apiUrl">API URL</label>
            <input
              type="text"
              id="apiUrl"
              name="apiUrl"
              value={settings.apiUrl}
              onChange={handleChange}
              placeholder="e.g., http://localhost:8000"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="apiKey">API Key</label>
            <input
              type="password"
              id="apiKey"
              name="apiKey"
              value={settings.apiKey}
              onChange={handleChange}
              placeholder="Your API key"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="theme">Theme</label>
            <select 
              id="theme" 
              name="theme" 
              value={settings.theme}
              onChange={handleChange}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System Default</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="refreshInterval">Dashboard Refresh Interval (seconds)</label>
            <input
              type="number"
              id="refreshInterval"
              name="refreshInterval"
              value={settings.refreshInterval}
              onChange={handleChange}
              min="5"
              max="300"
            />
          </div>
          
          <button type="submit" className="save-button">Save Settings</button>
        </form>
      </div>
      
      <div className="settings-card">
        <h2>About Meerkatics</h2>
        <p>Version: 0.1.0</p>
        <p>Built with ❤️ by the Meerkatics Team</p>
        <p>
          <a href="https://github.com/meerkatics/meerkatics" target="_blank" rel="noopener noreferrer">
            GitHub Repository
          </a>
        </p>
      </div>
    </div>
  );
};

export default Settings;
