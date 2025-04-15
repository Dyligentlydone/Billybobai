import React, { useState, useEffect } from 'react';
import { useWizard } from '../../../contexts/WizardContext';
import {
  Box,
  Stack,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  IconButton,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { enqueueSnackbar } from 'notistack';

interface EventType {
  id: string;
  name: string;
  duration: number;
  description?: string;
  price?: number;
}

interface SMSNotificationSettings {
  enabled: boolean;
  include_cancel_link: boolean;
  include_reschedule_link: boolean;
  confirmation_message: string;
  reminder_message: string;
  cancellation_message: string;
  reschedule_message: string;
}

interface CalendlyConfig {
  enabled: boolean;
  access_token: string;
  user_uri: string;
  webhook_uri?: string;
  default_event_type: string;
  reminder_hours: number[];
  allow_cancellation: boolean;
  allow_rescheduling: boolean;
  booking_window_days: number;
  min_notice_hours: number;
  sms_notifications: SMSNotificationSettings;
}

const DEFAULT_CONFIG: CalendlyConfig = {
  enabled: false,
  access_token: '',
  user_uri: '',
  default_event_type: '',
  reminder_hours: [24, 1],
  allow_cancellation: true,
  allow_rescheduling: true,
  booking_window_days: 14,
  min_notice_hours: 1,
  sms_notifications: {
    enabled: true,
    include_cancel_link: true,
    include_reschedule_link: true,
    confirmation_message: 'Your appointment is confirmed for {{time}}. We look forward to meeting with you!',
    reminder_message: 'Reminder: Your appointment is scheduled for {{time}}.',
    cancellation_message: 'Your appointment for {{time}} has been cancelled.',
    reschedule_message: 'Your appointment has been rescheduled to {{time}}.'
  }
};

const CalendlySetup: React.FC = () => {
  const { state, updateState } = useWizard();
  const [config, setConfig] = useState<CalendlyConfig>(state.calendly || DEFAULT_CONFIG);
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [testingSMS, setTestingSMS] = useState(false);

  useEffect(() => {
    if (config.enabled && config.access_token && config.user_uri) {
      fetchEventTypes();
    }
  }, [config.enabled, config.access_token, config.user_uri]);

  const handleChange = (field: keyof CalendlyConfig, value: any) => {
    const newConfig = { ...config, [field]: value };
    setConfig(newConfig);
    updateState({ calendly: newConfig });
  };

  const fetchEventTypes = async () => {
    try {
      const response = await axios.get('/api/calendly/event-types', {
        headers: { Authorization: `Bearer ${config.access_token}` }
      });
      setEventTypes(response.data);
    } catch (err) {
      setError('Failed to fetch event types. Please check your credentials.');
      console.error('Error fetching event types:', err);
    }
  };

  const testConnection = async () => {
    setTestStatus('testing');
    try {
      await axios.post('/api/calendly/test-connection', {
        access_token: config.access_token,
        user_uri: config.user_uri
      });
      setTestStatus('success');
      setError(null);
    } catch (err) {
      setTestStatus('error');
      setError('Connection test failed. Please check your credentials.');
    }
  };

  const handleReminderChange = (index: number, value: string) => {
    const hours = [...config.reminder_hours];
    hours[index] = parseInt(value);
    handleChange('reminder_hours', hours);
  };

  const addReminder = () => {
    handleChange('reminder_hours', [...config.reminder_hours, 24]);
  };

  const removeReminder = (index: number) => {
    const hours = config.reminder_hours.filter((_, i) => i !== index);
    handleChange('reminder_hours', hours);
  };

  const testSMSNotifications = async () => {
    setTestingSMS(true);
    try {
      await axios.post(`/api/calendly/test-sms?business_id=${state.businessId}`);
      setError(null);
      enqueueSnackbar('Test SMS messages sent successfully!', { variant: 'success' });
    } catch (error: any) {
      console.error('Error testing SMS:', error);
      const errorMessage = error.response?.data?.error || 'Failed to send test SMS messages';
      setError(errorMessage);
      enqueueSnackbar(errorMessage, { variant: 'error' });
    } finally {
      setTestingSMS(false);
    }
  };

  if (!config.enabled) {
    return (
      <Box p={2}>
        <FormControlLabel
          control={
            <Switch
              checked={config.enabled}
              onChange={(e) => handleChange('enabled', e.target.checked)}
            />
          }
          label="Enable Calendly Integration"
        />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, p: 2 }}>
      <Stack spacing={3}>
        <FormControlLabel
          control={
            <Switch
              checked={config.enabled}
              onChange={(e) => handleChange('enabled', e.target.checked)}
            />
          }
          label="Enable Calendly Integration"
        />

        <Card>
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="h6">Calendly Credentials</Typography>
              
              <TextField
                fullWidth
                label="Access Token"
                value={config.access_token}
                onChange={(e) => handleChange('access_token', e.target.value)}
                type="password"
                required
              />
              
              <TextField
                fullWidth
                label="User URI"
                value={config.user_uri}
                onChange={(e) => handleChange('user_uri', e.target.value)}
                required
                helperText="Your Calendly user URI (e.g., https://calendly.com/your-uri)"
              />

              <TextField
                fullWidth
                label="Webhook URI (Optional)"
                value={config.webhook_uri}
                onChange={(e) => handleChange('webhook_uri', e.target.value)}
                helperText="URL where Calendly will send event notifications"
              />

              <Box>
                <Button
                  variant="outlined"
                  onClick={testConnection}
                  disabled={testStatus === 'testing'}
                  startIcon={testStatus === 'testing' ? <CircularProgress size={20} /> : <RefreshIcon />}
                >
                  Test Connection
                </Button>
                {testStatus === 'success' && (
                  <Alert severity="success" sx={{ mt: 1 }}>Connection successful!</Alert>
                )}
                {testStatus === 'error' && (
                  <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>
                )}
              </Box>
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Stack spacing={2}>
              <Typography variant="h6">Booking Settings</Typography>
              
              <FormControl fullWidth>
                <InputLabel>Default Event Type</InputLabel>
                <Select
                  value={config.default_event_type}
                  onChange={(e) => handleChange('default_event_type', e.target.value)}
                  label="Default Event Type"
                >
                  {eventTypes.map((type) => (
                    <MenuItem key={type.id} value={type.id}>
                      {type.name} ({type.duration} min)
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  fullWidth
                  type="number"
                  label="Booking Window (Days)"
                  value={config.booking_window_days}
                  onChange={(e) => handleChange('booking_window_days', parseInt(e.target.value))}
                  InputProps={{ inputProps: { min: 1 } }}
                />

                <TextField
                  fullWidth
                  type="number"
                  label="Minimum Notice (Hours)"
                  value={config.min_notice_hours}
                  onChange={(e) => handleChange('min_notice_hours', parseInt(e.target.value))}
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Box>

              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Reminder Hours Before Appointment
                </Typography>
                <Stack spacing={1}>
                  {config.reminder_hours.map((hours, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 1 }}>
                      <TextField
                        type="number"
                        label={`Reminder ${index + 1}`}
                        value={hours}
                        onChange={(e) => handleReminderChange(index, e.target.value)}
                        InputProps={{ inputProps: { min: 1 } }}
                      />
                      <IconButton
                        onClick={() => removeReminder(index)}
                        disabled={config.reminder_hours.length <= 1}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  ))}
                  <Button
                    startIcon={<AddIcon />}
                    onClick={addReminder}
                    disabled={config.reminder_hours.length >= 5}
                  >
                    Add Reminder
                  </Button>
                </Stack>
              </Box>

              <Box sx={{ display: 'flex', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.allow_cancellation}
                      onChange={(e) => handleChange('allow_cancellation', e.target.checked)}
                    />
                  }
                  label="Allow Cancellation"
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={config.allow_rescheduling}
                      onChange={(e) => handleChange('allow_rescheduling', e.target.checked)}
                    />
                  }
                  label="Allow Rescheduling"
                />
              </Box>

              <Box>
                <Typography variant="h6">SMS Notifications</Typography>
                <Stack spacing={2}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.sms_notifications.enabled}
                        onChange={(e) => handleChange('sms_notifications', { ...config.sms_notifications, enabled: e.target.checked })}
                      />
                    }
                    label="Enable SMS Notifications"
                  />

                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.sms_notifications.include_cancel_link}
                        onChange={(e) => handleChange('sms_notifications', { ...config.sms_notifications, include_cancel_link: e.target.checked })}
                      />
                    }
                    label="Include Cancellation Link"
                  />

                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.sms_notifications.include_reschedule_link}
                        onChange={(e) => handleChange('sms_notifications', { ...config.sms_notifications, include_reschedule_link: e.target.checked })}
                      />
                    }
                    label="Include Reschedule Link"
                  />

                  <TextField
                    fullWidth
                    label="Confirmation Message"
                    value={config.sms_notifications.confirmation_message}
                    onChange={(e) => handleChange('sms_notifications', { ...config.sms_notifications, confirmation_message: e.target.value })}
                  />

                  <TextField
                    fullWidth
                    label="Reminder Message"
                    value={config.sms_notifications.reminder_message}
                    onChange={(e) => handleChange('sms_notifications', { ...config.sms_notifications, reminder_message: e.target.value })}
                  />

                  <TextField
                    fullWidth
                    label="Cancellation Message"
                    value={config.sms_notifications.cancellation_message}
                    onChange={(e) => handleChange('sms_notifications', { ...config.sms_notifications, cancellation_message: e.target.value })}
                  />

                  <TextField
                    fullWidth
                    label="Reschedule Message"
                    value={config.sms_notifications.reschedule_message}
                    onChange={(e) => handleChange('sms_notifications', { ...config.sms_notifications, reschedule_message: e.target.value })}
                  />

                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="outlined"
                      onClick={testSMSNotifications}
                      disabled={testingSMS || !config.sms_notifications.enabled}
                      startIcon={testingSMS ? <CircularProgress size={20} /> : <SendIcon />}
                    >
                      Test SMS Messages
                    </Button>
                    <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 1 }}>
                      This will send test messages to your business phone number
                    </Typography>
                  </Box>
                </Stack>
              </Box>
            </Stack>
          </CardContent>
        </Card>

        {error && (
          <Alert severity="error">{error}</Alert>
        )}
      </Stack>
    </Box>
  );
};

export default CalendlySetup;
