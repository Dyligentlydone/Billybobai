import type { FC } from 'react';
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
} from '@mui/material';
import { CalendlyConfig } from '../../types/calendly';

interface Props {
  config: CalendlyConfig;
  onChange: (updates: Partial<CalendlyConfig>) => void;
  variant?: 'sms' | 'voice';
}

export const CalendlyIntegration: FC<Props> = ({ config, onChange, variant = 'sms' }) => {
  const handleChange = (updates: Partial<CalendlyConfig>) => {
    onChange({ ...config, ...updates });
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
            onChange={(e) => handleChange({ access_token: e.target.value })}
            type="password"
          />

          <TextField
            fullWidth
            label="User URI"
            value={config.user_uri}
            onChange={(e) => handleChange({ user_uri: e.target.value })}
            helperText="Your Calendly user URI (e.g., https://calendly.com/your-name)"
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
