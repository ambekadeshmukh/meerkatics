// meerkatics/frontend/src/components/Dashboard/HallucinationDetectionChart.js

import React, { useState } from 'react';
import { Box, Tabs, Tab, Grid, Typography, Paper } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const HallucinationDetectionChart = ({ data }) => {
  const [viewType, setViewType] = useState('trend');
  
  const handleViewChange = (event, newValue) => {
    setViewType(newValue);
  };
  
  // Render hallucination trend chart
  const renderTrendChart = () => {
    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={data.trend || []}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="rate" name="Hallucination Rate (%)" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    );
  };
  
  // Render hallucination distribution chart
  const renderDistributionChart = () => {
    return (
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" align="center" gutterBottom>By Model</Typography>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={data.byModel || []}
                cx="50%"
                cy="50%"
                labelLine={true}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                nameKey="name"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              >
                {(data.byModel || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
            </PieChart>
          </ResponsiveContainer>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" align="center" gutterBottom>By Application</Typography>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={data.byApplication || []}
                cx="50%"
                cy="50%"
                labelLine={true}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                nameKey="name"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              >
                {(data.byApplication || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
            </PieChart>
          </ResponsiveContainer>
        </Grid>
      </Grid>
    );
  };
  
  // Render hallucination examples or details
  const renderExamplesSection = () => {
    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle1" gutterBottom>Recent Detected Hallucinations</Typography>
        {(data.examples || []).map((example, index) => (
          <Paper key={index} sx={{ p: 2, mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Model: {example.model} | Application: {example.application} | Time: {example.timestamp}
            </Typography>
            <Typography variant="body1" paragraph>
              <strong>Prompt:</strong> {example.prompt}
            </Typography>
            <Typography variant="body1" paragraph>
              <strong>Completion:</strong> {example.completion}
            </Typography>
            <Typography variant="body1">
              <strong>Hallucination Score:</strong> {example.score.toFixed(2)} | 
              <strong> Confidence:</strong> {example.confidence}
            </Typography>
          </Paper>
        ))}
      </Box>
    );
  };
  
  return (
    <Box sx={{ height: '100%' }}>
      <Tabs
        value={viewType}
        onChange={handleViewChange}
        aria-label="hallucination detection view tabs"
        sx={{ mb: 2 }}
      >
        <Tab value="trend" label="Trend" />
        <Tab value="distribution" label="Distribution" />
        <Tab value="examples" label="Examples" />
      </Tabs>
      
      {viewType === 'trend' && renderTrendChart()}
      {viewType === 'distribution' && renderDistributionChart()}
      {viewType === 'examples' && renderExamplesSection()}
    </Box>
  );
};

export default HallucinationDetectionChart;