import { VoiceProvider } from '../types/wizard';

interface VoiceOption {
  name: string;
  displayName: string;
  gender: 'male' | 'female';
  accent: string;
  provider: VoiceProvider;
  type: 'basic' | 'neural' | 'standard';
}

export const voiceOptions: VoiceOption[] = [
  // Basic Twilio voices
  {
    name: 'man',
    displayName: 'Man',
    gender: 'male',
    accent: 'American',
    provider: 'twilio',
    type: 'basic'
  },
  {
    name: 'woman',
    displayName: 'Woman',
    gender: 'female',
    accent: 'American',
    provider: 'twilio',
    type: 'basic'
  },

  // Neural Amazon Polly voices
  {
    name: 'Polly.Joanna',
    displayName: 'Joanna',
    gender: 'female',
    accent: 'American',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Matthew',
    displayName: 'Matthew',
    gender: 'male',
    accent: 'American',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Ivy',
    displayName: 'Ivy',
    gender: 'female',
    accent: 'American (Child)',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Kendra',
    displayName: 'Kendra',
    gender: 'female',
    accent: 'American',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Kevin',
    displayName: 'Kevin',
    gender: 'male',
    accent: 'American (Child)',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Salli',
    displayName: 'Salli',
    gender: 'female',
    accent: 'American',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Stephen',
    displayName: 'Stephen',
    gender: 'male',
    accent: 'American',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Emma',
    displayName: 'Emma',
    gender: 'female',
    accent: 'British',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Brian',
    displayName: 'Brian',
    gender: 'male',
    accent: 'British',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Amy',
    displayName: 'Amy',
    gender: 'female',
    accent: 'British',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Arthur',
    displayName: 'Arthur',
    gender: 'male',
    accent: 'British',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Olivia',
    displayName: 'Olivia',
    gender: 'female',
    accent: 'Australian',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Liam',
    displayName: 'Liam',
    gender: 'male',
    accent: 'Australian',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Aria',
    displayName: 'Aria',
    gender: 'female',
    accent: 'New Zealand',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Gabrielle',
    displayName: 'Gabrielle',
    gender: 'female',
    accent: 'French',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Lea',
    displayName: 'Lea',
    gender: 'female',
    accent: 'French',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Vicki',
    displayName: 'Vicki',
    gender: 'female',
    accent: 'German',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Daniel',
    displayName: 'Daniel',
    gender: 'male',
    accent: 'German',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Hannah',
    displayName: 'Hannah',
    gender: 'female',
    accent: 'German',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Bianca',
    displayName: 'Bianca',
    gender: 'female',
    accent: 'Italian',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Adriano',
    displayName: 'Adriano',
    gender: 'male',
    accent: 'Italian',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Pedro',
    displayName: 'Pedro',
    gender: 'male',
    accent: 'Portuguese',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Camila',
    displayName: 'Camila',
    gender: 'female',
    accent: 'Portuguese',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Lucia',
    displayName: 'Lucia',
    gender: 'female',
    accent: 'Spanish (Castilian)',
    provider: 'amazon-polly',
    type: 'neural'
  },
  {
    name: 'Polly.Sergio',
    displayName: 'Sergio',
    gender: 'male',
    accent: 'Spanish (Castilian)',
    provider: 'amazon-polly',
    type: 'neural'
  },

  // Google Cloud voices
  {
    name: 'en-US-Neural2-A',
    displayName: 'Neural A',
    gender: 'female',
    accent: 'American',
    provider: 'google-text-to-speech',
    type: 'neural'
  },
  {
    name: 'en-US-Neural2-C',
    displayName: 'Neural C',
    gender: 'female',
    accent: 'American',
    provider: 'google-text-to-speech',
    type: 'neural'
  },
  {
    name: 'en-US-Neural2-D',
    displayName: 'Neural D',
    gender: 'male',
    accent: 'American',
    provider: 'google-text-to-speech',
    type: 'neural'
  },
  {
    name: 'en-US-Neural2-F',
    displayName: 'Neural F',
    gender: 'female',
    accent: 'American',
    provider: 'google-text-to-speech',
    type: 'neural'
  },
  {
    name: 'en-US-Neural2-H',
    displayName: 'Neural H',
    gender: 'female',
    accent: 'American',
    provider: 'google-text-to-speech',
    type: 'neural'
  },
  {
    name: 'en-US-Neural2-I',
    displayName: 'Neural I',
    gender: 'male',
    accent: 'American',
    provider: 'google-text-to-speech',
    type: 'neural'
  }
];

export const getVoicesByType = (type: 'basic' | 'neural' | 'standard'): VoiceOption[] => {
  return voiceOptions.filter(voice => voice.type === type);
};

export const getVoicesByGender = (voices: VoiceOption[], gender: 'male' | 'female'): VoiceOption[] => {
  return voices.filter(voice => voice.gender === gender);
};

export const getVoiceByName = (name: string): VoiceOption | undefined => {
  return voiceOptions.find(voice => voice.name === name);
};
