import React from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepButton,
  Button,
} from '@mui/material';
import { useWizard } from '../../contexts/WizardContext';
import { WizardStep } from '../../types/wizard';

const stepLabels: Record<WizardStep, string> = {
  intro: 'Introduction',
  services: 'Services',
  phone: 'Phone Setup',
  voice: 'Voice Setup',
  workflow: 'Workflow',
  calendly: 'Calendly',
  testing: 'Testing',
  deployment: 'Deployment',
  account: 'Account'
};

const stepOrder: readonly WizardStep[] = [
  'intro',
  'services',
  'phone',
  'voice',
  'workflow',
  'calendly',
  'testing',
  'deployment',
] as const;

const WizardNavigation: React.FC = () => {
  const { state, dispatch } = useWizard();
  const currentStepIndex = stepOrder.indexOf(state.currentStep as WizardStep);

  const handleNext = () => {
    if (currentStepIndex < stepOrder.length - 1) {
      dispatch({ type: 'SET_STEP', step: stepOrder[currentStepIndex + 1] });
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      dispatch({ type: 'SET_STEP', step: stepOrder[currentStepIndex - 1] });
    }
  };

  const handleStepClick = (step: WizardStep) => {
    dispatch({ type: 'SET_STEP', step });
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Stepper activeStep={currentStepIndex} alternativeLabel>
        {stepOrder.map((step) => (
          <Step key={step}>
            <StepButton onClick={() => handleStepClick(step)}>
              <StepLabel>{stepLabels[step]}</StepLabel>
            </StepButton>
          </Step>
        ))}
      </Stepper>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        <Button
          color="inherit"
          disabled={currentStepIndex === 0}
          onClick={handleBack}
        >
          Back
        </Button>
        <Button
          variant="contained"
          disabled={currentStepIndex === stepOrder.length - 1}
          onClick={handleNext}
        >
          Next
        </Button>
      </Box>
    </Box>
  );
};

export default WizardNavigation;
