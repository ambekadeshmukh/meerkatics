// frontend/src/components/Dashboard/DashboardSimple.js
import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Box,
  CircularProgress,
  Chip,
  Alert
} from '@mui/material';

const DashboardSimple = () => {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    totalRequests: 0,
    totalCost: 0,
    avgLatency: 0,
    errorRate: 0,
    successRate: 0,
    activeModels: 0
  });

  // Simulate loading metrics
  useEffect(() => {
    const loadMetrics = async () => {
      // Simulate API call
      setTimeout(() => {
        setMetrics({
          totalRequests: 12458,
          totalCost: 245.67,
          avgLatency: 1.2,
          errorRate: 0.8,
          successRate: 99.2,
          activeModels: 8
        });
        setLoading(false);
      }, 1000);
    };

    loadMetrics();
  }, []);

  const MetricCard = ({ title, value, subtitle }) => (
    <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {loading ? <CircularProgress size={24} /> : value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Meerkatics Dashboard
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          AI/LLM Observability Platform - Real-time monitoring and analytics
        </Typography>
      </Box>

      <Alert severity="success" sx={{ mb: 3 }}>
        All systems operational • Last updated: {new Date().toLocaleTimeString()}
      </Alert>

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Total Requests"
            value={metrics.totalRequests.toLocaleString()}
            subtitle="Last 24 hours"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Total Cost"
            value={`$${metrics.totalCost.toFixed(2)}`}
            subtitle="Last 24 hours"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Avg Latency"
            value={`${metrics.avgLatency}s`}
            subtitle="Response time"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Success Rate"
            value={`${metrics.successRate}%`}
            subtitle="Last 24 hours"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Error Rate"
            value={`${metrics.errorRate}%`}
            subtitle="Last 24 hours"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Active Models"
            value={metrics.activeModels}
            subtitle="Currently monitored"
          />
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            <Chip label="API Server: Online" color="success" size="small" />
            <Chip label="Stream Processor: Running" color="success" size="small" />
            <Chip label="Database: Connected" color="success" size="small" />
            <Chip label="Monitoring: Active" color="success" size="small" />
          </Box>
          
          <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
            Welcome to Meerkatics! Your AI/LLM observability platform is ready for monitoring.
            Connect your applications using our SDK to start collecting metrics.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardSimple;
