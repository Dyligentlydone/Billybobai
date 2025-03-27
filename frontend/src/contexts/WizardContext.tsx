import React, { createContext, useContext, useReducer } from 'react';
import { WizardState, WizardAction, WizardStep } from '../types/wizard';

const initialState: WizardState = {
  currentStep: 'intro',
  services: {
    twilio: {
      accountSid: '',
      authToken: '',
      isValid: false,
    },
    openai: {
      apiKey: '',
      isValid: false,
    },
  },
  phone: {
    phoneNumbers: [],
  },
  workflow: {
    intentAnalysis: {
      prompt: '',
    },
    responseRules: [],
  },
  testing: {
    scenarios: [],
  },
  deployment: {
    name: '',
    description: '',
  },
};

function wizardReducer(state: WizardState, action: WizardAction): WizardState {
  switch (action.type) {
    case 'SET_STEP':
      return {
        ...state,
        currentStep: action.step,
      };
    case 'UPDATE_SERVICES':
      return {
        ...state,
        services: {
          ...state.services,
          ...action.services,
        },
      };
    case 'UPDATE_PHONE':
      return {
        ...state,
        phone: {
          ...state.phone,
          ...action.phone,
        },
      };
    case 'UPDATE_WORKFLOW':
      return {
        ...state,
        workflow: {
          ...state.workflow,
          ...action.workflow,
        },
      };
    case 'UPDATE_TESTING':
      return {
        ...state,
        testing: {
          ...state.testing,
          ...action.testing,
        },
      };
    case 'UPDATE_DEPLOYMENT':
      return {
        ...state,
        deployment: {
          ...state.deployment,
          ...action.deployment,
        },
      };
    default:
      return state;
  }
}

const WizardContext = createContext<{
  state: WizardState;
  dispatch: React.Dispatch<WizardAction>;
} | null>(null);

export function WizardProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(wizardReducer, initialState);

  return (
    <WizardContext.Provider value={{ state, dispatch }}>
      {children}
    </WizardContext.Provider>
  );
}

export function useWizard() {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error('useWizard must be used within a WizardProvider');
  }
  return context;
}

export function useWizardStep() {
  const { state, dispatch } = useWizard();
  
  const goToStep = (stepId: WizardStep) => {
    dispatch({ type: 'SET_STEP', step: stepId });
  };

  return {
    currentStep: state.currentStep,
    goToStep,
  };
}
