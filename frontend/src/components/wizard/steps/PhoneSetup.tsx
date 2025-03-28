import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  FormControlLabel,
  Switch,
  Card,
  CardContent,
  Alert,
} from '@mui/material';

interface Props {
  onComplete: (data: any) => void;
  setupData: any;
}

export const PhoneSetup: React.FC<Props> = ({ onComplete, setupData }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    businessName: setupData.businessName || '',
    phoneNumber: setupData.phoneNumber || '',
    greeting: '',
    voicemail: true
  });

  const handleChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.type === 'checkbox' ? event.target.checked : event.target.value
    }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError('');

      // Create business record
      const { data } = await axios.post('/api/businesses', {
        name: formData.businessName,
        phoneNumber: formData.phoneNumber,
        greeting: formData.greeting,
        voicemail: formData.voicemail
      });

      // Move to next step with business data
      onComplete({
        businessName: formData.businessName,
        businessId: data.id,
        phoneNumber: formData.phoneNumber
      });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create business');
    } finally {
      setLoading(false);
    }
  };

  const gridItemProps = {
    item: true,
    xs: 12
  } as const;

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Business Setup
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Configure your business information and phone number for the SMS automation system.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid {...gridItemProps}>
              <TextField
                required
                fullWidth
                label="Business Name"
                value={formData.businessName}
                onChange={handleChange('businessName')}
                placeholder="Your Business Name"
              />
            </Grid>
            <Grid {...gridItemProps}>
              <TextField
                required
                fullWidth
                label="Phone Number"
                value={formData.phoneNumber}
                onChange={handleChange('phoneNumber')}
                placeholder="+1234567890"
                helperText="This is the number that will be used for SMS communications"
              />
            </Grid>
            <Grid {...gridItemProps}>
              <TextField
                fullWidth
                label="Default Greeting"
                value={formData.greeting}
                onChange={handleChange('greeting')}
                placeholder="Welcome! How can we help you today?"
                multiline
                rows={2}
              />
            </Grid>
            <Grid {...gridItemProps}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.voicemail}
                    onChange={handleChange('voicemail')}
                  />
                }
                label="Enable Automated Responses"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={!formData.businessName || !formData.phoneNumber || loading}
        >
          {loading ? 'Creating...' : 'Continue'}
        </Button>
      </Box>
    </Box>
  );
};
