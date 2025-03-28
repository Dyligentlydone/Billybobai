import React from 'react';
import { Box, Stack, TextField, Switch, FormControlLabel, Typography } from '@mui/material';

interface CalendlySetupProps {
  config: {
    enabled: boolean;
    access_token: string;
    user_uri: string;
    webhook_uri?: string;
    default_event_type: string;
    booking_window_days: number;
    min_notice_hours: number;
    reminder_hours: number[];
    allow_cancellation: boolean;
    allow_rescheduling: boolean;
  };
  onChange: (updates: Partial<CalendlySetupProps['config']>) => void;
}

export const CalendlySetup: React.FC<CalendlySetupProps> = ({ config, onChange }) => {
  const handleChange = (field: keyof CalendlySetupProps['config']) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    onChange({ [field]: value });
  };

  const handleArrayChange = (field: keyof CalendlySetupProps['config']) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.value.split(',').map(Number);
    onChange({ [field]: value });
  };

  return (
    <Box>
      <Stack spacing={3}>
        <Typography variant="h6">Calendly Integration</Typography>
        
        <FormControlLabel
          control={
            <Switch
              checked={config.enabled}
              onChange={handleChange('enabled')}
            />
          }
          label="Enable Calendly Integration"
        />

        {config.enabled && (
          <>
            <TextField
              label="Access Token"
              value={config.access_token}
              onChange={handleChange('access_token')}
              fullWidth
              type="password"
              required
            />

            <TextField
              label="User URI"
              value={config.user_uri}
              onChange={handleChange('user_uri')}
              fullWidth
              required
              helperText="Your Calendly user URI (e.g., https://calendly.com/your-username)"
            />

            <TextField
              label="Webhook URI"
              value={config.webhook_uri}
              onChange={handleChange('webhook_uri')}
              fullWidth
              helperText="Optional: Webhook URL for receiving booking notifications"
            />

            <TextField
              label="Default Event Type"
              value={config.default_event_type}
              onChange={handleChange('default_event_type')}
              fullWidth
              required
              helperText="The default event type to use for bookings"
            />

            <TextField
              label="Booking Window (Days)"
              value={config.booking_window_days}
              onChange={handleChange('booking_window_days')}
              fullWidth
              type="number"
              inputProps={{ min: 1 }}
              required
            />

            <TextField
              label="Minimum Notice (Hours)"
              value={config.min_notice_hours}
              onChange={handleChange('min_notice_hours')}
              fullWidth
              type="number"
              inputProps={{ min: 0 }}
              required
            />

            <TextField
              label="Reminder Hours"
              value={config.reminder_hours.join(',')}
              onChange={handleArrayChange('reminder_hours')}
              fullWidth
              helperText="Comma-separated list of hours before the event to send reminders"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={config.allow_cancellation}
                  onChange={handleChange('allow_cancellation')}
                />
              }
              label="Allow Cancellations"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={config.allow_rescheduling}
                  onChange={handleChange('allow_rescheduling')}
                />
              }
              label="Allow Rescheduling"
            />
          </>
        )}
      </Stack>
    </Box>
  );
};
