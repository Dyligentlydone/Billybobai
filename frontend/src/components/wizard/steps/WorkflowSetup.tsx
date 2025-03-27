import {
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { useWizard } from '../../../contexts/WizardContext';

export function WorkflowSetup() {
  const { state, dispatch } = useWizard();

  const handleAddRule = () => {
    dispatch({
      type: 'UPDATE_WORKFLOW',
      workflow: {
        responseRules: [
          ...state.workflow.responseRules,
          { condition: '', response: '', action: 'respond' },
        ],
      },
    });
  };

  const handleRuleChange = (index: number, field: string, value: string) => {
    const updatedRules = [...state.workflow.responseRules];
    updatedRules[index] = {
      ...updatedRules[index],
      [field]: value,
    };

    dispatch({
      type: 'UPDATE_WORKFLOW',
      workflow: {
        responseRules: updatedRules,
      },
    });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Workflow Configuration
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Design how your voice automation system should handle calls and respond to different scenarios.
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Intent Analysis
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="AI Prompt Template"
            value={state.workflow.intentAnalysis.prompt}
            onChange={(e) =>
              dispatch({
                type: 'UPDATE_WORKFLOW',
                workflow: {
                  intentAnalysis: {
                    prompt: e.target.value,
                  },
                },
              })
            }
            placeholder="You are an AI assistant analyzing customer voicemails..."
          />
        </CardContent>
      </Card>

      <Typography variant="h6" gutterBottom>
        Response Rules
      </Typography>

      {state.workflow.responseRules.map((rule, index) => (
        <Card key={index} sx={{ mb: 2 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Condition"
                  value={rule.condition}
                  onChange={(e) => handleRuleChange(index, 'condition', e.target.value)}
                  placeholder="e.g., contains 'urgent'"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Response"
                  value={rule.response}
                  onChange={(e) => handleRuleChange(index, 'response', e.target.value)}
                  placeholder="Custom response message..."
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Action</InputLabel>
                  <Select
                    value={rule.action}
                    onChange={(e) => handleRuleChange(index, 'action', e.target.value)}
                  >
                    <MenuItem value="respond">Send Response</MenuItem>
                    <MenuItem value="transfer">Transfer Call</MenuItem>
                    <MenuItem value="voicemail">Take Voicemail</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      ))}

      <Button
        variant="outlined"
        onClick={handleAddRule}
        sx={{ mt: 2 }}
      >
        Add Response Rule
      </Button>
    </Box>
  );
}
