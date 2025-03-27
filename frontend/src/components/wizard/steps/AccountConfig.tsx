import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  FormControlLabel,
  Switch,
  Grid,
  Paper,
  Alert,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import { Help as HelpIcon } from '@mui/icons-material';
import { useWizard } from '../../../contexts/WizardContext';

export function AccountConfig() {
  const { state, dispatch } = useWizard();
  const [validating, setValidating] = useState<{
    twilio: boolean;
    openai: boolean;
    zendesk: boolean;
  }>({
    twilio: false,
    openai: false,
    zendesk: false,
  });

  const validateTwilio = async () => {
    setValidating(v => ({ ...v, twilio: true }));
    try {
      // TODO: Add actual Twilio validation
      await new Promise(resolve => setTimeout(resolve, 1000));
      dispatch({
        type: 'UPDATE_SERVICES',
        services: {
          twilio: {
            ...state.services.twilio,
            isValid: true,
          },
        },
      });
    } catch (error) {
      dispatch({
        type: 'UPDATE_SERVICES',
        services: {
          twilio: {
            ...state.services.twilio,
            isValid: false,
            error: 'Failed to validate Twilio credentials',
          },
        },
      });
    } finally {
      setValidating(v => ({ ...v, twilio: false }));
    }
  };

  const validateOpenAI = async () => {
    setValidating(v => ({ ...v, openai: true }));
    try {
      // TODO: Add actual OpenAI validation
      await new Promise(resolve => setTimeout(resolve, 1000));
      dispatch({
        type: 'UPDATE_SERVICES',
        services: {
          openai: {
            ...state.services.openai,
            isValid: true,
          },
        },
      });
    } catch (error) {
      dispatch({
        type: 'UPDATE_SERVICES',
        services: {
          openai: {
            ...state.services.openai,
            isValid: false,
            error: 'Failed to validate OpenAI credentials',
          },
        },
      });
    } finally {
      setValidating(v => ({ ...v, openai: false }));
    }
  };

  const validateZendesk = async () => {
    if (!state.services.zendesk?.enabled) return;
    
    setValidating(v => ({ ...v, zendesk: true }));
    try {
      // TODO: Add actual Zendesk validation
      await new Promise(resolve => setTimeout(resolve, 1000));
      dispatch({
        type: 'UPDATE_SERVICES',
        services: {
          zendesk: {
            ...state.services.zendesk,
            isValid: true,
          },
        },
      });
    } catch (error) {
      dispatch({
        type: 'UPDATE_SERVICES',
        services: {
          zendesk: {
            ...state.services.zendesk,
            isValid: false,
            error: 'Failed to validate Zendesk credentials',
          },
        },
      });
    } finally {
      setValidating(v => ({ ...v, zendesk: false }));
    }
  };

  const handleTwilioChange = (field: keyof typeof state.services.twilio) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    dispatch({
      type: 'UPDATE_SERVICES',
      services: {
        twilio: {
          ...state.services.twilio,
          [field]: e.target.value,
          isValid: false,
        },
      },
    });
  };

  const handleOpenAIChange = (field: keyof typeof state.services.openai) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    dispatch({
      type: 'UPDATE_SERVICES',
      services: {
        openai: {
          ...state.services.openai,
          [field]: e.target.value,
          isValid: false,
        },
      },
    });
  };

  const handleZendeskToggle = () => {
    dispatch({
      type: 'UPDATE_SERVICES',
      services: {
        zendesk: {
          ...state.services.zendesk,
          enabled: !state.services.zendesk?.enabled,
          isValid: false,
        },
      },
    });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Connect Your Services
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Provide API credentials to connect Twilio, OpenAI, and optionally Zendesk.
        We'll validate them for you.
      </Typography>

      <Grid container spacing={3}>
        {/* Twilio Configuration */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <Typography variant="h6">Twilio Credentials</Typography>
              <Tooltip title="Find these in your Twilio Console">
                <IconButton size="small" sx={{ ml: 1 }}>
                  <HelpIcon />
                </IconButton>
              </Tooltip>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Account SID"
                  value={state.services.twilio.accountSid}
                  onChange={handleTwilioChange('accountSid')}
                  error={state.services.twilio.error !== undefined}
                  helperText={state.services.twilio.error}
                  InputProps={{
                    endAdornment: validating.twilio && <CircularProgress size={20} />,
                  }}
                  onBlur={validateTwilio}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Auth Token"
                  type="password"
                  value={state.services.twilio.authToken}
                  onChange={handleTwilioChange('authToken')}
                  error={state.services.twilio.error !== undefined}
                  InputProps={{
                    endAdornment: validating.twilio && <CircularProgress size={20} />,
                  }}
                  onBlur={validateTwilio}
                />
              </Grid>
            </Grid>

            {state.services.twilio.isValid && (
              <Alert severity="success" sx={{ mt: 2 }}>
                Twilio credentials validated successfully
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* OpenAI Configuration */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <Typography variant="h6">OpenAI Configuration</Typography>
              <Tooltip title="Find this in your OpenAI dashboard">
                <IconButton size="small" sx={{ ml: 1 }}>
                  <HelpIcon />
                </IconButton>
              </Tooltip>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="API Key"
                  type="password"
                  value={state.services.openai.apiKey}
                  onChange={handleOpenAIChange('apiKey')}
                  error={state.services.openai.error !== undefined}
                  helperText={state.services.openai.error}
                  InputProps={{
                    endAdornment: validating.openai && <CircularProgress size={20} />,
                  }}
                  onBlur={validateOpenAI}
                />
              </Grid>
            </Grid>

            {state.services.openai.isValid && (
              <Alert severity="success" sx={{ mt: 2 }}>
                OpenAI credentials validated successfully
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Zendesk Configuration */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <Typography variant="h6">Zendesk Integration</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={state.services.zendesk?.enabled}
                    onChange={handleZendeskToggle}
                  />
                }
                label="Enable Zendesk"
                sx={{ ml: 2 }}
              />
            </Box>

            {state.services.zendesk?.enabled && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="API Token"
                    type="password"
                    value={state.services.zendesk?.apiToken}
                    onChange={e =>
                      dispatch({
                        type: 'UPDATE_SERVICES',
                        services: {
                          zendesk: {
                            ...state.services.zendesk,
                            enabled: true,
                            apiToken: e.target.value,
                            isValid: false,
                          },
                        },
                      })
                    }
                    error={state.services.zendesk?.error !== undefined}
                    helperText={state.services.zendesk?.error}
                    InputProps={{
                      endAdornment: validating.zendesk && <CircularProgress size={20} />,
                    }}
                    onBlur={validateZendesk}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Subdomain"
                    value={state.services.zendesk?.subdomain}
                    onChange={e =>
                      dispatch({
                        type: 'UPDATE_SERVICES',
                        services: {
                          zendesk: {
                            ...state.services.zendesk,
                            enabled: true,
                            subdomain: e.target.value,
                            isValid: false,
                          },
                        },
                      })
                    }
                    placeholder="your-subdomain"
                    InputProps={{
                      endAdornment: validating.zendesk && <CircularProgress size={20} />,
                    }}
                    onBlur={validateZendesk}
                  />
                </Grid>
              </Grid>
            )}

            {state.services.zendesk?.enabled && state.services.zendesk?.isValid && (
              <Alert severity="success" sx={{ mt: 2 }}>
                Zendesk credentials validated successfully
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
