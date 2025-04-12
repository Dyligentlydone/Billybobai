import { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  FormControlLabel,
  Switch,
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

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Account Configuration
      </Typography>
      <Typography variant="body1" gutterBottom>
        Configure your service accounts for the automation workflow.
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="h6">Twilio Configuration</Typography>
            <Tooltip title="Your Twilio credentials can be found in your Twilio Console">
              <IconButton size="small">
                <HelpIcon />
              </IconButton>
            </Tooltip>
          </Box>

          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ flex: '1 1 300px' }}>
              <TextField
                fullWidth
                label="Account SID"
                value={state.services.twilio?.accountSid || ''}
                onChange={e =>
                  dispatch({
                    type: 'UPDATE_SERVICES',
                    services: {
                      twilio: {
                        ...state.services.twilio,
                        accountSid: e.target.value,
                        isValid: false,
                      },
                    },
                  })
                }
                error={state.services.twilio?.error !== undefined}
                helperText={state.services.twilio?.error}
                InputProps={{
                  endAdornment: validating.twilio && <CircularProgress size={20} />,
                }}
                onBlur={validateTwilio}
              />
            </Box>

            <Box sx={{ flex: '1 1 300px' }}>
              <TextField
                fullWidth
                label="Auth Token"
                type="password"
                value={state.services.twilio?.authToken || ''}
                onChange={e =>
                  dispatch({
                    type: 'UPDATE_SERVICES',
                    services: {
                      twilio: {
                        ...state.services.twilio,
                        authToken: e.target.value,
                        isValid: false,
                      },
                    },
                  })
                }
                error={state.services.twilio?.error !== undefined}
                helperText={state.services.twilio?.error}
                InputProps={{
                  endAdornment: validating.twilio && <CircularProgress size={20} />,
                }}
                onBlur={validateTwilio}
              />
            </Box>
          </Box>

          {state.services.twilio?.isValid && (
            <Alert severity="success" sx={{ mt: 2 }}>
              Twilio credentials validated successfully
            </Alert>
          )}
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="h6">OpenAI Configuration</Typography>
            <Tooltip title="Your OpenAI API key can be found in your OpenAI dashboard">
              <IconButton size="small">
                <HelpIcon />
              </IconButton>
            </Tooltip>
          </Box>

          <Box sx={{ flex: '1 1 300px' }}>
            <TextField
              fullWidth
              label="API Key"
              type="password"
              value={state.services.openai?.apiKey || ''}
              onChange={e =>
                dispatch({
                  type: 'UPDATE_SERVICES',
                  services: {
                    openai: {
                      ...state.services.openai,
                      apiKey: e.target.value,
                      isValid: false,
                    },
                  },
                })
              }
              error={state.services.openai?.error !== undefined}
              helperText={state.services.openai?.error}
              InputProps={{
                endAdornment: validating.openai && <CircularProgress size={20} />,
              }}
              onBlur={validateOpenAI}
            />
          </Box>

          {state.services.openai?.isValid && (
            <Alert severity="success" sx={{ mt: 2 }}>
              OpenAI credentials validated successfully
            </Alert>
          )}
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="h6">Zendesk Integration</Typography>
            <Tooltip title="Optional: Configure Zendesk for ticket creation">
              <IconButton size="small">
                <HelpIcon />
              </IconButton>
            </Tooltip>
          </Box>

          <FormControlLabel
            control={
              <Switch
                checked={state.services.zendesk?.enabled || false}
                onChange={e =>
                  dispatch({
                    type: 'UPDATE_SERVICES',
                    services: {
                      zendesk: {
                        ...state.services.zendesk,
                        enabled: e.target.checked,
                      },
                    },
                  })
                }
              />
            }
            label="Enable Zendesk Integration"
          />

          {state.services.zendesk?.enabled && (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mt: 2 }}>
              <Box sx={{ flex: '1 1 300px' }}>
                <TextField
                  fullWidth
                  label="API Token"
                  type="password"
                  value={state.services.zendesk?.apiToken || ''}
                  onChange={e =>
                    dispatch({
                      type: 'UPDATE_SERVICES',
                      services: {
                        zendesk: {
                          ...state.services.zendesk,
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
              </Box>

              <Box sx={{ flex: '1 1 300px' }}>
                <TextField
                  fullWidth
                  label="Subdomain"
                  value={state.services.zendesk?.subdomain || ''}
                  onChange={e =>
                    dispatch({
                      type: 'UPDATE_SERVICES',
                      services: {
                        zendesk: {
                          ...state.services.zendesk,
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
              </Box>
            </Box>
          )}

          {state.services.zendesk?.enabled && state.services.zendesk?.isValid && (
            <Alert severity="success" sx={{ mt: 2 }}>
              Zendesk credentials validated successfully
            </Alert>
          )}
        </Paper>
      </Box>
    </Box>
  );
}
