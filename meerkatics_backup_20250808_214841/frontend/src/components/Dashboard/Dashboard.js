import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, Cell, AreaChart, Area
} from 'recharts';
import { 
  Grid, Card, CardContent, Typography, Box, 
  CircularProgress, Tabs, Tab, Select, MenuItem,
  FormControl, InputLabel, Button, Chip, Divider
} from '@mui/material';
import { 
  AccessTime, AttachMoney, Memory, 
  Speed, Error, Insights, TrendingUp
} from '@mui/icons-material';
import { format } from 'date-fns';
import { axiosInstance, COLORS } from '../../App';
import MetricCard from '../common/MetricCard';
import ErrorBoundary from '../common/ErrorBoundary';
import './Dashboard.css';

const Dashboard = () => {
  // State for dashboard data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [timeseriesData, setTimeseriesData] = useState({});
  const [topModels, setTopModels] = useState([]);
  const [topApplications, setTopApplications] = useState([]);
  const [recentAnomalies, setRecentAnomalies] = useState([]);
  const [recentRequests, setRecentRequests] = useState([]);
  
  // State for filters
  const [timeRange, setTimeRange] = useState('24h');
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedMetric, setSelectedMetric] = useState('inference_time');
  
  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Fetch dashboard summary
        const summaryResponse = await axiosInstance.get('/v1/dashboard/summary', {
          params: { time_range: timeRange }
        });
        setSummary(summaryResponse.data);
        
        // Fetch time series data for selected metric
        const timeseriesResponse = await axiosInstance.get('/v1/metrics/timeseries', {
          params: { 
            metric: selectedMetric,
            time_range: timeRange
          }
        });
        setTimeseriesData(timeseriesResponse.data);
        
        // Fetch top models by usage
        const topModelsResponse = await axiosInstance.get('/v1/analytics/top-models', {
          params: { 
            metric: 'total_tokens',
            limit: 5,
            time_range: timeRange
          }
        });
        setTopModels(topModelsResponse.data);
        
        // Fetch top applications by usage
        const topAppsResponse = await axiosInstance.get('/v1/analytics/top-applications', {
          params: { 
            metric: 'total_tokens',
            limit: 5,
            time_range: timeRange
          }
        });
        setTopApplications(topAppsResponse.data);
        
        // Fetch recent anomalies
        const anomaliesResponse = await axiosInstance.get('/v1/anomalies', {
          params: { 
            limit: 5,
            time_range: timeRange
          }
        });
        setRecentAnomalies(anomaliesResponse.data);
        
        // Fetch recent requests
        const requestsResponse = await axiosInstance.get('/v1/requests', {
          params: { 
            limit: 10,
            time_range: timeRange
          }
        });
        setRecentRequests(requestsResponse.data);
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [timeRange, selectedMetric]);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };
  
  // Handle time range change
  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
  };
  
  // Handle metric change
  const handleMetricChange = (event) => {
    setSelectedMetric(event.target.value);
  };
  
  // Format timestamp for charts
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return format(date, 'HH:mm');
  };
  
  // Format number with abbreviation
  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num;
  };
  
  // Render loading state
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading dashboard data...
        </Typography>
      </Box>
    );
  }
  
  // Render error state
  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Typography variant="h6" color="error">
          {error}
        </Typography>
        <Button variant="contained" sx={{ ml: 2 }} onClick={() => window.location.reload()}>
          Retry
        </Button>
      </Box>
    );
  }
  
  // Calculate summary metrics
  const totalRequests = summary?.total_requests || 0;
  const totalTokens = summary?.total_tokens || 0;
  const avgInferenceTime = summary?.avg_inference_time || 0;
  const totalCost = summary?.total_cost || 0;
  const errorRate = summary?.error_rate || 0;
  
  return (
    <ErrorBoundary>
      <div className="dashboard-container">
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Dashboard
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <FormControl variant="outlined" size="small" sx={{ minWidth: 120, mr: 2 }}>
              <InputLabel id="time-range-label">Time Range</InputLabel>
              <Select
                labelId="time-range-label"
                value={timeRange}
                onChange={handleTimeRangeChange}
                label="Time Range"
              >
                <MenuItem value="1h">Last Hour</MenuItem>
                <MenuItem value="24h">Last 24 Hours</MenuItem>
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
              </Select>
            </FormControl>
            
            <Button 
              variant="outlined" 
              onClick={() => window.location.reload()}
              startIcon={<Insights />}
            >
              Refresh
            </Button>
          </Box>
        </Box>
        
        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={2.4}>
            <MetricCard 
              title="Total Requests" 
              value={formatNumber(totalRequests)}
              icon={<TrendingUp />}
              color="#3f51b5"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <MetricCard 
              title="Total Tokens" 
              value={formatNumber(totalTokens)}
              icon={<Memory />}
              color="#4caf50"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <MetricCard 
              title="Avg Inference Time" 
              value={`${avgInferenceTime.toFixed(2)}s`}
              icon={<Speed />}
              color="#ff9800"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <MetricCard 
              title="Total Cost" 
              value={`$${totalCost.toFixed(2)}`}
              icon={<AttachMoney />}
              color="#2196f3"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <MetricCard 
              title="Error Rate" 
              value={`${(errorRate * 100).toFixed(2)}%`}
              icon={<Error />}
              color={errorRate > 0.05 ? "#f44336" : "#757575"}
            />
          </Grid>
        </Grid>
        
        {/* Tabs for different views */}
        <Box sx={{ mb: 3 }}>
          <Tabs 
            value={selectedTab} 
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="Overview" />
            <Tab label="Performance" />
            <Tab label="Usage" />
            <Tab label="Costs" />
            <Tab label="Errors" />
          </Tabs>
        </Box>
        
        {/* Overview Tab */}
        {selectedTab === 0 && (
          <Grid container spacing={3}>
            {/* Time Series Chart */}
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                      Request Metrics Over Time
                    </Typography>
                    <FormControl variant="outlined" size="small" sx={{ minWidth: 150 }}>
                      <InputLabel id="metric-label">Metric</InputLabel>
                      <Select
                        labelId="metric-label"
                        value={selectedMetric}
                        onChange={handleMetricChange}
                        label="Metric"
                      >
                        <MenuItem value="inference_time">Inference Time</MenuItem>
                        <MenuItem value="total_tokens">Token Usage</MenuItem>
                        <MenuItem value="estimated_cost">Cost</MenuItem>
                        <MenuItem value="error_rate">Error Rate</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={timeseriesData.data || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp" 
                        tickFormatter={formatTimestamp} 
                        minTickGap={60}
                      />
                      <YAxis />
                      <Tooltip 
                        formatter={(value) => [value.toFixed(2), selectedMetric.replace('_', ' ')]}
                        labelFormatter={(label) => format(new Date(label), 'yyyy-MM-dd HH:mm')}
                      />
                      <Legend />
                      <Area 
                        type="monotone" 
                        dataKey="value" 
                        name={selectedMetric.replace('_', ' ')} 
                        stroke={COLORS[0]} 
                        fill={COLORS[0]} 
                        fillOpacity={0.3}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Top Models Pie Chart */}
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Top Models by Usage
                  </Typography>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={topModels}
                        dataKey="usage"
                        nameKey="model"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                      >
                        {topModels.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatNumber(value)} />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Recent Anomalies */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Recent Anomalies
                  </Typography>
                  {recentAnomalies.length > 0 ? (
                    <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                      {recentAnomalies.map((anomaly) => (
                        <Box 
                          key={anomaly.id} 
                          sx={{ 
                            p: 2, 
                            mb: 1, 
                            border: '1px solid #e0e0e0', 
                            borderRadius: 1,
                            backgroundColor: '#f5f5f5'
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="subtitle1">
                              {anomaly.anomaly_type}
                            </Typography>
                            <Chip 
                              size="small" 
                              label={format(new Date(anomaly.timestamp), 'yyyy-MM-dd HH:mm')}
                              color="primary"
                            />
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            {anomaly.description}
                          </Typography>
                          <Box sx={{ mt: 1 }}>
                            <Chip size="small" label={anomaly.model} sx={{ mr: 1 }} />
                            <Chip size="small" label={anomaly.application} />
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body1" sx={{ textAlign: 'center', py: 4 }}>
                      No anomalies detected in the selected time range.
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
            
            {/* Top Applications */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Top Applications by Usage
                  </Typography>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={topApplications}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="application" />
                      <YAxis tickFormatter={formatNumber} />
                      <Tooltip formatter={(value) => formatNumber(value)} />
                      <Legend />
                      <Bar dataKey="usage" name="Token Usage" fill={COLORS[1]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
        
        {/* Performance Tab */}
        {selectedTab === 1 && (
          <Grid container spacing={3}>
            {/* Performance metrics would go here */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6">Performance Metrics</Typography>
                  {/* Performance visualizations */}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
        
        {/* Usage Tab */}
        {selectedTab === 2 && (
          <Grid container spacing={3}>
            {/* Usage metrics would go here */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6">Usage Metrics</Typography>
                  {/* Usage visualizations */}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
        
        {/* Costs Tab */}
        {selectedTab === 3 && (
          <Grid container spacing={3}>
            {/* Cost metrics would go here */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6">Cost Metrics</Typography>
                  {/* Cost visualizations */}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
        
        {/* Errors Tab */}
        {selectedTab === 4 && (
          <Grid container spacing={3}>
            {/* Error metrics would go here */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6">Error Metrics</Typography>
                  {/* Error visualizations */}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default Dashboard;