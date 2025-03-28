export type WizardStep = 'intro' | 'account' | 'phone' | 'voice' | 'workflow' | 'testing' | 'deploy';

interface ServiceConfig {
  isValid: boolean;
  error?: string;
}

export interface TwilioConfig extends ServiceConfig {
  accountSid: string;
  authToken: string;
}

export interface OpenAIConfig extends ServiceConfig {
  apiKey: string;
}

export interface ZendeskConfig extends ServiceConfig {
  enabled: boolean;
  apiToken?: string;
  subdomain?: string;
}

export interface PhoneConfig {
  number: string;
  greeting: string;
  voicemail: boolean;
}

export interface ResponseRule {
  condition: string;
  response: string;
  action: 'respond' | 'transfer' | 'voicemail';
}

export interface TestScenario {
  name: string;
  input: string;
  expectedOutput: string;
}

export interface VoicePersonalizationSettings {
  voice: {
    type: 'neural' | 'standard';
    gender: 'male' | 'female';
    accent: string;
    name: string;
  };
  speech: {
    rate: number;  // 0.5 to 2.0
    pitch: number; // -20 to 20
    emphasis: 'reduced' | 'normal' | 'enhanced';
  };
  brand: {
    tone: 'professional' | 'friendly' | 'casual' | 'formal';
    personality: string[];
    customPhrases: {
      greeting: string[];
      confirmation: string[];
      farewell: string[];
    };
    prosody: {
      wordEmphasis: boolean;
      naturalPauses: boolean;
      intonation: 'natural' | 'expressive' | 'controlled';
    };
  };
  timing: {
    responseDelay: number;  // milliseconds
    wordSpacing: number;    // 0.8 to 1.2
    pauseDuration: {
      comma: number;        // milliseconds
      period: number;
      question: number;
    };
  };
}

export interface WizardState {
  currentStep: WizardStep;
  services: {
    twilio: TwilioConfig;
    openai: OpenAIConfig;
    zendesk?: ZendeskConfig;
  };
  phone: {
    phoneNumbers: PhoneConfig[];
  };
  voiceSettings?: VoicePersonalizationSettings;
  workflow: {
    intentAnalysis: {
      prompt: string;
    };
    responseRules: ResponseRule[];
  };
  testing: {
    scenarios: TestScenario[];
  };
  deployment: {
    name: string;
    description: string;
  };
}

export type WizardAction =
  | { type: 'SET_STEP'; step: WizardStep }
  | { type: 'COMPLETE_STEP'; step: WizardStep }
  | { type: 'UPDATE_SERVICES'; services: Partial<WizardState['services']> }
  | { type: 'UPDATE_PHONE'; phone: Partial<WizardState['phone']> }
  | { type: 'UPDATE_VOICE'; voiceSettings: VoicePersonalizationSettings }
  | { type: 'UPDATE_WORKFLOW'; workflow: Partial<WizardState['workflow']> }
  | { type: 'UPDATE_TESTING'; testing: Partial<WizardState['testing']> }
  | { type: 'UPDATE_DEPLOYMENT'; deployment: Partial<WizardState['deployment']> };
