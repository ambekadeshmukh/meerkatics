import React from 'react';
import { Card, CardContent, Typography, Box, Avatar } from '@mui/material';
import { styled } from '@mui/material/styles';

// Styled components
const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  transition: 'transform 0.3s, box-shadow 0.3s',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[4],
  },
}));

const IconAvatar = styled(Avatar)(({ bgcolor }) => ({
  backgroundColor: bgcolor || '#1976d2',
  color: 'white',
  width: 56,
  height: 56,
}));

const MetricCard = ({ title, value, icon, color, subtitle, trend }) => {
  return (
    <StyledCard>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <IconAvatar bgcolor={color}>
            {icon}
          </IconAvatar>
          <Box sx={{ ml: 2 }}>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
          </Box>
        </Box>
        
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
        
        {trend && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            {trend.direction === 'up' ? (
              <Typography 
                variant="body2" 
                color={trend.positive ? 'success.main' : 'error.main'}
                sx={{ display: 'flex', alignItems: 'center' }}
              >
                ↑ {trend.value}%
              </Typography>
            ) : (
              <Typography 
                variant="body2" 
                color={trend.positive ? 'success.main' : 'error.main'}
                sx={{ display: 'flex', alignItems: 'center' }}
              >
                ↓ {trend.value}%
              </Typography>
            )}
            <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
              vs previous period
            </Typography>
          </Box>
        )}
      </CardContent>
    </StyledCard>
  );
};

export default MetricCard;
