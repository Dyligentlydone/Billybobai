import { useState } from 'react';
import { Tab } from '@headlessui/react';
import { PhoneSetup } from '../components/wizard/steps/PhoneSetup';
import { WorkflowSetup } from '../components/wizard/steps/WorkflowSetup';
import { TestingSetup } from '../components/wizard/steps/TestingSetup';
import { DeploySetup } from '../components/wizard/steps/DeploySetup';
import SuccessScreen from '../components/setup/SuccessScreen';

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

interface SetupData {
  businessName: string;
  businessId: string;
  phoneNumber: string;
  twilioAccountSid: string;
  twilioAuthToken: string;
  openaiApiKey: string;
  promptTemplate: string;
}

export default function Setup() {
  const [currentStep, setCurrentStep] = useState(0);
  const [setupComplete, setSetupComplete] = useState(false);
  const [setupData, setSetupData] = useState<SetupData>({
    businessName: '',
    businessId: '',
    phoneNumber: '',
    twilioAccountSid: '',
    twilioAuthToken: '',
    openaiApiKey: '',
    promptTemplate: ''
  });

  const steps = [
    { name: 'Phone Setup', component: PhoneSetup },
    { name: 'Workflow', component: WorkflowSetup },
    { name: 'Testing', component: TestingSetup },
    { name: 'Deploy', component: DeploySetup }
  ];

  const handleStepComplete = (stepData: Partial<SetupData>) => {
    setSetupData(prev => ({ ...prev, ...stepData }));
    
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setSetupComplete(true);
    }
  };

  if (setupComplete) {
    return (
      <SuccessScreen
        businessName={setupData.businessName}
        businessId={setupData.businessId}
        phoneNumber={setupData.phoneNumber}
      />
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">SMS Automation Setup</h1>
          <p className="mt-2 text-sm text-gray-700">
            Configure your SMS automation workflow in a few simple steps.
          </p>
        </div>
      </div>

      <Tab.Group selectedIndex={currentStep} onChange={setCurrentStep}>
        <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-8">
          {steps.map((step, index) => (
            <Tab
              key={step.name}
              disabled={index > currentStep}
              className={({ selected }) =>
                classNames(
                  'w-full rounded-lg py-2.5 text-sm font-medium leading-5',
                  'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2',
                  selected
                    ? 'bg-white text-blue-700 shadow'
                    : index <= currentStep
                    ? 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
                    : 'text-blue-400 cursor-not-allowed'
                )
              }
            >
              {step.name}
            </Tab>
          ))}
        </Tab.List>
        <Tab.Panels>
          {steps.map((step, idx) => (
            <Tab.Panel key={idx}>
              <step.component
                onComplete={handleStepComplete}
                setupData={setupData}
              />
            </Tab.Panel>
          ))}
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}
