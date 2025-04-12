import {
  Box,
  Typography,
  TextField,
  Button,
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
          { name: '', input: '', expectedResponse: '' },
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
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
              <Box sx={{ flex: '0 0 calc(25% - 12px)' }}>
                <TextField
                  fullWidth
                  label="Scenario Name"
                  value={scenario.name}
                  onChange={(e) => handleScenarioChange(index, 'name', e.target.value)}
                  placeholder="e.g., Urgent Support Request"
                />
              </Box>
              <Box sx={{ flex: '0 0 calc(33% - 12px)' }}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Sample Input"
                  value={scenario.input}
                  onChange={(e) => handleScenarioChange(index, 'input', e.target.value)}
                  placeholder="Sample voicemail content..."
                />
              </Box>
              <Box sx={{ flex: '0 0 calc(33% - 12px)' }}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Expected Response"
                  value={scenario.expectedResponse}
                  onChange={(e) => handleScenarioChange(index, 'expectedResponse', e.target.value)}
                  placeholder="Expected system response..."
                />
              </Box>
              <Box sx={{ flex: '0 0 calc(9% - 12px)' }}>
                <IconButton
                  onClick={() => handleDeleteScenario(index)}
                  color="error"
                  aria-label="Delete scenario"
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            </Box>
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
