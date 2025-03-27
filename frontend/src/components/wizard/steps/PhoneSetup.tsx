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
} from '@mui/material';
import { useWizard } from '../../../contexts/WizardContext';

export function PhoneSetup() {
  const { state, dispatch } = useWizard();

  const handleAddPhoneNumber = () => {
    dispatch({
      type: 'UPDATE_PHONE',
      phone: {
        phoneNumbers: [
          ...state.phone.phoneNumbers,
          { number: '', greeting: '', voicemail: true },
        ],
      },
    });
  };

  const handlePhoneNumberChange = (index: number, field: string, value: string | boolean) => {
    const updatedNumbers = [...state.phone.phoneNumbers];
    updatedNumbers[index] = {
      ...updatedNumbers[index],
      [field]: value,
    };

    dispatch({
      type: 'UPDATE_PHONE',
      phone: {
        phoneNumbers: updatedNumbers,
      },
    });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Phone Number Configuration
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Add and configure the phone numbers you want to use with your voice automation system.
      </Typography>

      {state.phone.phoneNumbers.map((phone, index) => (
        <Card key={index} sx={{ mb: 2 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Phone Number"
                  value={phone.number}
                  onChange={(e) => handlePhoneNumberChange(index, 'number', e.target.value)}
                  placeholder="+1234567890"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Greeting Message"
                  value={phone.greeting}
                  onChange={(e) => handlePhoneNumberChange(index, 'greeting', e.target.value)}
                  placeholder="Welcome to our service..."
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={phone.voicemail}
                      onChange={(e) => handlePhoneNumberChange(index, 'voicemail', e.target.checked)}
                    />
                  }
                  label="Enable Voicemail"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      ))}

      <Button
        variant="outlined"
        onClick={handleAddPhoneNumber}
        sx={{ mt: 2 }}
      >
        Add Phone Number
      </Button>
    </Box>
  );
}
