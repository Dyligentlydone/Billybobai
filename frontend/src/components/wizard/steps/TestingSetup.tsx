import {
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  IconButton,
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { useWizard } from '../../../contexts/WizardContext';

export function TestingSetup() {
  const { state, dispatch } = useWizard();

  const handleAddScenario = () => {
    dispatch({
      type: 'UPDATE_TESTING',
      testing: {
        scenarios: [
          ...state.testing.scenarios,
          { name: '', input: '', expectedOutput: '' },
        ],
      },
    });
  };

  const handleScenarioChange = (index: number, field: string, value: string) => {
    const updatedScenarios = [...state.testing.scenarios];
    updatedScenarios[index] = {
      ...updatedScenarios[index],
      [field]: value,
    };

    dispatch({
      type: 'UPDATE_TESTING',
      testing: {
        scenarios: updatedScenarios,
      },
    });
  };

  const handleDeleteScenario = (index: number) => {
    const updatedScenarios = state.testing.scenarios.filter((_, i) => i !== index);
    dispatch({
      type: 'UPDATE_TESTING',
      testing: {
        scenarios: updatedScenarios,
      },
    });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Testing Configuration
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Create test scenarios to validate your voice automation system's behavior.
      </Typography>

      {state.testing.scenarios.map((scenario, index) => (
        <Card key={index} sx={{ mb: 2 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="Scenario Name"
                  value={scenario.name}
                  onChange={(e) => handleScenarioChange(index, 'name', e.target.value)}
                  placeholder="e.g., Urgent Support Request"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Test Input"
                  value={scenario.input}
                  onChange={(e) => handleScenarioChange(index, 'input', e.target.value)}
                  placeholder="Sample voicemail content..."
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Expected Output"
                  value={scenario.expectedOutput}
                  onChange={(e) => handleScenarioChange(index, 'expectedOutput', e.target.value)}
                  placeholder="Expected system response..."
                />
              </Grid>
              <Grid item xs={12} md={1}>
                <IconButton
                  onClick={() => handleDeleteScenario(index)}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      ))}

      <Button
        variant="outlined"
        onClick={handleAddScenario}
        sx={{ mt: 2 }}
      >
        Add Test Scenario
      </Button>
    </Box>
  );
}
