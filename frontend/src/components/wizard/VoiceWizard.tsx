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
import { 
  WizardStep, 
  VoicePersonalizationSettings
} from '../../types/wizard';
import { AccountConfig } from './steps/AccountConfig';
import { PhoneSetup } from './steps/PhoneSetup';
import { WorkflowSetup } from './steps/WorkflowSetup';
import { TestingSetup } from './steps/TestingSetup';
import { DeploySetup } from './steps/DeploySetup';
import { VoicePersonalization } from '../voice/VoicePersonalization';
import { useWizard } from '../../contexts/WizardContext';

const defaultVoiceSettings = {
  voice: {
    type: 'basic',
    gender: 'male',
    accent: 'American',
    name: 'Matthew',
    provider: 'twilio'
  },
  ssml: {
    rate: 'x-slow',
    pitch: 'medium',
    volume: 'medium',
    emphasis: 'moderate',
    breakTime: 0
  }
} as VoicePersonalizationSettings;

const steps: Array<{ id: WizardStep; label: string; description: string }> = [
  {
    id: 'intro',
    label: 'Introduction',
    description: 'Welcome to the voice automation setup wizard'
  },
  {
    id: 'services',
    label: 'Services',
    description: 'Configure your Twilio and OpenAI credentials'
  },
  {
    id: 'phone',
    label: 'Phone Setup',
    description: 'Set up your phone numbers and voicemail'
  },
  {
    id: 'voice',
    label: 'Voice Settings',
    description: 'Customize the voice and speech settings'
  },
  {
    id: 'workflow',
    label: 'Workflow',
    description: 'Configure your call handling workflow'
  },
  {
    id: 'testing',
    label: 'Testing',
    description: 'Test your voice automation setup'
  },
  {
    id: 'deployment',
    label: 'Deploy',
    description: 'Deploy your voice automation'
  }
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
      case 'services':
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
        const voiceSettings = (state.voiceSettings || defaultVoiceSettings) as VoicePersonalizationSettings;
        return (
          <VoicePersonalization
            settings={voiceSettings}
            onSettingsChange={handleVoiceSettingsChange}
            twilioConfig={twilioConfig}
          />
        );
      case 'workflow':
        return <WorkflowSetup />;
      case 'testing':
        return <TestingSetup />;
      case 'deployment':
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
