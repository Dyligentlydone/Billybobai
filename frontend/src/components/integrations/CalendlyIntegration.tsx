import { FC, useState } from 'react';
import {
  Box,
  FormControlLabel,
  Switch,
  TextField,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Button,
  InputAdornment,
  Alert,
  CircularProgress,
} from '@mui/material';
import { CalendlyConfig } from '../../types/calendly';
import axios from 'axios';

interface Props {
  config: CalendlyConfig;
  onChange: (updates: Partial<CalendlyConfig>) => void;
  variant?: 'sms' | 'voice';
}

export const CalendlyIntegration: FC<Props> = ({ config, onChange, variant = 'sms' }) => {
  const [validating, setValidating] = useState(false);
  const [tokenStatus, setTokenStatus] = useState<{
    valid?: boolean;
    message?: string;
    name?: string;
  } | null>(null);
  
  const handleChange = (updates: Partial<CalendlyConfig>) => {
    onChange({ ...config, ...updates });
  };
  
  const validateToken = async () => {
    if (!config.access_token) {
      setTokenStatus({
        valid: false,
        message: 'Please enter an access token',
      });
      return;
    }
    
    setValidating(true);
    try {
      const response = await axios.post('/api/integrations/calendly/validate-token', {
        access_token: config.access_token
      });
      
      if (response.data.valid) {
        setTokenStatus({
          valid: true,
          message: 'Token validated successfully',
          name: response.data.name
        });
        
        // Auto-fill the user URI
        handleChange({
          user_uri: response.data.user_uri
        });
      } else {
        setTokenStatus({
          valid: false,
          message: response.data.message || 'Invalid token',
        });
      }
    } catch (error) {
      setTokenStatus({
        valid: false,
        message: 'Error validating token. Please try again.',
      });
    }
    setValidating(false);
  };

  const title = variant === 'sms' 
    ? 'SMS Scheduling Integration' 
    : 'Voice Scheduling Integration';
  
  const description = variant === 'sms'
    ? 'Allow customers to schedule appointments via text message'
    : 'Enable automated voice scheduling for callers';

  return (
    <Box className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <Typography variant="h6">{title}</Typography>
          <Typography variant="body2" color="textSecondary">
            {description}
          </Typography>
        </div>
        <FormControlLabel
          control={
            <Switch
              checked={config.enabled}
              onChange={(e) => handleChange({ enabled: e.target.checked })}
            />
          }
          label="Enable"
        />
      </div>

      {config.enabled && (
        <Stack spacing={3}>
          <TextField
            fullWidth
            label="Access Token"
            value={config.access_token}
            onChange={(e) => {
              handleChange({ access_token: e.target.value });
              // Clear token status when token changes
              if (tokenStatus) setTokenStatus(null);
            }}
            type="password"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <Button
                    onClick={validateToken}
                    disabled={validating || !config.access_token}
                    variant="contained"
                    size="small"
                  >
                    {validating ? <CircularProgress size={20} /> : 'Validate'}
                  </Button>
                </InputAdornment>
              ),
            }}
          />
          
          {tokenStatus && (
            <Alert severity={tokenStatus.valid ? 'success' : 'error'}>
              {tokenStatus.valid 
                ? `✓ Valid token for ${tokenStatus.name}` 
                : `✗ ${tokenStatus.message}`}
            </Alert>
          )}

          <TextField
            fullWidth
            label="User URI"
            value={config.user_uri || ''}
            onChange={(e) => handleChange({ user_uri: e.target.value })}
            helperText={tokenStatus?.valid 
              ? "Auto-filled from your Calendly account" 
              : "Will be automatically retrieved when you validate your access token"}
            InputProps={{
              readOnly: tokenStatus?.valid || false,
              sx: tokenStatus?.valid ? { bgcolor: 'rgba(0, 0, 0, 0.05)' } : {}
            }}
          />

          <TextField
            fullWidth
            label="Webhook URI"
            value={config.webhook_uri}
            onChange={(e) => handleChange({ webhook_uri: e.target.value })}
            helperText="Optional: Webhook endpoint for event notifications"
          />

          <TextField
            fullWidth
            label="Default Event Type"
            value={config.default_event_type}
            onChange={(e) => handleChange({ default_event_type: e.target.value })}
          />

          <TextField
            type="number"
            fullWidth
            label="Booking Window (days)"
            value={config.booking_window_days}
            onChange={(e) => handleChange({ 
              booking_window_days: parseInt(e.target.value) || 14 
            })}
          />

          <TextField
            type="number"
            fullWidth
            label="Minimum Notice (hours)"
            value={config.min_notice_hours}
            onChange={(e) => handleChange({ 
              min_notice_hours: parseInt(e.target.value) || 4 
            })}
          />

          <FormControl fullWidth>
            <InputLabel>Reminder Hours</InputLabel>
            <Select
              multiple
              value={config.reminder_hours}
              onChange={(e) => {
                const hours = e.target.value as number[];
                handleChange({ reminder_hours: hours });
              }}
            >
              {[2, 4, 8, 12, 24, 48, 72].map((hours) => (
                <MenuItem key={hours} value={hours}>
                  {hours} hours before
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControlLabel
            control={
              <Switch
                checked={config.allow_cancellation}
                onChange={(e) => handleChange({ 
                  allow_cancellation: e.target.checked 
                })}
              />
            }
            label="Allow Cancellations"
          />

          <FormControlLabel
            control={
              <Switch
                checked={config.allow_rescheduling}
                onChange={(e) => handleChange({ 
                  allow_rescheduling: e.target.checked 
                })}
              />
            }
            label="Allow Rescheduling"
          />
        </Stack>
      )}
    </Box>
  );
}
