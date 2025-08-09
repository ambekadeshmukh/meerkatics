// meerkatics/frontend/src/components/Dashboard/CostBreakdownChart.js

import React, { useState } from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

// Custom colors for chart
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B6B'];

const CostBreakdownChart = ({ data }) => {
  const [viewType, setViewType] = useState('provider');
  
  const handleViewChange = (event, newValue) => {
    setViewType(newValue);
  };
  
  // Prepare data based on current view
  const getChartData = () => {
    switch (viewType) {
      case 'provider':
        return data.byProvider || [];
      case 'model':
        return data.byModel || [];
      case 'application':
        return data.byApplication || [];
      case 'time':
        return data.byTime || [];
      default:
        return [];
    }
  };
  
  const chartData = getChartData();
  
  // Render pie chart for all views except 'time'
  if (viewType !== 'time') {
    return (
      <Box sx={{ height: '100%' }}>
        <Tabs
          value={viewType}
          onChange={handleViewChange}
          aria-label="cost breakdown view tabs"
          sx={{ mb: 2 }}
        >
          <Tab value="provider" label="By Provider" />
          <Tab value="model" label="By Model" />
          <Tab value="application" label="By Application" />
          <Tab value="time" label="Over Time" />
        </Tabs>
        
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={true}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
              nameKey="name"
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Box>
    );
  }
  
  // Render bar chart for 'time' view
  return (
    <Box sx={{ height: '100%' }}>
      <Tabs
        value={viewType}
        onChange={handleViewChange}
        aria-label="cost breakdown view tabs"
        sx={{ mb: 2 }}
      >
        <Tab value="provider" label="By Provider" />
        <Tab value="model" label="By Model" />
        <Tab value="application" label="By Application" />
        <Tab value="time" label="Over Time" />
      </Tabs>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis tickFormatter={(value) => `$${value}`} />
          <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
          <Legend />
          <Bar dataKey="value" name="Cost" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default CostBreakdownChart;