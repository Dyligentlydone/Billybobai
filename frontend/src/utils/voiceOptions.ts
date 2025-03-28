interface VoiceOption {
  name: string;
  displayName: string;
  gender: 'male' | 'female';
  accent: string;
  provider: 'twilio' | 'polly' | 'google';
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
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Matthew',
    displayName: 'Matthew',
    gender: 'male',
    accent: 'American',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Ivy',
    displayName: 'Ivy',
    gender: 'female',
    accent: 'American (Child)',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Kendra',
    displayName: 'Kendra',
    gender: 'female',
    accent: 'American',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Kevin',
    displayName: 'Kevin',
    gender: 'male',
    accent: 'American (Child)',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Salli',
    displayName: 'Salli',
    gender: 'female',
    accent: 'American',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Stephen',
    displayName: 'Stephen',
    gender: 'male',
    accent: 'American',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Emma',
    displayName: 'Emma',
    gender: 'female',
    accent: 'British',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Brian',
    displayName: 'Brian',
    gender: 'male',
    accent: 'British',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Amy',
    displayName: 'Amy',
    gender: 'female',
    accent: 'British',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Arthur',
    displayName: 'Arthur',
    gender: 'male',
    accent: 'British',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Olivia',
    displayName: 'Olivia',
    gender: 'female',
    accent: 'Australian',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Liam',
    displayName: 'Liam',
    gender: 'male',
    accent: 'Australian',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Aria',
    displayName: 'Aria',
    gender: 'female',
    accent: 'New Zealand',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Gabrielle',
    displayName: 'Gabrielle',
    gender: 'female',
    accent: 'French',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Lea',
    displayName: 'Lea',
    gender: 'female',
    accent: 'French',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Vicki',
    displayName: 'Vicki',
    gender: 'female',
    accent: 'German',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Daniel',
    displayName: 'Daniel',
    gender: 'male',
    accent: 'German',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Hannah',
    displayName: 'Hannah',
    gender: 'female',
    accent: 'German',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Bianca',
    displayName: 'Bianca',
    gender: 'female',
    accent: 'Italian',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Adriano',
    displayName: 'Adriano',
    gender: 'male',
    accent: 'Italian',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Pedro',
    displayName: 'Pedro',
    gender: 'male',
    accent: 'Portuguese',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Camila',
    displayName: 'Camila',
    gender: 'female',
    accent: 'Portuguese',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Lucia',
    displayName: 'Lucia',
    gender: 'female',
    accent: 'Spanish (Castilian)',
    provider: 'polly',
    type: 'neural'
  },
  {
    name: 'Polly.Sergio',
    displayName: 'Sergio',
    gender: 'male',
    accent: 'Spanish (Castilian)',
    provider: 'polly',
    type: 'neural'
  },

  // Standard Google voices
  {
    name: 'Google.en-US-Standard-A',
    displayName: 'Alex',
    gender: 'male',
    accent: 'American',
    provider: 'google',
    type: 'standard'
  },
  {
    name: 'Google.en-US-Standard-B',
    displayName: 'Beth',
    gender: 'female',
    accent: 'American',
    provider: 'google',
    type: 'standard'
  },
  {
    name: 'Google.en-GB-Standard-A',
    displayName: 'Charles',
    gender: 'male',
    accent: 'British',
    provider: 'google',
    type: 'standard'
  },
  {
    name: 'Google.en-GB-Standard-B',
    displayName: 'Diana',
    gender: 'female',
    accent: 'British',
    provider: 'google',
    type: 'standard'
  },
  {
    name: 'Google.en-AU-Standard-A',
    displayName: 'James',
    gender: 'male',
    accent: 'Australian',
    provider: 'google',
    type: 'standard'
  },
  {
    name: 'Google.en-AU-Standard-B',
    displayName: 'Karen',
    gender: 'female',
    accent: 'Australian',
    provider: 'google',
    type: 'standard'
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
