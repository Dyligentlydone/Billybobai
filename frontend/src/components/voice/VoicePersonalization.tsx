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
  Slider,
  Divider,
  Alert,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { GridProps } from '@mui/material/Grid';

interface CustomGridProps extends Omit<GridProps, 'item' | 'container'> {
  item?: boolean;
  container?: boolean;
  xs?: number | boolean;
  md?: number | boolean;
}

const CustomGrid = React.forwardRef<HTMLDivElement, CustomGridProps>((props, ref) => {
  return <Grid {...props} ref={ref} />;
});

CustomGrid.displayName = 'CustomGrid';

import { 
  VoicePersonalizationSettings,
  SSMLRate,
  SSMLPitch,
  SSMLVolume,
  SSMLEmphasis,
  VoiceProvider 
} from '../../types/wizard';
import { getVoicesByType, getVoicesByGender, getVoiceByName } from '../../utils/voiceOptions';
import { VoicePreview } from './VoicePreview';

interface VoicePersonalizationProps {
  settings: VoicePersonalizationSettings;
  onSettingsChange: (settings: VoicePersonalizationSettings) => void;
  twilioConfig?: {
    accountSid: string;
    authToken: string;
  };
}

export const VoicePersonalization: React.FC<VoicePersonalizationProps> = ({
  settings,
  onSettingsChange,
  twilioConfig,
}) => {
  const availableVoices = useMemo(() => {
    const voices = getVoicesByType(settings.voice.type);
    return getVoicesByGender(voices, settings.voice.gender);
  }, [settings.voice.type, settings.voice.gender]);

  const voiceProviders: VoiceProvider[] = ['twilio', 'amazon-polly', 'google-text-to-speech'];

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

  const handleProviderChange = (event: SelectChangeEvent<VoiceProvider>) => {
    const provider = event.target.value as VoiceProvider;
    onSettingsChange({
      ...settings,
      voice: {
        ...settings.voice,
        provider
      }
    });
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
    <Box sx={{ width: '100%', p: 2 }}>
      <CustomGrid container spacing={3}>
        <CustomGrid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Voice Settings
          </Typography>
          <Divider sx={{ mb: 2 }} />
        </CustomGrid>

        <CustomGrid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Voice Type</InputLabel>
            <Select
              value={settings.voice.type}
              onChange={handleVoiceTypeChange}
              label="Voice Type"
            >
              <MenuItem value="basic">Basic (Fastest Response)</MenuItem>
              <MenuItem value="neural">Neural (High Quality)</MenuItem>
              <MenuItem value="standard">Standard</MenuItem>
            </Select>
            <FormHelperText>Select the type of voice synthesis</FormHelperText>
          </FormControl>
        </CustomGrid>

        <CustomGrid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Provider</InputLabel>
            <Select
              value={settings.voice.provider}
              onChange={handleProviderChange}
              label="Provider"
            >
              {voiceProviders.map((provider) => (
                <MenuItem key={provider} value={provider}>
                  {provider}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>Select a voice provider</FormHelperText>
          </FormControl>
        </CustomGrid>

        <CustomGrid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Gender</InputLabel>
            <Select
              value={settings.voice.gender}
              onChange={handleGenderChange}
              label="Gender"
            >
              <MenuItem value="male">Male</MenuItem>
              <MenuItem value="female">Female</MenuItem>
            </Select>
          </FormControl>
        </CustomGrid>

        {settings.voice.type !== 'basic' && (
          <CustomGrid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Voice</InputLabel>
              <Select
                value={settings.voice.name}
                onChange={handleVoiceChange}
                label="Voice"
              >
                {availableVoices.map((voice) => (
                  <MenuItem key={voice.name} value={voice.name}>
                    {voice.displayName} ({voice.accent})
                  </MenuItem>
                ))}
              </Select>
              <FormHelperText>Select a specific voice</FormHelperText>
            </FormControl>
          </CustomGrid>
        )}

        <CustomGrid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Voice Customization
          </Typography>
          <Divider sx={{ mb: 2 }} />
        </CustomGrid>

        <CustomGrid item xs={12} md={6}>
          <Typography gutterBottom>Speaking Rate</Typography>
          <FormControl fullWidth>
            <Select
              value={settings.ssml.rate}
              onChange={(e) => handleSSMLStringChange('rate', e.target.value)}
              label="Speaking Rate"
            >
              <MenuItem value="x-slow">Extra Slow</MenuItem>
              <MenuItem value="slow">Slow</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="fast">Fast</MenuItem>
              <MenuItem value="x-fast">Extra Fast</MenuItem>
            </Select>
            <FormHelperText>Speaking rate</FormHelperText>
          </FormControl>
        </CustomGrid>

        <CustomGrid item xs={12} md={6}>
          <Typography gutterBottom>Pitch</Typography>
          <FormControl fullWidth>
            <Select
              value={settings.ssml.pitch}
              onChange={(e) => handleSSMLStringChange('pitch', e.target.value)}
              label="Pitch"
            >
              <MenuItem value="x-low">Extra Low</MenuItem>
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="x-high">Extra High</MenuItem>
            </Select>
            <FormHelperText>Voice pitch</FormHelperText>
          </FormControl>
        </CustomGrid>

        <CustomGrid item xs={12} md={6}>
          <Typography gutterBottom>Volume</Typography>
          <FormControl fullWidth>
            <Select
              value={settings.ssml.volume}
              onChange={(e) => handleSSMLStringChange('volume', e.target.value)}
              label="Volume"
            >
              <MenuItem value="silent">Silent</MenuItem>
              <MenuItem value="x-soft">Extra Soft</MenuItem>
              <MenuItem value="soft">Soft</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="loud">Loud</MenuItem>
              <MenuItem value="x-loud">Extra Loud</MenuItem>
            </Select>
            <FormHelperText>Voice volume</FormHelperText>
          </FormControl>
        </CustomGrid>

        <CustomGrid item xs={12} md={6}>
          <Typography gutterBottom>Emphasis</Typography>
          <FormControl fullWidth>
            <Select
              value={settings.ssml.emphasis}
              onChange={(e) => handleSSMLStringChange('emphasis', e.target.value)}
              label="Emphasis"
            >
              <MenuItem value="reduced">Reduced</MenuItem>
              <MenuItem value="none">None</MenuItem>
              <MenuItem value="moderate">Moderate</MenuItem>
              <MenuItem value="strong">Strong</MenuItem>
            </Select>
            <FormHelperText>Voice emphasis</FormHelperText>
          </FormControl>
        </CustomGrid>

        <CustomGrid item xs={12}>
          <Typography gutterBottom>Break Time (ms)</Typography>
          <Slider
            value={settings.ssml.breakTime}
            onChange={handleBreakTimeChange}
            min={0}
            max={2000}
            step={100}
            valueLabelDisplay="auto"
            marks={[
              { value: 0, label: '0' },
              { value: 500, label: '500' },
              { value: 1000, label: '1000' },
              { value: 2000, label: '2000' }
            ]}
          />
          <FormHelperText>Add a pause after speaking (0-2000ms)</FormHelperText>
        </CustomGrid>

        {!twilioConfig && (
          <CustomGrid item xs={12}>
            <Alert severity="warning">
              Twilio credentials not configured. Voice preview will not be available.
            </Alert>
          </CustomGrid>
        )}

        <CustomGrid item xs={12}>
          {twilioConfig ? (
            <VoicePreview settings={settings} twilioConfig={twilioConfig} />
          ) : null}
        </CustomGrid>
      </CustomGrid>
    </Box>
  );
};
