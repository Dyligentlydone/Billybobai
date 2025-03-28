import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
  Typography,
  FormHelperText,
} from '@mui/material';
import { VoicePersonalizationSettings } from '../../types/wizard';

interface VoicePersonalizationProps {
  settings: VoicePersonalizationSettings;
  onSettingsChange: (settings: VoicePersonalizationSettings) => void;
}

export const VoicePersonalization: React.FC<VoicePersonalizationProps> = ({
  settings,
  onSettingsChange,
}) => {
  const handleVoiceTypeChange = (event: SelectChangeEvent) => {
    const type = event.target.value as 'basic' | 'neural' | 'standard';
    const newSettings = { ...settings };
    newSettings.voice.type = type;
    
    // If switching to basic, update to Twilio's basic voices
    if (type === 'basic') {
      newSettings.voice.provider = 'twilio';
      newSettings.voice.name = newSettings.voice.gender === 'male' ? 'man' : 'woman';
    }
    
    onSettingsChange(newSettings);
  };

  const handleGenderChange = (event: SelectChangeEvent) => {
    const gender = event.target.value as 'male' | 'female';
    const newSettings = { ...settings };
    newSettings.voice.gender = gender;
    
    // If using basic voice, update name accordingly
    if (newSettings.voice.type === 'basic') {
      newSettings.voice.name = gender === 'male' ? 'man' : 'woman';
    }
    
    onSettingsChange(newSettings);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Voice Settings
      </Typography>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Voice Type</InputLabel>
        <Select
          value={settings.voice.type}
          label="Voice Type"
          onChange={handleVoiceTypeChange}
        >
          <MenuItem value="basic">Basic (Fastest Response)</MenuItem>
          <MenuItem value="neural">Neural (High Quality)</MenuItem>
          <MenuItem value="standard">Standard</MenuItem>
        </Select>
        {settings.voice.type === 'basic' && (
          <FormHelperText>
            Basic voices provide instant response with minimal latency
          </FormHelperText>
        )}
      </FormControl>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Gender</InputLabel>
        <Select
          value={settings.voice.gender}
          label="Gender"
          onChange={handleGenderChange}
        >
          <MenuItem value="male">Male</MenuItem>
          <MenuItem value="female">Female</MenuItem>
        </Select>
      </FormControl>

      {settings.voice.type === 'basic' && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Using Twilio's basic {settings.voice.gender === 'male' ? 'man' : 'woman'} voice
          for optimal performance.
        </Typography>
      )}
    </Box>
  );
};
