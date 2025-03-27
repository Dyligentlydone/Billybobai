export interface VoiceConfig {
  business: {
    name: string;
    phone: string;
    timezone: string;
  };
  integration: {
    twilio: {
      accountSid: string;
      authToken: string;
      phoneNumber: string;
    };
    openai: {
      apiKey: string;
    };
  };
  callFlow: {
    greeting: {
      enabled: boolean;
      message: string;
      voice: {
        language: string;
        gender: 'male' | 'female';
        speed: number;
      };
    };
    mainMenu: {
      prompt: string;
      options: Array<{
        digit: string;
        description: string;
        action: 'message' | 'transfer' | 'voicemail';
      }>;
    };
    fallback: {
      message: string;
      action: 'transfer' | 'voicemail' | 'end';
    };
    businessHours: {
      enabled: boolean;
      timezone: string;
      hours: Record<string, { start: string; end: string; }>;
      outOfHoursMessage: string;
    };
    voicePreferences: {
      language: string;
      speed: number;
      gender: 'male' | 'female';
    };
    workflow?: {
      nodes: VoiceNodeData[];
      edges: Array<{
        id: string;
        source: string;
        target: string;
      }>;
    };
  };
}

// Voice workflow node types
export type VoiceNodeType = 
  | 'menu'           // IVR menu with options
  | 'message'        // AI response
  | 'transfer'       // Transfer to agent
  | 'voicemail'      // Record voicemail
  | 'hours'          // Business hours check
  | 'condition'      // Conditional branching
  | 'end';           // End call

export interface VoiceNodeData {
  label: string;
  type: VoiceNodeType;
  // Menu Node
  prompt?: string;
  options?: MenuOption[];
  timeoutSeconds?: number;
  maxRetries?: number;
  invalidInputMessage?: string;
  timeoutMessage?: string;
  defaultRouteNodeId?: string;
  repeatOptionsMessage?: string;
  invalidInputAction?: 'repeat' | 'default' | 'disconnect';
  gatherConfig?: {
    finishOnKey: string;
    numDigits?: number;
    timeout: number;
  };
  // Message Node
  aiModel?: string;
  maxTokens?: number;
  // Transfer Node
  transferNumber?: string;
  // Voicemail Node
  maxDuration?: number;
  transcribe?: boolean;
  // Hours Node
  timezone?: string;
  schedule?: BusinessHours[];
  outOfHoursNode?: string;
  // Condition Node
  conditions?: Condition[];
  // Voice Settings
  voice?: {
    language: string;
    gender: string;
    speed: number;
  };
}

export interface MenuOption {
  digit: string;
  description: string;
  nextNodeId: string;
}

export interface BusinessHours {
  day: string;
  start: string;
  end: string;
}

export interface Condition {
  type: string;
  operator: string;
  value: string;
  nextNodeId: string;
}

export interface MenuNodeData extends VoiceNodeData {
  prompt: string;
  options: Array<{
    digit: string;
    description: string;
    nextNodeId: string;
  }>;
  timeoutSeconds: number;
  maxRetries: number;
  invalidInputMessage: string;
  timeoutMessage: string;
  defaultRouteNodeId?: string;
  repeatOptionsMessage?: string;
  invalidInputAction?: 'repeat' | 'default' | 'disconnect';
  gatherConfig?: {
    finishOnKey: string;
    numDigits?: number;
    timeout: number;
  };
}

export interface VoiceWorkflowNode {
  id: string;
  type: 'voiceNode';
  position: { x: number; y: number; };
  data: VoiceNodeData;
}
