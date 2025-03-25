export interface VoiceConfig {
  business: {
    name: string;
    phone: string;
    timezone: string;
    greeting: string;
  };
  integration: {
    twilio: {
      accountSid: string;
      authToken: string;
      phoneNumber: string;
    };
    openai: {
      apiKey: string;
      model: string;
      voiceId: string; // For text-to-speech
    };
  };
  callFlow: {
    greeting: string;
    mainMenu: {
      prompt: string;
      options: Array<{
        digit: string;
        description: string;
        action: 'transfer' | 'message' | 'voicemail';
      }>;
    };
    fallback: {
      message: string;
      action: 'transfer' | 'voicemail' | 'end';
    };
    businessHours: {
      enabled: boolean;
      timezone: string;
      hours: Record<string, {
        start: string;
        end: string;
      }>;
      outOfHoursMessage: string;
    };
    voicePreferences: {
      language: string;
      speed: number;
      gender: 'male' | 'female';
    };
  };
}
