import { FC } from 'react';
import CalendlySetup from './CalendlySetup';
import { DeploySetup } from './DeploySetup';
import { TestingSetup } from './TestingSetup';
import { WorkflowSetup } from './WorkflowSetup';

export type WizardStep = 'calendly' | 'workflow' | 'testing' | 'deploy';

interface StepConfig {
  title: string;
  description: string;
  component: FC<{}>;
  optional?: boolean;
}

export const steps: Record<WizardStep, StepConfig> = {
  calendly: {
    title: 'Calendly Integration',
    description: 'Configure your Calendly integration settings',
    component: CalendlySetup,
    optional: true,
  },
  workflow: {
    title: 'Workflow Configuration',
    description: 'Set up your workflow rules and responses',
    component: WorkflowSetup,
  },
  testing: {
    title: 'Testing Scenarios',
    description: 'Create test scenarios for your workflow',
    component: TestingSetup,
  },
  deploy: {
    title: 'Deploy',
    description: 'Review and deploy your configuration',
    component: DeploySetup,
  },
};
