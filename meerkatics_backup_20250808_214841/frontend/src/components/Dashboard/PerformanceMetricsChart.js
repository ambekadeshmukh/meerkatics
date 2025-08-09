// meerkatics/frontend/src/components/Dashboard/PerformanceMetricsChart.js

import React, { useState } from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const PerformanceMetricsChart = ({ data }) => {
  const [metricType, setMetricType] = useState('latency');
  
  const handleMetricChange = (event, newValue) => {
    setMetricType(newValue);
  };
  
  // Prepare data based on selected metric
  const getChartData = () => {
    switch (metricType) {
      case 'latency':
        return data.latency || [];
      case 'tokens':
        return data.tokens || [];
      case 'requests':
        return data.requests || [];
      case 'errors':
        return data.errors || [];
      default:
        return [];
    }
  };
  
  const chartData = getChartData();
  
  // Different chart types based on the metric
  const renderChart = () => {
    if (metricType === 'latency') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip formatter={(value) => `${value.toFixed(2)} ms`} />
            <Legend />
            <Line type="monotone" dataKey="avg" name="Average" stroke="#8884d8" />
            <Line type="monotone" dataKey="p95" name="95th Percentile" stroke="#82ca9d" />
            <Line type="monotone" dataKey="max" name="Maximum" stroke="#ff7300" />
          </LineChart>
        </ResponsiveContainer>
      );
    }
    
    if (metricType === 'tokens') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="prompt" name="Prompt Tokens" fill="#8884d8" />
            <Bar dataKey="completion" name="Completion Tokens" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      );
    }
    
    if (metricType === 'requests') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" name="Request Count" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      );
    }
    
    if (metricType === 'errors') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="rate" name="Error Rate (%)" stroke="#ff7300" />
          </LineChart>
        </ResponsiveContainer>
      );
    }
    
    return null;
  };
  
  return (
    <Box sx={{ height: '100%' }}>
      <Tabs
        value={metricType}
        onChange={handleMetricChange}
        aria-label="performance metrics tabs"
        sx={{ mb: 2 }}
      >
        <Tab value="latency" label="Latency" />
        <Tab value="tokens" label="Token Usage" />
        <Tab value="requests" label="Request Volume" />
        <Tab value="errors" label="Error Rate" />
      </Tabs>
      
      {renderChart()}
    </Box>
  );
};

export default PerformanceMetricsChart;