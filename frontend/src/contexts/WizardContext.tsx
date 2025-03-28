import React, { createContext, useContext, useReducer } from 'react';
import { WizardState, WizardAction, WizardStep, VoicePersonalizationSettings } from '../types/wizard';

const defaultVoiceSettings: VoicePersonalizationSettings = {
  voice: {
    type: 'basic',
    gender: 'female',
    accent: 'American',
    name: 'woman',
    provider: 'twilio'
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
  voiceSettings: defaultVoiceSettings,
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
    case 'UPDATE_VOICE':
      return {
        ...state,
        voiceSettings: action.voiceSettings,
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
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error('useWizardStep must be used within a WizardProvider');
  }

  const { state, dispatch } = context;

  const goToStep = (stepId: WizardStep) => {
    dispatch({ type: 'SET_STEP', step: stepId });
  };

  const updateState = (newState: Partial<WizardState>) => {
    if (newState.services) {
      dispatch({ type: 'UPDATE_SERVICES', services: newState.services });
    }
    if (newState.phone) {
      dispatch({ type: 'UPDATE_PHONE', phone: newState.phone });
    }
    if (newState.voiceSettings) {
      dispatch({ type: 'UPDATE_VOICE', voiceSettings: newState.voiceSettings });
    }
    if (newState.workflow) {
      dispatch({ type: 'UPDATE_WORKFLOW', workflow: newState.workflow });
    }
    if (newState.testing) {
      dispatch({ type: 'UPDATE_TESTING', testing: newState.testing });
    }
    if (newState.deployment) {
      dispatch({ type: 'UPDATE_DEPLOYMENT', deployment: newState.deployment });
    }
  };

  return {
    currentStep: state.currentStep,
    state,
    goToStep,
    updateState,
  };
}
