import React from 'react';
import {
  Box,
  Typography,
  Select,
  MenuItem,
  Slider,
  TextField,
  Chip,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { VoicePersonalizationSettings } from '../../types/voice';

interface VoicePersonalizationProps {
  settings: VoicePersonalizationSettings;
  onChange: (settings: VoicePersonalizationSettings) => void;
  title?: string;
}

const voiceAccents = [
  'American', 'British', 'Australian', 'Indian',
  'Irish', 'South African', 'Canadian'
];

const voiceNames = {
  male: ['Matthew', 'James', 'David', 'John'],
  female: ['Sarah', 'Emma', 'Lisa', 'Amy']
};

export const VoicePersonalization: React.FC<VoicePersonalizationProps> = ({
  settings,
  onChange,
  title = 'Voice Settings'
}) => {
  const handleChange = (path: string, value: any) => {
    const newSettings = { ...settings };
    const parts = path.split('.');
    let current: any = newSettings;
    
    for (let i = 0; i < parts.length - 1; i++) {
      current = current[parts[i]];
    }
    current[parts[parts.length - 1]] = value;
    
    onChange(newSettings);
  };

  const addPersonalityTrait = (trait: string) => {
    if (!settings.brand.personality.includes(trait)) {
      handleChange('brand.personality', [...settings.brand.personality, trait]);
    }
  };

  const removePersonalityTrait = (trait: string) => {
    handleChange('brand.personality', 
      settings.brand.personality.filter(t => t !== trait)
    );
  };

  const addCustomPhrase = (type: 'greeting' | 'confirmation' | 'farewell', phrase: string) => {
    handleChange(`brand.customPhrases.${type}`, 
      [...settings.brand.customPhrases[type], phrase]
    );
  };

  const removeCustomPhrase = (type: 'greeting' | 'confirmation' | 'farewell', index: number) => {
    handleChange(`brand.customPhrases.${type}`,
      settings.brand.customPhrases[type].filter((_, i) => i !== index)
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        {title}
      </Typography>

      <Grid container spacing={3}>
        {/* Voice Selection */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Voice Selection
              </Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Voice Type</InputLabel>
                <Select
                  value={settings.voice.type}
                  onChange={(e) => handleChange('voice.type', e.target.value)}
                  label="Voice Type"
                >
                  <MenuItem value="neural">Neural (Premium)</MenuItem>
                  <MenuItem value="standard">Standard</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Gender</InputLabel>
                <Select
                  value={settings.voice.gender}
                  onChange={(e) => handleChange('voice.gender', e.target.value)}
                  label="Gender"
                >
                  <MenuItem value="male">Male</MenuItem>
                  <MenuItem value="female">Female</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Accent</InputLabel>
                <Select
                  value={settings.voice.accent}
                  onChange={(e) => handleChange('voice.accent', e.target.value)}
                  label="Accent"
                >
                  {voiceAccents.map(accent => (
                    <MenuItem key={accent} value={accent}>{accent}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Voice Name</InputLabel>
                <Select
                  value={settings.voice.name}
                  onChange={(e) => handleChange('voice.name', e.target.value)}
                  label="Voice Name"
                >
                  {voiceNames[settings.voice.gender].map(name => (
                    <MenuItem key={name} value={name}>{name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Speech Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Speech Settings
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Speed</Typography>
                <Slider
                  value={settings.speech.rate}
                  onChange={(_, value) => handleChange('speech.rate', value)}
                  min={0.5}
                  max={2.0}
                  step={0.1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Pitch</Typography>
                <Slider
                  value={settings.speech.pitch}
                  onChange={(_, value) => handleChange('speech.pitch', value)}
                  min={-20}
                  max={20}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <FormControl fullWidth>
                <InputLabel>Emphasis</InputLabel>
                <Select
                  value={settings.speech.emphasis}
                  onChange={(e) => handleChange('speech.emphasis', e.target.value)}
                  label="Emphasis"
                >
                  <MenuItem value="reduced">Reduced</MenuItem>
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="enhanced">Enhanced</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Brand Personality */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Brand Personality
              </Typography>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Tone</InputLabel>
                <Select
                  value={settings.brand.tone}
                  onChange={(e) => handleChange('brand.tone', e.target.value)}
                  label="Tone"
                >
                  <MenuItem value="professional">Professional</MenuItem>
                  <MenuItem value="friendly">Friendly</MenuItem>
                  <MenuItem value="casual">Casual</MenuItem>
                  <MenuItem value="formal">Formal</MenuItem>
                </Select>
              </FormControl>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Personality Traits</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {settings.brand.personality.map((trait) => (
                    <Chip
                      key={trait}
                      label={trait}
                      onDelete={() => removePersonalityTrait(trait)}
                    />
                  ))}
                </Box>
                <TextField
                  fullWidth
                  placeholder="Add trait (press Enter)"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      const input = e.target as HTMLInputElement;
                      addPersonalityTrait(input.value);
                      input.value = '';
                    }
                  }}
                  sx={{ mt: 1 }}
                />
              </Box>

              {/* Custom Phrases */}
              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Custom Phrases</Typography>
                {(['greeting', 'confirmation', 'farewell'] as const).map((type) => (
                  <Box key={type} sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ textTransform: 'capitalize' }}>
                      {type} Phrases
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                      {settings.brand.customPhrases[type].map((phrase, index) => (
                        <Chip
                          key={index}
                          label={phrase}
                          onDelete={() => removeCustomPhrase(type, index)}
                        />
                      ))}
                    </Box>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder={`Add ${type} phrase (press Enter)`}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          const input = e.target as HTMLInputElement;
                          addCustomPhrase(type, input.value);
                          input.value = '';
                        }
                      }}
                    />
                  </Box>
                ))}
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Prosody Settings</Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.brand.prosody.wordEmphasis}
                      onChange={(e) => handleChange('brand.prosody.wordEmphasis', e.target.checked)}
                    />
                  }
                  label="Word Emphasis"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.brand.prosody.naturalPauses}
                      onChange={(e) => handleChange('brand.prosody.naturalPauses', e.target.checked)}
                    />
                  }
                  label="Natural Pauses"
                />
                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>Intonation</InputLabel>
                  <Select
                    value={settings.brand.prosody.intonation}
                    onChange={(e) => handleChange('brand.prosody.intonation', e.target.value)}
                    label="Intonation"
                  >
                    <MenuItem value="natural">Natural</MenuItem>
                    <MenuItem value="expressive">Expressive</MenuItem>
                    <MenuItem value="controlled">Controlled</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Timing Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Timing & Pacing
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Response Delay (ms)</Typography>
                <Slider
                  value={settings.timing.responseDelay}
                  onChange={(_, value) => handleChange('timing.responseDelay', value)}
                  min={0}
                  max={2000}
                  step={100}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Word Spacing</Typography>
                <Slider
                  value={settings.timing.wordSpacing}
                  onChange={(_, value) => handleChange('timing.wordSpacing', value)}
                  min={0.8}
                  max={1.2}
                  step={0.1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <Typography gutterBottom>Pause Duration (ms)</Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <TextField
                    label="Comma"
                    type="number"
                    value={settings.timing.pauseDuration.comma}
                    onChange={(e) => handleChange('timing.pauseDuration.comma', Number(e.target.value))}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    label="Period"
                    type="number"
                    value={settings.timing.pauseDuration.period}
                    onChange={(e) => handleChange('timing.pauseDuration.period', Number(e.target.value))}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    label="Question"
                    type="number"
                    value={settings.timing.pauseDuration.question}
                    onChange={(e) => handleChange('timing.pauseDuration.question', Number(e.target.value))}
                    fullWidth
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
