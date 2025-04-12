import {
  Box,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import { useWizard } from '../../../contexts/WizardContext';

interface ServiceStatus {
  accountSid?: string;
  apiKey?: string;
  authToken?: string;
  apiToken?: string;
  isValid?: boolean;
}

interface WizardState {
  services: {
    twilio: ServiceStatus;
    openai: ServiceStatus;
    zendesk?: ServiceStatus;
  };
  testing: {
    scenarios: Array<{
      name: string;
      input: string;
      expectedResponse: string;
    }>;
  };
}

export function DeploySetup() {
  const { state } = useWizard();

  const services = {
    twilio: state.services?.twilio || {},
    openai: state.services?.openai || {},
    zendesk: state.services?.zendesk,
  } as WizardState['services'];

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Deployment Review
      </Typography>
      <Typography variant="body1" gutterBottom>
        Review your configuration before deploying your voice automation system.
      </Typography>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        <Box sx={{ flex: '0 0 calc(50% - 12px)' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Twilio Configuration
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Account SID"
                    secondary={services?.twilio?.accountSid || 'Not configured'}
                  />
                  <Chip
                    label={services?.twilio?.isValid ? 'Valid' : 'Invalid'}
                    color={services?.twilio?.isValid ? 'success' : 'error'}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Box>

        <Box sx={{ flex: '0 0 calc(50% - 12px)' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                OpenAI Configuration
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="API Key"
                    secondary={services?.openai?.apiKey ? '********' : 'Not configured'}
                  />
                  <Chip
                    label={services?.openai?.isValid ? 'Valid' : 'Invalid'}
                    color={services?.openai?.isValid ? 'success' : 'error'}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Box>

        {services?.zendesk && (
          <Box sx={{ flex: '1 1 100%' }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Zendesk Integration
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="API Token"
                      secondary={services?.zendesk?.apiToken ? '********' : 'Not configured'}
                    />
                    <Chip
                      label={services?.zendesk?.isValid ? 'Valid' : 'Invalid'}
                      color={services?.zendesk?.isValid ? 'success' : 'error'}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Box>
        )}

        <Box sx={{ flex: '1 1 100%' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Testing Configuration
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Test Scenarios"
                    secondary={`${state.testing?.scenarios?.length || 0} scenarios configured`}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
}
