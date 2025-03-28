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
import { WizardStep } from '../../types/wizard';
import { AccountConfig } from './steps/AccountConfig';
import { PhoneSetup } from './steps/PhoneSetup';
import { WorkflowSetup } from './steps/WorkflowSetup';
import { TestingSetup } from './steps/TestingSetup';
import { DeploySetup } from './steps/DeploySetup';
import { VoicePersonalization } from '../voice/VoicePersonalization';
import { VoicePersonalizationSettings } from '../../types/voice';

const defaultVoiceSettings: VoicePersonalizationSettings = {
  voice: {
    type: 'neural',
    gender: 'female',
    accent: 'American',
    name: 'Sarah'
  },
  speech: {
    rate: 1.0,
    pitch: 0,
    emphasis: 'normal'
  },
  brand: {
    tone: 'professional',
    personality: ['helpful', 'friendly', 'efficient'],
    customPhrases: {
      greeting: ['Hello, thank you for calling'],
      confirmation: ['I understand', 'Let me help you with that'],
      farewell: ['Thank you for your time', 'Have a great day']
    },
    prosody: {
      wordEmphasis: true,
      naturalPauses: true,
      intonation: 'natural'
    }
  },
  timing: {
    responseDelay: 500,
    wordSpacing: 1.0,
    pauseDuration: {
      comma: 200,
      period: 500,
      question: 300
    }
  }
};

const steps: { id: WizardStep; label: string; description: string }[] = [
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
  const { currentStep, goToStep, updateState, state } = useWizardStep();
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
    updateState({
      ...state,
      voiceSettings: settings
    });
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 'intro':
        return (
          <Box textAlign="center" py={4}>
            <Typography variant="h4" gutterBottom>
              Welcome to Voice Automation Setup
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              This wizard will guide you through setting up your automated voice response system.
              We'll help you connect your services, configure phone numbers, design your workflow,
              and test everything before going live.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleNext}
            >
              Begin Setup
            </Button>
          </Box>
        );
      case 'account':
        return <AccountConfig />;
      case 'phone':
        return <PhoneSetup />;
      case 'voice':
        return (
          <VoicePersonalization
            settings={state.voiceSettings || defaultVoiceSettings}
            onChange={handleVoiceSettingsChange}
            title="Voice Personalization"
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
