import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import { useWizard } from '../../../contexts/WizardContext';

export function DeploySetup() {
  const { state } = useWizard();

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Review and Deploy
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Review your configuration before deploying your voice automation system.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Connections
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Twilio"
                    secondary={state.services.twilio.accountSid ? 'Connected' : 'Not configured'}
                  />
                  <Chip
                    label={state.services.twilio.isValid ? 'Valid' : 'Invalid'}
                    color={state.services.twilio.isValid ? 'success' : 'error'}
                    size="small"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="OpenAI"
                    secondary={state.services.openai.apiKey ? 'Connected' : 'Not configured'}
                  />
                  <Chip
                    label={state.services.openai.isValid ? 'Valid' : 'Invalid'}
                    color={state.services.openai.isValid ? 'success' : 'error'}
                    size="small"
                  />
                </ListItem>
                {state.services.zendesk?.enabled && (
                  <ListItem>
                    <ListItemText
                      primary="Zendesk"
                      secondary={state.services.zendesk.apiToken ? 'Connected' : 'Not configured'}
                    />
                    <Chip
                      label={state.services.zendesk.isValid ? 'Valid' : 'Invalid'}
                      color={state.services.zendesk.isValid ? 'success' : 'error'}
                      size="small"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Phone Numbers
              </Typography>
              <List>
                {state.phone.phoneNumbers.map((phone, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={phone.number}
                      secondary={`Voicemail ${phone.voicemail ? 'Enabled' : 'Disabled'}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Workflow Configuration
              </Typography>
              <Typography variant="subtitle2" gutterBottom>
                Response Rules:
              </Typography>
              <List>
                {state.workflow.responseRules.map((rule, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={`Rule ${index + 1}: ${rule.condition}`}
                      secondary={`Action: ${rule.action}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Scenarios
              </Typography>
              <List>
                {state.testing.scenarios.map((scenario, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={scenario.name}
                      secondary={`Input: ${scenario.input}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
