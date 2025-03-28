import React from 'react';
import { WizardStep } from '../../../types/wizard';
import IntroStep from './IntroStep';
import ServicesStep from './ServicesStep';
import PhoneStep from './PhoneStep';
import VoiceStep from './VoiceStep';
import WorkflowStep from './WorkflowStep';
import CalendlySetup from './CalendlySetup';
import TestingStep from './TestingStep';
import DeploymentStep from './DeploymentStep';

export const wizardSteps: Record<WizardStep, {
  title: string;
  description: string;
  component: React.FC;
  optional?: boolean;
}> = {
  intro: {
    title: 'Welcome',
    description: 'Set up your SMS automation workflow',
    component: IntroStep,
  },
  services: {
    title: 'Service Configuration',
    description: 'Configure your Twilio and OpenAI credentials',
    component: ServicesStep,
  },
  phone: {
    title: 'Phone Numbers',
    description: 'Set up your business phone numbers',
    component: PhoneStep,
  },
  calendly: {
    title: 'Appointment Booking',
    description: 'Configure Calendly integration for automated appointment scheduling (Optional)',
    component: CalendlySetup,
    optional: true,
  },
  workflow: {
    title: 'Workflow Configuration',
    description: 'Set up your automation workflow and responses',
    component: WorkflowStep,
  },
  testing: {
    title: 'Testing',
    description: 'Test your SMS automation setup',
    component: TestingStep,
  },
  deployment: {
    title: 'Deployment',
    description: 'Deploy your SMS automation workflow',
    component: DeploymentStep,
  }
};
