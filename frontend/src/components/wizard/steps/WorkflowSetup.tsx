import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { useWizard } from '../../../contexts/WizardContext';

interface ResponseRule {
  condition: string;
  response: string;
  action: string;
}

interface WorkflowData {
  intentAnalysis: {
    prompt: string;
  };
  responseRules: ResponseRule[];
}

export function WorkflowSetup() {
  const { state, dispatch } = useWizard();

  const handleAddRule = () => {
    dispatch({
      type: 'UPDATE_WORKFLOW',
      workflow: {
        ...state.workflow,
        intentAnalysis: state.workflow.intentAnalysis || { prompt: '' },
        responseRules: [
          ...(state.workflow.responseRules || []),
          { condition: '', response: '', action: 'respond' },
        ],
      },
    });
  };

  const handleRuleChange = (index: number, field: keyof ResponseRule, value: string) => {
    const newRules = [...(state.workflow.responseRules || [])];
    if (!newRules[index]) {
      newRules[index] = { condition: '', response: '', action: '' };
    }
    newRules[index] = { ...newRules[index], [field]: value };

    dispatch({
      type: 'UPDATE_WORKFLOW',
      workflow: {
        ...state.workflow,
        responseRules: newRules,
      },
    });
  };

  const handleChange = (field: keyof WorkflowData, value: any) => {
    dispatch({
      type: 'UPDATE_WORKFLOW',
      workflow: {
        ...state.workflow,
        [field]: value,
      },
    });
  };

  const data: WorkflowData = {
    intentAnalysis: state.workflow.intentAnalysis || { prompt: '' },
    responseRules: state.workflow.responseRules || []
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
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
            <Box sx={{ flex: '0 0 calc(33% - 12px)' }}>
              <TextField
                fullWidth
                label="Intent Analysis Prompt"
                multiline
                rows={4}
                value={data.intentAnalysis.prompt}
                onChange={(e) => handleChange('intentAnalysis', { prompt: e.target.value })}
                placeholder="Enter prompt for intent analysis..."
              />
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Typography variant="h6" gutterBottom>
        Response Rules
      </Typography>

      {data.responseRules.map((rule, index) => (
        <Card key={index} sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
              <Box sx={{ flex: '0 0 calc(33% - 12px)' }}>
                <TextField
                  fullWidth
                  label="Condition"
                  value={rule.condition}
                  onChange={(e) => handleRuleChange(index, 'condition', e.target.value)}
                  placeholder="e.g., contains 'urgent'"
                />
              </Box>
              <Box sx={{ flex: '0 0 calc(33% - 12px)' }}>
                <TextField
                  fullWidth
                  label="Response"
                  value={rule.response}
                  onChange={(e) => handleRuleChange(index, 'response', e.target.value)}
                  placeholder="Custom response message..."
                />
              </Box>
              <Box sx={{ flex: '0 0 calc(33% - 12px)' }}>
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
              </Box>
            </Box>
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
