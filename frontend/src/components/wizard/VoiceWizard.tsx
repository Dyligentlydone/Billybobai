import {
  Stepper,
  Step,
  StepLabel,
  Paper,
  Box,
  Button,
  Typography,
  Container,
} from '@mui/material';
import { useWizardStep } from '../../contexts/WizardContext';
import { WizardStep, VoicePersonalizationSettings } from '../../types/wizard';
import { AccountConfig } from './steps/AccountConfig';
import { PhoneSetup } from './steps/PhoneSetup';
import { WorkflowSetup } from './steps/WorkflowSetup';
import { TestingSetup } from './steps/TestingSetup';
import { DeploySetup } from './steps/DeploySetup';
import { VoicePersonalization } from '../voice/VoicePersonalization';
import { useWizard } from '../../contexts/WizardContext';

const defaultVoiceSettings: VoicePersonalizationSettings = {
  voice: {
    type: 'basic',
    gender: 'male',
    accent: 'American',
    name: 'Matthew',
    provider: 'twilio'
  },
  ssml: {
    rate: 'medium',
    pitch: 'medium',
    volume: 'medium',
    emphasis: 'moderate',
    breakTime: 0
  }
} as const;

const steps: Array<{ id: WizardStep; label: string; description: string }> = [
  {
    id: 'intro',
    label: 'Welcome',
    description: 'Set up your automated voice response system',
  },
  {
    id: 'account',
    label: 'Connect Services',
    description: 'Configure your Twilio, OpenAI, and Zendesk integrations',
  },
  {
    id: 'phone',
    label: 'Phone Setup',
    description: 'Set up your phone numbers and call handling',
  },
  {
    id: 'voice',
    label: 'Voice Settings',
    description: 'Personalize your voice response system',
  },
  {
    id: 'workflow',
    label: 'Workflow',
    description: 'Design your voicemail workflow',
  },
  {
    id: 'testing',
    label: 'Testing',
    description: 'Test your configuration',
  },
  {
    id: 'deploy',
    label: 'Deploy',
    description: 'Review and launch your system',
  },
];

interface VoiceWizardProps {
  onComplete?: (config: any) => void;
  onCancel?: () => void;
}

export function VoiceWizard({ onComplete, onCancel }: VoiceWizardProps) {
  const { currentStep, goToStep } = useWizardStep();
  const { state, dispatch } = useWizard();

  const activeStep = steps.findIndex(step => step.id === currentStep);

  const handleNext = () => {
    const nextStep = steps[activeStep + 1];
    if (nextStep) {
      goToStep(nextStep.id);
    } else if (onComplete) {
      onComplete(state);
    }
  };

  const handleBack = () => {
    const prevStep = steps[activeStep - 1];
    if (prevStep) {
      goToStep(prevStep.id);
    } else if (onCancel) {
      onCancel();
    }
  };

  const handleVoiceSettingsChange = (settings: VoicePersonalizationSettings) => {
    dispatch({ type: 'UPDATE_VOICE', voiceSettings: settings });
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 'intro':
        return (
          <Box>
            <Typography variant="h5" gutterBottom>
              Welcome to the Voice Automation Wizard
            </Typography>
            <Typography paragraph>
              This wizard will help you set up a voice automation workflow.
              We'll guide you through configuring your accounts, phone numbers,
              voice settings, and workflow rules.
            </Typography>
          </Box>
        );
      case 'account':
        return <AccountConfig />;
      case 'phone':
        return <PhoneSetup />;
      case 'voice':
        const accountSid = state.services.twilio.accountSid;
        const authToken = state.services.twilio.authToken;
        const twilioConfig = accountSid && authToken ? {
          accountSid,
          authToken
        } : undefined;
        return (
          <VoicePersonalization
            settings={state.voiceSettings || defaultVoiceSettings}
            onSettingsChange={handleVoiceSettingsChange}
            twilioConfig={twilioConfig}
          />
        );
      case 'workflow':
        return <WorkflowSetup />;
      case 'testing':
        return <TestingSetup />;
      case 'deploy':
        return <DeploySetup />;
      default:
        return null;
    }
  };

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((step) => (
            <Step key={step.id}>
              <StepLabel>{step.label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderStepContent()}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            onClick={handleBack}
            variant="outlined"
            disabled={activeStep === 0}
          >
            {activeStep === 0 ? 'Cancel' : 'Back'}
          </Button>
          <Button
            onClick={handleNext}
            variant="contained"
            color="primary"
          >
            {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}
