// meerkatics/frontend/src/components/Dashboard/DashboardLayout.js

import React, { useState, useEffect } from 'react';
import { Box, Grid, Select, MenuItem, FormControl, InputLabel, Typography, Paper } from '@mui/material';
import CostBreakdownChart from './CostBreakdownChart';
import PerformanceMetricsChart from './PerformanceMetricsChart';
import HallucinationDetectionChart from './HallucinationDetectionChart';
import SummaryCards from './SummaryCards';
import AlertsPanel from './AlertsPanel';
import { fetchDashboardData } from '../../api';

const DashboardLayout = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [provider, setProvider] = useState('all');
  const [model, setModel] = useState('all');
  const [application, setApplication] = useState('all');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filter options from data
  const [providerOptions, setProviderOptions] = useState([]);
  const [modelOptions, setModelOptions] = useState([]);
  const [applicationOptions, setApplicationOptions] = useState([]);
  
  // Fetch dashboard data based on filters
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const data = await fetchDashboardData({
          timeRange,
          provider: provider === 'all' ? null : provider,
          model: model === 'all' ? null : model,
          application: application === 'all' ? null : application
        });
        
        setDashboardData(data);
        
        // Extract filter options
        const providers = ['all', ...new Set(data.providers || [])];
        const models = ['all', ...new Set(data.models || [])];
        const applications = ['all', ...new Set(data.applications || [])];
        
        setProviderOptions(providers);
        setModelOptions(models);
        setApplicationOptions(applications);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [timeRange, provider, model, application]);
  
  // Handle filter changes
  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
  };
  
  const handleProviderChange = (event) => {
    setProvider(event.target.value);
    // Reset model when provider changes
    setModel('all');
  };
  
  const handleModelChange = (event) => {
    setModel(event.target.value);
  };
  
  const handleApplicationChange = (event) => {
    setApplication(event.target.value);
  };
  
  if (loading) {
    return <Typography>Loading dashboard data...</Typography>;
  }
  
  if (error) {
    return <Typography color="error">Error loading dashboard: {error}</Typography>;
  }
  
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Filter controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth>
              <InputLabel id="time-range-label">Time Range</InputLabel>
              <Select
                labelId="time-range-label"
                value={timeRange}
                label="Time Range"
                onChange={handleTimeRangeChange}
              >
                <MenuItem value="1h">Last Hour</MenuItem>
                <MenuItem value="6h">Last 6 Hours</MenuItem>
                <MenuItem value="24h">Last 24 Hours</MenuItem>
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth>
              <InputLabel id="provider-label">Provider</InputLabel>
              <Select
                labelId="provider-label"
                value={provider}
                label="Provider"
                onChange={handleProviderChange}
              >
                {providerOptions.map(p => (
                  <MenuItem key={p} value={p}>{p === 'all' ? 'All Providers' : p}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth>
              <InputLabel id="model-label">Model</InputLabel>
              <Select
                labelId="model-label"
                value={model}
                label="Model"
                onChange={handleModelChange}
              >
                {modelOptions.map(m => (
                  <MenuItem key={m} value={m}>{m === 'all' ? 'All Models' : m}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth>
              <InputLabel id="application-label">Application</InputLabel>
              <Select
                labelId="application-label"
                value={application}
                label="Application"
                onChange={handleApplicationChange}
              >
                {applicationOptions.map(a => (
                  <MenuItem key={a} value={a}>{a === 'all' ? 'All Applications' : a}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Summary cards */}
      <SummaryCards data={dashboardData.summary} />
      
      {/* Main charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Cost Breakdown</Typography>
            <CostBreakdownChart data={dashboardData.costBreakdown} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Performance Metrics</Typography>
            <PerformanceMetricsChart data={dashboardData.performanceMetrics} />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Hallucination Detection</Typography>
            <HallucinationDetectionChart data={dashboardData.hallucinations} />
          </Paper>
        </Grid>
      </Grid>
      
      {/* Recent alerts */}
      <Paper sx={{ p: 2, mt: 3 }}>
        <Typography variant="h6" gutterBottom>Recent Alerts</Typography>
        <AlertsPanel alerts={dashboardData.alerts} />
      </Paper>
    </Box>
  );
};

export default DashboardLayout;