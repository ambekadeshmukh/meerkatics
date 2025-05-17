import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Divider, 
  Chip, 
  IconButton, 
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
  Snackbar,
  Alert
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Error as ErrorIcon,
  Check as CheckIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material';
import axios from 'axios';
import { formatDistanceToNow } from 'date-fns';

const AlertsPanel = () => {
  // State
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openFilterDialog, setOpenFilterDialog] = useState(false);
  const [severityFilter, setSeverityFilter] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  
  // New alert form state
  const [newAlert, setNewAlert] = useState({
    title: '',
    message: '',
    severity: 'info',
    metadata: {}
  });

  // Fetch alerts
  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      params.append('limit', 100);
      
      if (severityFilter) {
        params.append('severity', severityFilter);
      }
      
      const response = await axios.get(`/api/alerts/history?${params.toString()}`);
      setAlerts(response.data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError('Failed to fetch alerts. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchAlerts();
  }, [severityFilter]);

  // Handlers
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleCreateAlert = async () => {
    try {
      await axios.post('/api/alerts', newAlert);
      setOpenCreateDialog(false);
      setNewAlert({
        title: '',
        message: '',
        severity: 'info',
        metadata: {}
      });
      setSnackbar({
        open: true,
        message: 'Alert created successfully',
        severity: 'success'
      });
      fetchAlerts();
    } catch (err) {
      console.error('Error creating alert:', err);
      setSnackbar({
        open: true,
        message: 'Failed to create alert',
        severity: 'error'
      });
    }
  };

  const handleTestAlert = async (channel) => {
    try {
      await axios.post(`/api/alerts/test?channel=${channel}`);
      setSnackbar({
        open: true,
        message: `Test alert sent to ${channel}`,
        severity: 'success'
      });
    } catch (err) {
      console.error(`Error testing ${channel} alert:`, err);
      setSnackbar({
        open: true,
        message: `Failed to send test alert to ${channel}`,
        severity: 'error'
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Render severity icon
  const renderSeverityIcon = (severity) => {
    switch (severity) {
      case 'info':
        return <InfoIcon fontSize="small" sx={{ color: 'info.main' }} />;
      case 'warning':
        return <WarningIcon fontSize="small" sx={{ color: 'warning.main' }} />;
      case 'error':
        return <ErrorIcon fontSize="small" sx={{ color: 'error.main' }} />;
      case 'critical':
        return <ErrorIcon fontSize="small" sx={{ color: 'error.dark' }} />;
      default:
        return <InfoIcon fontSize="small" sx={{ color: 'info.main' }} />;
    }
  };

  // Render severity chip
  const renderSeverityChip = (severity) => {
    const colorMap = {
      info: 'info',
      warning: 'warning',
      error: 'error',
      critical: 'error'
    };
    
    return (
      <Chip 
        icon={renderSeverityIcon(severity)}
        label={severity.toUpperCase()}
        color={colorMap[severity] || 'default'}
        size="small"
        variant="outlined"
      />
    );
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" component="h2" sx={{ display: 'flex', alignItems: 'center' }}>
          <NotificationsIcon sx={{ mr: 1 }} /> Alerts & Notifications
        </Typography>
        
        <Box>
          <Button 
            startIcon={<FilterListIcon />}
            size="small"
            onClick={() => setOpenFilterDialog(true)}
            sx={{ mr: 1 }}
          >
            Filter
          </Button>
          
          <Button 
            startIcon={<RefreshIcon />}
            size="small"
            onClick={fetchAlerts}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            size="small"
            onClick={() => setOpenCreateDialog(true)}
          >
            Create Alert
          </Button>
        </Box>
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      ) : alerts.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="textSecondary">
            No alerts found. {severityFilter && `Try removing the "${severityFilter}" filter.`}
          </Typography>
        </Paper>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Severity</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Message</TableCell>
                  <TableCell>Time</TableCell>
                  <TableCell>Metadata</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {alerts
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((alert, index) => (
                    <TableRow key={index} hover>
                      <TableCell>
                        {renderSeverityChip(alert.severity)}
                      </TableCell>
                      <TableCell>{alert.title}</TableCell>
                      <TableCell>{alert.message}</TableCell>
                      <TableCell>
                        {formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true })}
                      </TableCell>
                      <TableCell>
                        {Object.keys(alert.metadata).length > 0 ? (
                          <Box sx={{ maxWidth: 200, maxHeight: 100, overflow: 'auto' }}>
                            {Object.entries(alert.metadata).map(([key, value]) => (
                              <Typography key={key} variant="caption" display="block">
                                <strong>{key}:</strong> {value.toString()}
                              </Typography>
                            ))}
                          </Box>
                        ) : (
                          <Typography variant="caption" color="textSecondary">
                            No metadata
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={alerts.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </>
      )}
      
      {/* Create Alert Dialog */}
      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Alert</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Title"
            fullWidth
            variant="outlined"
            value={newAlert.title}
            onChange={(e) => setNewAlert({ ...newAlert, title: e.target.value })}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            label="Message"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={newAlert.message}
            onChange={(e) => setNewAlert({ ...newAlert, message: e.target.value })}
            sx={{ mb: 2 }}
          />
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="severity-label">Severity</InputLabel>
            <Select
              labelId="severity-label"
              value={newAlert.severity}
              label="Severity"
              onChange={(e) => setNewAlert({ ...newAlert, severity: e.target.value })}
            >
              <MenuItem value="info">Info</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="error">Error</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
            </Select>
          </FormControl>
          
          <Typography variant="subtitle2" gutterBottom>
            Test Channels
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Button 
              variant="outlined" 
              size="small"
              onClick={() => handleTestAlert('email')}
            >
              Test Email
            </Button>
            <Button 
              variant="outlined" 
              size="small"
              onClick={() => handleTestAlert('slack')}
            >
              Test Slack
            </Button>
            <Button 
              variant="outlined" 
              size="small"
              onClick={() => handleTestAlert('webhook')}
            >
              Test Webhook
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateAlert} 
            variant="contained"
            disabled={!newAlert.title || !newAlert.message}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Filter Dialog */}
      <Dialog open={openFilterDialog} onClose={() => setOpenFilterDialog(false)}>
        <DialogTitle>Filter Alerts</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 1 }}>
            <InputLabel id="severity-filter-label">Severity</InputLabel>
            <Select
              labelId="severity-filter-label"
              value={severityFilter}
              label="Severity"
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <MenuItem value="">All Severities</MenuItem>
              <MenuItem value="info">Info</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="error">Error</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => {
              setSeverityFilter('');
              setOpenFilterDialog(false);
            }}
          >
            Clear Filters
          </Button>
          <Button 
            onClick={() => setOpenFilterDialog(false)} 
            variant="contained"
          >
            Apply
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AlertsPanel;
