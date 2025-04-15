import React, { createContext, useContext, useReducer } from 'react';

export interface CalendlyConfig {
  enabled: boolean;
  access_token: string;
  user_uri: string;
  webhook_uri?: string;
  default_event_type: string;
  reminder_hours: number[];
  allow_cancellation: boolean;
  allow_rescheduling: boolean;
  booking_window_days: number;
  min_notice_hours: number;
  sms_notifications: SMSNotificationSettings;
}

export interface SMSNotificationSettings {
  enabled: boolean;
  include_cancel_link: boolean;
  include_reschedule_link: boolean;
  confirmation_message: string;
  reminder_message: string;
  cancellation_message: string;
  reschedule_message: string;
}

export interface WizardState {
  businessId: number;
  currentStep: string;
  services: {
    twilio: {
      accountSid: string;
      authToken: string;
      isValid: boolean;
    };
    openai: {
      apiKey: string;
      isValid: boolean;
    };
  };
  phone: {
    phoneNumbers: any[];
  };
  voiceSettings: {
    voice: {
      type: string;
      gender: string;
      accent: string;
      name: string;
      provider: string;
    };
    ssml: {
      rate: string;
      pitch: string;
      volume: string;
      emphasis: string;
      breakTime: number;
    };
  };
  workflow: {
    intentAnalysis: {
      prompt: string;
    };
    responseRules: any[];
  };
  testing: {
    scenarios: any[];
  };
  deployment: {
    name: string;
    description: string;
  };
  calendly: CalendlyConfig;
}

type WizardAction = {
  type: 'SET_STEP';
  step: string;
} | {
  type: 'UPDATE_SERVICES';
  services: {
    twilio?: {
      accountSid: string;
      authToken: string;
      isValid: boolean;
    };
    openai?: {
      apiKey: string;
      isValid: boolean;
    };
  };
} | {
  type: 'UPDATE_PHONE';
  phone: {
    phoneNumbers: any[];
  };
} | {
  type: 'UPDATE_VOICE';
  voiceSettings: {
    voice: {
      type: string;
      gender: string;
      accent: string;
      name: string;
      provider: string;
    };
    ssml: {
      rate: string;
      pitch: string;
      volume: string;
      emphasis: string;
      breakTime: number;
    };
  };
} | {
  type: 'UPDATE_WORKFLOW';
  workflow: {
    intentAnalysis: {
      prompt: string;
    };
    responseRules: any[];
  };
} | {
  type: 'UPDATE_TESTING';
  testing: {
    scenarios: any[];
  };
} | {
  type: 'UPDATE_DEPLOYMENT';
  deployment: {
    name: string;
    description: string;
  };
} | {
  type: 'UPDATE_CALENDLY';
  calendly: CalendlyConfig;
};

const defaultVoiceSettings = {
  voice: {
    type: 'basic',
    gender: 'female',
    accent: 'American',
    name: 'woman',
    provider: 'twilio'
  },
  ssml: {
    rate: 'medium',
    pitch: 'medium',
    volume: 'medium',
    emphasis: 'none',
    breakTime: 500
  }
};

const initialState: WizardState = {
  businessId: 0,
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
  calendly: {
    enabled: false,
    access_token: '',
    user_uri: '',
    default_event_type: '',
    reminder_hours: [24, 1],
    allow_cancellation: true,
    allow_rescheduling: true,
    booking_window_days: 14,
    min_notice_hours: 1,
    sms_notifications: {
      enabled: false,
      include_cancel_link: false,
      include_reschedule_link: false,
      confirmation_message: '',
      reminder_message: '',
      cancellation_message: '',
      reschedule_message: '',
    },
  }
};

const wizardReducer = (state: WizardState, action: WizardAction): WizardState => {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, currentStep: action.step };
    case 'UPDATE_SERVICES':
      return { ...state, services: { ...state.services, ...action.services } };
    case 'UPDATE_PHONE':
      return { ...state, phone: { ...state.phone, ...action.phone } };
    case 'UPDATE_VOICE':
      return { ...state, voiceSettings: action.voiceSettings };
    case 'UPDATE_WORKFLOW':
      return { ...state, workflow: { ...state.workflow, ...action.workflow } };
    case 'UPDATE_TESTING':
      return { ...state, testing: { ...state.testing, ...action.testing } };
    case 'UPDATE_DEPLOYMENT':
      return { ...state, deployment: { ...state.deployment, ...action.deployment } };
    case 'UPDATE_CALENDLY':
      return { ...state, calendly: action.calendly };
    default:
      return state;
  }
};

interface WizardContextType {
  state: WizardState;
  dispatch: React.Dispatch<WizardAction>;
  updateState: (payload: Partial<WizardState>) => void;
}

const WizardContext = createContext<WizardContextType | null>(null);

export const WizardProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(wizardReducer, initialState);

  const updateState = (payload: Partial<WizardState>) => {
    if (payload.services) {
      dispatch({ type: 'UPDATE_SERVICES', services: payload.services });
    }
    if (payload.phone) {
      dispatch({ type: 'UPDATE_PHONE', phone: payload.phone });
    }
    if (payload.voiceSettings) {
      dispatch({ type: 'UPDATE_VOICE', voiceSettings: payload.voiceSettings });
    }
    if (payload.workflow) {
      dispatch({ type: 'UPDATE_WORKFLOW', workflow: payload.workflow });
    }
    if (payload.testing) {
      dispatch({ type: 'UPDATE_TESTING', testing: payload.testing });
    }
    if (payload.deployment) {
      dispatch({ type: 'UPDATE_DEPLOYMENT', deployment: payload.deployment });
    }
    if (payload.calendly) {
      dispatch({ type: 'UPDATE_CALENDLY', calendly: payload.calendly });
    }
  };

  return (
    <WizardContext.Provider value={{ state, dispatch, updateState }}>
      {children}
    </WizardContext.Provider>
  );
};

export const useWizard = () => {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error('useWizard must be used within a WizardProvider');
  }
  return context;
};

export function useWizardStep() {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error('useWizardStep must be used within a WizardProvider');
  }

  const { state, dispatch } = context;

  const goToStep = (stepId: string) => {
    dispatch({ type: 'SET_STEP', step: stepId });
  };

  return {
    currentStep: state.currentStep,
    state,
    goToStep,
    updateState: context.updateState,
  };
}
