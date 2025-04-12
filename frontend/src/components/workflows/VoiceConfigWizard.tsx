import React, { useState } from 'react';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import ReactFlow, { 
  Background, 
  Controls,
  Node,
  Connection,
  addEdge,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Box,
  Select,
  MenuItem,
  IconButton,
  Grid,
  Tab,
  Tabs,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  FormControlLabel,
  Switch,
  styled,
} from '@mui/material';
import { GridProps, Theme } from '@mui/material';
import { SxProps } from '@mui/system';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { VoiceConfig, VoiceNodeData } from '../../types/voice';
import {
  MenuNode,
  MessageNode,
  TransferNode,
  VoicemailNode,
  HoursNode,
  ConditionNode,
  EndNode,
} from './nodes/VoiceNodes';

// Node types for React Flow
const nodeTypes = {
  menu: MenuNode,
  message: MessageNode,
  transfer: TransferNode,
  voicemail: VoicemailNode,
  hours: HoursNode,
  condition: ConditionNode,
  end: EndNode,
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} style={{ width: '100%' }}>
    {value === index && children}
  </div>
);

interface NodeConfigDialogProps {
  open: boolean;
  node: VoiceNodeData | null;
  onClose: () => void;
  onSave: (nodeData: VoiceNodeData) => void;
}

const NodeConfigDialog: React.FC<NodeConfigDialogProps> = ({
  open,
  node,
  onClose,
  onSave,
}) => {
  const { control, handleSubmit } = useForm<VoiceNodeData>({
    defaultValues: node || undefined,
  });

  const onSubmit = handleSubmit((data) => {
    onSave(data);
    onClose();
  });

  if (!node) return null;

  const handleAddMenuOption = () => {
    const currentOptions = (control as any)._formValues.options || [];
    const newOptions = [
      ...currentOptions,
      {
        digit: String(currentOptions.length + 1),
        description: '',
        nextNodeId: '',
      },
    ];
    (control as any)._fields.options._f.value = newOptions;
  };

  const handleRemoveMenuOption = (index: number) => {
    const currentOptions = (control as any)._formValues.options || [];
    const newOptions = currentOptions.filter((_: unknown, i: number) => i !== index);
    (control as any)._fields.options._f.value = newOptions;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Configure {node.type.charAt(0).toUpperCase() + node.type.slice(1)} Node</DialogTitle>
      <DialogContent>
        <form onSubmit={onSubmit}>
          <TextField
            fullWidth
            label="Node Label"
            name="label"
            defaultValue={node.label}
            sx={{ mt: 2 }}
          />
          {node.type === 'menu' && (
            <>
              <Controller
                name="prompt"
                control={control}
                defaultValue={node.prompt || 'Welcome to our menu. Please select from the following options:'}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Menu Prompt"
                    sx={{ mt: 2 }}
                    multiline
                    rows={2}
                    helperText="This is what will be spoken before listing the menu options"
                  />
                )}
              />
              
              <Typography variant="subtitle1" sx={{ mt: 3, mb: 1 }}>
                Menu Options
              </Typography>
              
              <Controller
                name="options"
                control={control}
                defaultValue={node.options || []}
                render={({ field }) => (
                  <>
                    {Array.from(field.value || []).map((option: { digit: string; description: string }, index: number) => (
                      <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
                        <TextField
                          label="Key"
                          value={option.digit}
                          onChange={(e) => {
                            const newOptions = Array.from(field.value || []);
                            newOptions[index] = {
                              ...newOptions[index],
                              digit: e.target.value,
                            };
                            field.onChange(newOptions);
                          }}
                          sx={{ width: '80px' }}
                        />
                        <TextField
                          fullWidth
                          label="Description"
                          value={option.description}
                          onChange={(e) => {
                            const newOptions = Array.from(field.value || []);
                            newOptions[index] = {
                              ...newOptions[index],
                              description: e.target.value,
                            };
                            field.onChange(newOptions);
                          }}
                        />
                        <IconButton
                          onClick={() => handleRemoveMenuOption(index)}
                          color="error"
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    ))}
                    <Button
                      startIcon={<AddIcon />}
                      onClick={handleAddMenuOption}
                      variant="outlined"
                      size="small"
                      sx={{ mt: 1 }}
                    >
                      Add Option
                    </Button>
                  </>
                )}
              />
            </>
          )}
          {node.type === 'message' && (
            <Controller
              name="aiModel"
              control={control}
              defaultValue={node.aiModel || 'gpt-4'}
              render={({ field }) => (
                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>AI Model</InputLabel>
                  <Select {...field} label="AI Model">
                    <MenuItem value="gpt-4">GPT-4</MenuItem>
                    <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                  </Select>
                </FormControl>
              )}
            />
          )}
          {node.type === 'transfer' && (
            <Controller
              name="transferNumber"
              control={control}
              defaultValue={node.transferNumber || ''}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Transfer Number"
                  sx={{ mt: 2 }}
                />
              )}
            />
          )}
        </form>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={onSubmit} variant="contained" color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

interface VoiceConfigWizardProps {
  onComplete: (config: VoiceConfig) => void;
  onCancel: () => void;
}

export const VoiceConfigWizard: React.FC<VoiceConfigWizardProps> = ({
  onComplete,
  onCancel,
}) => {
  // Form state
  const { control, handleSubmit } = useForm<VoiceConfig>({
    defaultValues: {
      business: {
        name: '',
        phone: '',
        timezone: 'America/Los_Angeles',
      },
      integration: {
        twilio: {
          accountSid: '',
          authToken: '',
          phoneNumber: '',
        },
        openai: {
          apiKey: '',
        },
      },
      callFlow: {
        greeting: {
          enabled: true,
          message: 'Thank you for calling. We are excited to assist you today.',
          voiceSettings: {
            language: 'en-US',
            gender: 'female',
            speed: 'normal',
            voice: 'woman',
          },
        },
        mainMenu: {
          prompt: 'Please select from the following options:',
          options: [],
          voiceSettings: {
            language: 'en-US',
            gender: 'female',
            speed: 'normal',
            voice: 'woman',
          },
        },
        fallback: {
          message: 'I apologize, but I did not understand your response. Please try again.',
          action: 'transfer',
          voiceSettings: {
            language: 'en-US',
            gender: 'female',
            speed: 'normal',
            voice: 'woman',
          },
        },
        businessHours: {
          enabled: false,
          timezone: 'America/Los_Angeles',
          hours: {},
          outOfHoursMessage: 'We are currently closed. Please call back during business hours.',
          voiceSettings: {
            language: 'en-US',
            gender: 'female',
            speed: 'normal',
            voice: 'woman',
          },
        },
        defaultVoiceSettings: {
          language: 'en-US',
          gender: 'female',
          speed: 'normal',
          voice: 'woman',
        },
      },
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'callFlow.mainMenu.options',
  });

  // Tab state
  const [activeTab, setActiveTab] = useState(0);

  // Workflow state
  const [nodes, setNodes, onNodesChange] = useNodesState<VoiceNodeData>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<VoiceNodeData | null>(null);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);

  // Handle tab change
  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Add workflow node
  const addNode = (type: string) => {
    const newNode: Node<VoiceNodeData> = {
      id: `node_${nodes.length + 1}`,
      type,
      position: { x: 100, y: 100 + nodes.length * 100 },
      data: {
        label: `${type.charAt(0).toUpperCase() + type.slice(1)} Node`,
        type: type as VoiceNodeData['type'],
        options: type === 'menu' ? [] : undefined,
      },
    };
    setNodes([...nodes, newNode]);
    setSelectedNode(newNode.data);
    setConfigDialogOpen(true);
  };

  // Handle node click
  const onNodeClick = (_: React.MouseEvent, node: Node<VoiceNodeData>) => {
    setSelectedNode(node.data);
    setConfigDialogOpen(true);
  };

  // Handle node configuration save
  const onNodeConfigSave = (nodeData: VoiceNodeData) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.data.label === nodeData.label) {
          node.data = nodeData;
        }
        return node;
      })
    );
  };

  // Handle edge connections
  const onConnect = (connection: Connection) => {
    setEdges((eds) => addEdge(connection, eds));
  };

  // Form submission
  const onSubmit = async (data: VoiceConfig) => {
    try {
      // Add workflow data to config
      const configWithWorkflow = {
        ...data,
        workflow: {
          nodes,
          edges,
        },
      };
      onComplete(configWithWorkflow);
    } catch (error) {
      console.error('Error saving voice configuration:', error);
    }
  };

  // Create properly typed Grid components
  interface ExtendedGridProps extends GridProps {
    item?: boolean;
    container?: boolean;
    xs?: number;
    spacing?: number;
    sx?: SxProps<Theme>;
  }

  const StyledGrid = styled(Grid)<ExtendedGridProps>({});

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Basic Settings" />
          <Tab label="Menu Options" />
          <Tab label="Call Flow" />
        </Tabs>
      </Box>

      <TabPanel value={activeTab} index={0}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Business Configuration
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Controller
                name="business.name"
                control={control}
                rules={{ required: 'Business name is required' }}
                render={({ field, fieldState: { error } }) => (
                  <TextField
                    {...field}
                    label="Business Name"
                    error={!!error}
                    helperText={error?.message}
                  />
                )}
              />

              <Controller
                name="business.phone"
                control={control}
                rules={{ required: 'Phone number is required' }}
                render={({ field, fieldState: { error } }) => (
                  <TextField
                    {...field}
                    label="Business Phone"
                    error={!!error}
                    helperText={error?.message}
                  />
                )}
              />

              <Controller
                name="business.timezone"
                control={control}
                rules={{ required: 'Timezone is required' }}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Timezone</InputLabel>
                    <Select {...field} label="Timezone">
                      <MenuItem value="America/New_York">America/New_York</MenuItem>
                      <MenuItem value="America/Chicago">America/Chicago</MenuItem>
                      <MenuItem value="America/Denver">America/Denver</MenuItem>
                      <MenuItem value="America/Los_Angeles">America/Los_Angeles</MenuItem>
                      <MenuItem value="America/Phoenix">America/Phoenix</MenuItem>
                      <MenuItem value="America/Anchorage">America/Anchorage</MenuItem>
                      <MenuItem value="Pacific/Honolulu">Pacific/Honolulu</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />

              <Typography variant="h6" sx={{ mt: 2 }}>
                Greeting Configuration
              </Typography>
              
              <Controller
                name="callFlow.greeting.enabled"
                control={control}
                render={({ field: { value, onChange } }) => (
                  <FormControlLabel
                    control={
                      <Switch
                        checked={value}
                        onChange={(e) => onChange(e.target.checked)}
                      />
                    }
                    label="Enable Greeting Message"
                  />
                )}
              />

              <Controller
                name="callFlow.greeting.message"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    multiline
                    rows={2}
                    label="Greeting Message"
                    fullWidth
                    disabled={!control._formValues.callFlow.greeting.enabled}
                    helperText="This message will be played when someone calls"
                  />
                )}
              />

              <Typography variant="subtitle1" sx={{ mt: 1 }}>
                Voice Settings
              </Typography>

              <StyledGrid container spacing={2}>
                <StyledGrid item xs={6}>
                  <Controller
                    name="callFlow.greeting.voiceSettings.language"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth disabled={!control._formValues.callFlow.greeting.enabled}>
                        <InputLabel>Language</InputLabel>
                        <Select {...field} label="Language">
                          <MenuItem value="en-US">English (US)</MenuItem>
                          <MenuItem value="en-GB">English (UK)</MenuItem>
                          <MenuItem value="es-ES">Spanish</MenuItem>
                          <MenuItem value="fr-FR">French</MenuItem>
                          <MenuItem value="de-DE">German</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  />
                </StyledGrid>
                <StyledGrid item xs={3}>
                  <Controller
                    name="callFlow.greeting.voiceSettings.gender"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth disabled={!control._formValues.callFlow.greeting.enabled}>
                        <InputLabel>Voice Gender</InputLabel>
                        <Select {...field} label="Voice Gender">
                          <MenuItem value="male">Male</MenuItem>
                          <MenuItem value="female">Female</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  />
                </StyledGrid>
                <StyledGrid item xs={3}>
                  <Controller
                    name="callFlow.greeting.voiceSettings.speed"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth disabled={!control._formValues.callFlow.greeting.enabled}>
                        <InputLabel>Voice Speed</InputLabel>
                        <Select {...field} label="Voice Speed">
                          <MenuItem value="slow">Slow</MenuItem>
                          <MenuItem value="normal">Normal</MenuItem>
                          <MenuItem value="fast">Fast</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  />
                </StyledGrid>
              </StyledGrid>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Integration Settings
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Typography variant="h6" gutterBottom>
                Twilio Configuration
              </Typography>
              <Controller
                name="integration.twilio.accountSid"
                control={control}
                rules={{ required: 'Twilio Account SID is required' }}
                render={({ field, fieldState: { error } }) => (
                  <TextField
                    {...field}
                    label="Account SID"
                    error={!!error}
                    helperText={error?.message || 'Find this in your Twilio Console'}
                    fullWidth
                  />
                )}
              />

              <Controller
                name="integration.twilio.authToken"
                control={control}
                rules={{ required: 'Twilio Auth Token is required' }}
                render={({ field, fieldState: { error } }) => (
                  <TextField
                    {...field}
                    type="password"
                    label="Auth Token"
                    error={!!error}
                    helperText={error?.message || 'Find this in your Twilio Console'}
                    fullWidth
                  />
                )}
              />

              <Controller
                name="integration.twilio.phoneNumber"
                control={control}
                rules={{ required: 'Twilio Phone Number is required' }}
                render={({ field, fieldState: { error } }) => (
                  <TextField
                    {...field}
                    label="Phone Number"
                    error={!!error}
                    helperText={error?.message || 'The Twilio number to use for calls'}
                    fullWidth
                  />
                )}
              />

              <Typography variant="h6" sx={{ mt: 2 }}>
                OpenAI Configuration
              </Typography>
              <Controller
                name="integration.openai.apiKey"
                control={control}
                rules={{ required: 'OpenAI API Key is required' }}
                render={({ field, fieldState: { error } }) => (
                  <TextField
                    {...field}
                    type="password"
                    label="API Key"
                    error={!!error}
                    helperText={error?.message || 'Your OpenAI API key for AI responses'}
                    fullWidth
                  />
                )}
              />
            </Box>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Menu Options
            </Typography>
            {fields.map((field, index) => (
              <StyledGrid container spacing={2} key={field.id}>
                <StyledGrid item xs={1}>
                  <Controller
                    name={`callFlow.mainMenu.options.${index}.digit`}
                    control={control}
                    rules={{ required: 'Required' }}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Key"
                        size="small"
                        inputProps={{ maxLength: 1 }}
                      />
                    )}
                  />
                </StyledGrid>
                <StyledGrid item xs={6}>
                  <Controller
                    name={`callFlow.mainMenu.options.${index}.description`}
                    control={control}
                    rules={{ required: 'Description is required' }}
                    render={({ field, fieldState: { error } }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Description"
                        error={!!error}
                        helperText={error?.message}
                        size="small"
                      />
                    )}
                  />
                </StyledGrid>
                <StyledGrid item xs={4}>
                  <Controller
                    name={`callFlow.mainMenu.options.${index}.action`}
                    control={control}
                    rules={{ required: 'Action is required' }}
                    render={({ field }) => (
                      <Select {...field} fullWidth size="small" label="Action">
                        <MenuItem value="message">AI Response</MenuItem>
                        <MenuItem value="transfer">Transfer to Agent</MenuItem>
                        <MenuItem value="voicemail">Leave Voicemail</MenuItem>
                      </Select>
                    )}
                  />
                </StyledGrid>
                <StyledGrid item xs={1}>
                  <IconButton 
                    onClick={() => remove(index)}
                    color="error"
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                </StyledGrid>
              </StyledGrid>
            ))}
            <Button
              startIcon={<AddIcon />}
              onClick={() => append({
                digit: String(fields.length + 1),
                description: '',
                action: 'message' as const,
              })}
              variant="outlined"
              sx={{ mt: 1 }}
            >
              Add Menu Option
            </Button>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Call Flow Builder
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => addNode('menu')}
                sx={{ mr: 1 }}
              >
                Add Menu
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => addNode('message')}
                sx={{ mr: 1 }}
              >
                Add AI Response
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => addNode('transfer')}
                sx={{ mr: 1 }}
              >
                Add Transfer
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => addNode('voicemail')}
                sx={{ mr: 1 }}
              >
                Add Voicemail
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => addNode('hours')}
                sx={{ mr: 1 }}
              >
                Add Hours Check
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => addNode('condition')}
                sx={{ mr: 1 }}
              >
                Add Condition
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => addNode('end')}
              >
                Add End
              </Button>
            </Box>
            <Box sx={{ height: 500, border: '1px solid #ccc' }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onNodeClick={onNodeClick}
                nodeTypes={nodeTypes}
                fitView
              >
                <Background />
                <Controls />
              </ReactFlow>
            </Box>
          </CardContent>
        </Card>

        <NodeConfigDialog
          open={configDialogOpen}
          node={selectedNode}
          onClose={() => setConfigDialogOpen(false)}
          onSave={onNodeConfigSave}
        />
      </TabPanel>

      <Box sx={{ mt: 2, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button onClick={onCancel}>Cancel</Button>
        <Button variant="contained" type="submit">
          Save Configuration
        </Button>
      </Box>
    </form>
  );
};
