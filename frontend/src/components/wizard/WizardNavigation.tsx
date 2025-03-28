import React from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepButton,
  Button,
  Typography,
} from '@mui/material';
import { useWizardContext } from '../../contexts/WizardContext';
import { wizardSteps } from './steps';
import { WizardStep } from '../../types/wizard';

const stepOrder: WizardStep[] = [
  'intro',
  'services',
  'phone',
  'voice',
  'workflow',
  'calendly',
  'testing',
  'deployment',
];

const WizardNavigation: React.FC = () => {
  const { state, dispatch } = useWizardContext();
  const currentStepIndex = stepOrder.indexOf(state.currentStep);

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
              <StepLabel>
                <Typography variant="caption">
                  {wizardSteps[step].title}
                </Typography>
              </StepLabel>
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
