import React, { useMemo } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
  Typography,
  FormHelperText,
  Grid,
  Slider,
  Divider,
} from '@mui/material';
import { 
  VoicePersonalizationSettings,
  SSMLRate,
  SSMLPitch,
  SSMLVolume,
  SSMLEmphasis 
} from '../../types/wizard';
import { getVoicesByType, getVoicesByGender, getVoiceByName } from '../../utils/voiceOptions';
import { VoicePreview } from './VoicePreview';

interface VoicePersonalizationProps {
  settings: VoicePersonalizationSettings;
  onSettingsChange: (settings: VoicePersonalizationSettings) => void;
}

export const VoicePersonalization: React.FC<VoicePersonalizationProps> = ({
  settings,
  onSettingsChange,
}) => {
  const availableVoices = useMemo(() => {
    const voices = getVoicesByType(settings.voice.type);
    return getVoicesByGender(voices, settings.voice.gender);
  }, [settings.voice.type, settings.voice.gender]);

  const handleVoiceTypeChange = (event: SelectChangeEvent) => {
    const type = event.target.value as 'basic' | 'neural' | 'standard';
    const newSettings = { ...settings };
    newSettings.voice.type = type;
    
    // If switching to basic, update to Twilio's basic voices
    if (type === 'basic') {
      newSettings.voice.provider = 'twilio';
      newSettings.voice.name = newSettings.voice.gender === 'male' ? 'man' : 'woman';
    } else {
      // Select the first available voice of the selected type and gender
      const voices = getVoicesByType(type);
      const genderVoices = getVoicesByGender(voices, settings.voice.gender);
      if (genderVoices.length > 0) {
        const voice = genderVoices[0];
        newSettings.voice.name = voice.name;
        newSettings.voice.provider = voice.provider;
        newSettings.voice.accent = voice.accent;
      }
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
    } else {
      // Select the first available voice of the current type and new gender
      const voices = getVoicesByType(settings.voice.type);
      const genderVoices = getVoicesByGender(voices, gender);
      if (genderVoices.length > 0) {
        const voice = genderVoices[0];
        newSettings.voice.name = voice.name;
        newSettings.voice.provider = voice.provider;
        newSettings.voice.accent = voice.accent;
      }
    }
    
    onSettingsChange(newSettings);
  };

  const handleVoiceChange = (event: SelectChangeEvent) => {
    const voiceName = event.target.value;
    const voice = getVoiceByName(voiceName);
    if (voice) {
      const newSettings = { ...settings };
      newSettings.voice.name = voice.name;
      newSettings.voice.provider = voice.provider;
      newSettings.voice.accent = voice.accent;
      onSettingsChange(newSettings);
    }
  };

  const handleSSMLStringChange = (
    property: 'rate' | 'pitch' | 'volume' | 'emphasis',
    value: string
  ) => {
    const newSettings = { ...settings };
    switch (property) {
      case 'rate':
        newSettings.ssml.rate = value as SSMLRate;
        break;
      case 'pitch':
        newSettings.ssml.pitch = value as SSMLPitch;
        break;
      case 'volume':
        newSettings.ssml.volume = value as SSMLVolume;
        break;
      case 'emphasis':
        newSettings.ssml.emphasis = value as SSMLEmphasis;
        break;
    }
    onSettingsChange(newSettings);
  };

  const handleBreakTimeChange = (_: Event, value: number | number[]) => {
    const newSettings = { ...settings };
    newSettings.ssml.breakTime = value as number;
    onSettingsChange(newSettings);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Voice Settings
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
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
        </Grid>

        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
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
        </Grid>

        {settings.voice.type !== 'basic' && (
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Voice</InputLabel>
              <Select
                value={settings.voice.name}
                label="Voice"
                onChange={handleVoiceChange}
              >
                {availableVoices.map((voice) => (
                  <MenuItem key={voice.name} value={voice.name}>
                    {voice.displayName} ({voice.accent})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        )}
      </Grid>

      {settings.voice.type === 'basic' && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Using Twilio's basic {settings.voice.gender === 'male' ? 'man' : 'woman'} voice
          for optimal performance.
        </Typography>
      )}

      {settings.voice.type !== 'basic' && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Using {settings.voice.provider} {settings.voice.accent} voice for enhanced quality.
        </Typography>
      )}

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" gutterBottom>
        Voice Customization
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Speaking Rate</InputLabel>
            <Select
              value={settings.ssml.rate}
              label="Speaking Rate"
              onChange={(e) => handleSSMLStringChange('rate', e.target.value)}
            >
              <MenuItem value="x-slow">Extra Slow</MenuItem>
              <MenuItem value="slow">Slow</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="fast">Fast</MenuItem>
              <MenuItem value="x-fast">Extra Fast</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Pitch</InputLabel>
            <Select
              value={settings.ssml.pitch}
              label="Pitch"
              onChange={(e) => handleSSMLStringChange('pitch', e.target.value)}
            >
              <MenuItem value="x-low">Extra Low</MenuItem>
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="x-high">Extra High</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Volume</InputLabel>
            <Select
              value={settings.ssml.volume}
              label="Volume"
              onChange={(e) => handleSSMLStringChange('volume', e.target.value)}
            >
              <MenuItem value="silent">Silent</MenuItem>
              <MenuItem value="x-soft">Extra Soft</MenuItem>
              <MenuItem value="soft">Soft</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="loud">Loud</MenuItem>
              <MenuItem value="x-loud">Extra Loud</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Emphasis</InputLabel>
            <Select
              value={settings.ssml.emphasis}
              label="Emphasis"
              onChange={(e) => handleSSMLStringChange('emphasis', e.target.value)}
            >
              <MenuItem value="reduced">Reduced</MenuItem>
              <MenuItem value="none">None</MenuItem>
              <MenuItem value="moderate">Moderate</MenuItem>
              <MenuItem value="strong">Strong</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <Typography gutterBottom>
            Break Time (ms)
          </Typography>
          <Slider
            value={settings.ssml.breakTime}
            onChange={handleBreakTimeChange}
            min={0}
            max={2000}
            step={100}
            marks={[
              { value: 0, label: '0' },
              { value: 500, label: '500' },
              { value: 1000, label: '1000' },
              { value: 2000, label: '2000' }
            ]}
            valueLabelDisplay="auto"
          />
          <FormHelperText>
            Add a pause after speaking (0-2000ms)
          </FormHelperText>
        </Grid>
      </Grid>

      <VoicePreview settings={settings} />
    </Box>
  );
};
