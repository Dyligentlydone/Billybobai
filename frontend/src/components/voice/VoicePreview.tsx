import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  CircularProgress,
  Typography,
  Alert,
} from '@mui/material';
import { VoicePersonalizationSettings } from '../../types/wizard';

interface VoicePreviewProps {
  settings: VoicePersonalizationSettings;
  twilioConfig: {
    accountSid: string;
    authToken: string;
  };
}

export const VoicePreview: React.FC<VoicePreviewProps> = ({ settings, twilioConfig }) => {
  const [previewText, setPreviewText] = useState('Hello! How can I help you today?');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const generateSSML = () => {
    const { ssml } = settings;
    return `
      <speak>
        <prosody rate="${ssml.rate}" 
                 pitch="${ssml.pitch}" 
                 volume="${ssml.volume}">
          <emphasis level="${ssml.emphasis}">
            ${previewText}
          </emphasis>
          ${ssml.breakTime > 0 ? `<break time="${ssml.breakTime}ms"/>` : ''}
        </prosody>
      </speak>
    `.trim();
  };

  const handlePreview = async () => {
    setIsLoading(true);
    setError(null);
    setAudioUrl(null);

    try {
      const response = await fetch('/api/tts/preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: generateSSML(),
          voice: settings.voice.name,
          useSSML: true,
          ...twilioConfig,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate voice preview');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Voice Preview
      </Typography>

      <TextField
        fullWidth
        multiline
        rows={2}
        value={previewText}
        onChange={(e) => setPreviewText(e.target.value)}
        placeholder="Enter text to preview..."
        sx={{ mb: 2 }}
      />

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Button
          variant="contained"
          onClick={handlePreview}
          disabled={isLoading || !previewText.trim() || !twilioConfig.accountSid || !twilioConfig.authToken}
          startIcon={isLoading ? <CircularProgress size={20} /> : null}
        >
          {isLoading ? 'Generating...' : 'Preview Voice'}
        </Button>

        {audioUrl && (
          <audio controls>
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};
