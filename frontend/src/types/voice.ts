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
  prompt?: string;
  options?: Array<{
    digit: string;
    description: string;
    nextNodeId?: string;
  }>;
  aiModel?: string;
  maxTokens?: number;
  transferNumber?: string;
  maxDuration?: number;
  transcribe?: boolean;
  timezone?: string;
  schedule?: Array<{
    day: string;
    open: string;
    close: string;
  }>;
  outOfHoursNode?: string;
  conditions?: Array<{
    condition: string;
    nextNodeId: string;
  }>;
  voice?: {
    language: string;
    gender: string;
    speed: number;
  };
}

export interface VoiceWorkflowNode {
  id: string;
  type: 'voiceNode';
  position: { x: number; y: number; };
  data: VoiceNodeData;
}
