import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Box,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { VoiceConfig } from '../../types/voice';
import { timezones } from '../../utils/timezones';

interface VoiceConfigWizardProps {
  onComplete: (config: VoiceConfig) => void;
  onCancel: () => void;
}

export const VoiceConfigWizard: React.FC<VoiceConfigWizardProps> = ({
  onComplete,
  onCancel,
}) => {
  const { control, handleSubmit } = useForm<VoiceConfig>({
    defaultValues: {
      business: {
        name: '',
        phone: '',
        timezone: 'America/New_York',
        greeting: 'Welcome to our business.',
      },
      integration: {
        twilio: {
          accountSid: '',
          authToken: '',
          phoneNumber: '',
        },
        openai: {
          apiKey: '',
          model: 'gpt-4',
          voiceId: 'nova',
        },
      },
      callFlow: {
        greeting: 'Thank you for calling. How can I assist you today?',
        mainMenu: {
          prompt: 'Please select from the following options:',
          options: [
            { digit: '1', description: 'Speak to an AI assistant', action: 'message' },
            { digit: '2', description: 'Leave a voicemail', action: 'voicemail' },
            { digit: '0', description: 'Transfer to operator', action: 'transfer' },
          ],
        },
        fallback: {
          message: 'I apologize, but I didn\'t understand that. Let me transfer you to someone who can help.',
          action: 'transfer',
        },
        businessHours: {
          enabled: true,
          timezone: 'America/New_York',
          hours: {
            Monday: { start: '09:00', end: '17:00' },
            Tuesday: { start: '09:00', end: '17:00' },
            Wednesday: { start: '09:00', end: '17:00' },
            Thursday: { start: '09:00', end: '17:00' },
            Friday: { start: '09:00', end: '17:00' },
          },
          outOfHoursMessage: 'We are currently closed. Please leave a message or call back during business hours.',
        },
        voicePreferences: {
          language: 'en-US',
          speed: 1,
          gender: 'female',
        },
      },
    },
  });

  const handleAddMenuOption = () => {
    // TODO: Implement adding menu options in next phase
    console.log('Adding menu option');
  };

  const onSubmit = async (data: VoiceConfig) => {
    try {
      onComplete(data);
    } catch (error) {
      console.error('Error saving voice configuration:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Business Configuration
          </Typography>
          <Box sx={{ display: 'grid', gap: 2 }}>
            <Controller
              name="business.name"
              control={control}
              rules={{ required: 'Business name is required' }}
              render={({ field, fieldState: { error } }) => (
                <TextField
                  {...field}
                  label="Business Name"
                  error={!!error}
                  helperText={error?.message}
                />
              )}
            />
            <Controller
              name="business.phone"
              control={control}
              rules={{ required: 'Phone number is required' }}
              render={({ field, fieldState: { error } }) => (
                <TextField
                  {...field}
                  label="Business Phone"
                  error={!!error}
                  helperText={error?.message}
                />
              )}
            />
            <Controller
              name="business.timezone"
              control={control}
              render={({ field }) => (
                <Select {...field} label="Timezone">
                  {timezones.map((timezone: string) => (
                    <MenuItem key={timezone} value={timezone}>
                      {timezone}
                    </MenuItem>
                  ))}
                </Select>
              )}
            />
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Integration Settings
          </Typography>
          <Box sx={{ display: 'grid', gap: 2 }}>
            <Controller
              name="integration.twilio.accountSid"
              control={control}
              rules={{ required: 'Twilio Account SID is required' }}
              render={({ field, fieldState: { error } }) => (
                <TextField
                  {...field}
                  label="Twilio Account SID"
                  error={!!error}
                  helperText={error?.message}
                />
              )}
            />
            <Controller
              name="integration.twilio.authToken"
              control={control}
              rules={{ required: 'Twilio Auth Token is required' }}
              render={({ field, fieldState: { error } }) => (
                <TextField
                  {...field}
                  type="password"
                  label="Twilio Auth Token"
                  error={!!error}
                  helperText={error?.message}
                />
              )}
            />
            <Controller
              name="integration.twilio.phoneNumber"
              control={control}
              rules={{ required: 'Twilio Phone Number is required' }}
              render={({ field, fieldState: { error } }) => (
                <TextField
                  {...field}
                  label="Twilio Phone Number"
                  error={!!error}
                  helperText={error?.message}
                />
              )}
            />
            <Controller
              name="integration.openai.apiKey"
              control={control}
              rules={{ required: 'OpenAI API Key is required' }}
              render={({ field, fieldState: { error } }) => (
                <TextField
                  {...field}
                  type="password"
                  label="OpenAI API Key"
                  error={!!error}
                  helperText={error?.message}
                />
              )}
            />
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Call Flow Configuration
          </Typography>
          <Box sx={{ display: 'grid', gap: 2 }}>
            <Controller
              name="callFlow.greeting"
              control={control}
              rules={{ required: 'Greeting message is required' }}
              render={({ field, fieldState: { error } }) => (
                <TextField
                  {...field}
                  multiline
                  rows={2}
                  label="Greeting Message"
                  error={!!error}
                  helperText={error?.message}
                />
              )}
            />
            
            <Typography variant="h6" gutterBottom>
              Menu Options
            </Typography>
            {/* Menu options will be rendered here */}
            
            <Button
              startIcon={<AddIcon />}
              onClick={handleAddMenuOption}
              variant="outlined"
            >
              Add Menu Option
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Business Hours
          </Typography>
          <Box sx={{ display: 'grid', gap: 2 }}>
            <Controller
              name="callFlow.businessHours.enabled"
              control={control}
              render={({ field }) => (
                <FormControlLabel
                  control={<Switch {...field} checked={field.value} />}
                  label="Enable Business Hours"
                />
              )}
            />
            {/* Business hours configuration will be rendered here */}
          </Box>
        </CardContent>
      </Card>

      <Box sx={{ mt: 2, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button onClick={onCancel} variant="outlined">
          Cancel
        </Button>
        <Button type="submit" variant="contained" color="primary">
          Save Configuration
        </Button>
      </Box>
    </form>
  );
};
