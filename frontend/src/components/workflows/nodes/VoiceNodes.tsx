import React from 'react';
import { Handle, Position } from 'reactflow';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  Box,
  Chip,
} from '@mui/material';
import {
  Phone as PhoneIcon,
  Message as MessageIcon,
  Voicemail as VoicemailIcon,
  AccessTime as TimeIcon,
  CallSplit as SplitIcon,
  Stop as StopIcon,
  Menu as MenuIcon,
} from '@mui/icons-material';
import { VoiceNodeData, MenuNodeData } from '../../../types/voice';

interface NodeProps {
  data: VoiceNodeData;
  selected: boolean;
}

interface BusinessHours {
  day: string;
  start: string;
  end: string;
}

interface Condition {
  type: string;
  operator: string;
  value: string;
  nextNodeId: string;
}

const nodeStyles = {
  minWidth: 200,
  maxWidth: 300,
  padding: 1,
  border: '1px solid #ccc',
  borderRadius: 2,
  backgroundColor: '#fff',
};

const selectedStyles = {
  boxShadow: '0 0 0 2px #1976d2',
};

// Menu Node
export const MenuNode: React.FC<NodeProps> = ({ data, selected }) => {
  const menuData = data as MenuNodeData;
  
  return (
    <Card sx={{ ...nodeStyles, ...(selected ? selectedStyles : {}) }}>
      <Handle type="target" position={Position.Top} />
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <MenuIcon color="primary" />
          <Typography variant="subtitle1">{menuData.label}</Typography>
        </Box>
        
        {/* Prompt and Configuration */}
        <Box mb={2}>
          <Typography variant="body2" color="textSecondary">
            {menuData.prompt}
          </Typography>
          <Box mt={1} display="flex" gap={1} flexWrap="wrap">
            <Chip
              size="small"
              label={`Timeout: ${menuData.timeoutSeconds}s`}
            />
            <Chip
              size="small"
              label={`Retries: ${menuData.maxRetries}`}
            />
            <Chip
              size="small"
              label={`Input: ${menuData.gatherConfig?.numDigits ?? 1} digit(s)`}
            />
          </Box>
        </Box>

        {/* Menu Options */}
        <List dense>
          {menuData.options?.map((option) => (
            <ListItem 
              key={option.digit}
              secondaryAction={
                <Chip
                  size="small"
                  variant="outlined"
                  label={`→ ${option.nextNodeId}`}
                />
              }
            >
              <ListItemText
                primary={`${option.digit}: ${option.description}`}
              />
            </ListItem>
          ))}
        </List>

        {/* Error Handling */}
        <Box mt={2} pt={1} borderTop={1} borderColor="divider">
          <Typography variant="caption" color="textSecondary" display="block">
            Invalid Input: {menuData.invalidInputAction} 
            {menuData.invalidInputAction === 'default' && 
              ` → ${menuData.defaultRouteNodeId}`}
          </Typography>
          <Typography variant="caption" color="textSecondary" display="block">
            Timeout: {menuData.timeoutMessage ? 'Custom message' : 'Default'}
          </Typography>
        </Box>
      </CardContent>

      {/* Dynamic output handles for each option */}
      {menuData.options?.map((option) => (
        <Handle
          key={option.digit}
          type="source"
          position={Position.Bottom}
          id={`option-${option.digit}`}
          style={{
            left: `${(parseInt(option.digit) / (menuData.options?.length || 1)) * 100}%`,
          }}
        />
      ))}
      
      {/* Default route handle */}
      {menuData.defaultRouteNodeId && (
        <Handle
          type="source"
          position={Position.Right}
          id="default-route"
          style={{ top: '50%' }}
        />
      )}
    </Card>
  );
};

// Message Node (AI Response)
export const MessageNode: React.FC<NodeProps> = ({ data, selected }) => (
  <Card sx={{ ...nodeStyles, ...(selected ? selectedStyles : {}) }}>
    <Handle type="target" position={Position.Top} />
    <CardContent>
      <Box display="flex" alignItems="center" gap={1}>
        <MessageIcon color="primary" />
        <Typography variant="subtitle1">{data.label}</Typography>
      </Box>
      <Box mt={1}>
        <Chip
          size="small"
          label={`Model: ${data.aiModel}`}
          sx={{ mr: 1 }}
        />
        <Chip
          size="small"
          label={`Max Tokens: ${data.maxTokens}`}
        />
      </Box>
    </CardContent>
    <Handle type="source" position={Position.Bottom} />
  </Card>
);

// Transfer Node
export const TransferNode: React.FC<NodeProps> = ({ data, selected }) => (
  <Card sx={{ ...nodeStyles, ...(selected ? selectedStyles : {}) }}>
    <Handle type="target" position={Position.Top} />
    <CardContent>
      <Box display="flex" alignItems="center" gap={1}>
        <PhoneIcon color="primary" />
        <Typography variant="subtitle1">{data.label}</Typography>
      </Box>
      <Typography variant="body2" color="textSecondary" mt={1}>
        Transfer to: {data.transferNumber}
      </Typography>
    </CardContent>
    <Handle type="source" position={Position.Bottom} />
  </Card>
);

// Voicemail Node
export const VoicemailNode: React.FC<NodeProps> = ({ data, selected }) => (
  <Card sx={{ ...nodeStyles, ...(selected ? selectedStyles : {}) }}>
    <Handle type="target" position={Position.Top} />
    <CardContent>
      <Box display="flex" alignItems="center" gap={1}>
        <VoicemailIcon color="primary" />
        <Typography variant="subtitle1">{data.label}</Typography>
      </Box>
      <Box mt={1}>
        <Chip
          size="small"
          label={`Max Duration: ${data.maxDuration}s`}
          sx={{ mr: 1 }}
        />
        <Chip
          size="small"
          label={data.transcribe ? 'Transcribe' : 'No Transcription'}
        />
      </Box>
    </CardContent>
    <Handle type="source" position={Position.Bottom} />
  </Card>
);

// Hours Node
export const HoursNode: React.FC<NodeProps> = ({ data, selected }) => (
  <Card sx={{ ...nodeStyles, ...(selected ? selectedStyles : {}) }}>
    <Handle type="target" position={Position.Top} />
    <CardContent>
      <Box display="flex" alignItems="center" gap={1}>
        <TimeIcon color="primary" />
        <Typography variant="subtitle1">{data.label}</Typography>
      </Box>
      <Typography variant="body2" color="textSecondary" mt={1}>
        Timezone: {data.timezone}
      </Typography>
      <List dense>
        {data.schedule?.map((hours: BusinessHours) => (
          <ListItem key={hours.day}>
            <ListItemText
              primary={`${hours.day}: ${hours.start} - ${hours.end}`}
            />
          </ListItem>
        ))}
      </List>
    </CardContent>
    <Handle 
      type="source" 
      position={Position.Bottom} 
      id="in-hours"
    />
    <Handle 
      type="source" 
      position={Position.Right} 
      id="out-of-hours"
      style={{ top: '50%' }}
    />
  </Card>
);

// Condition Node
export const ConditionNode: React.FC<NodeProps> = ({ data, selected }) => (
  <Card sx={{ ...nodeStyles, ...(selected ? selectedStyles : {}) }}>
    <Handle type="target" position={Position.Top} />
    <CardContent>
      <Box display="flex" alignItems="center" gap={1}>
        <SplitIcon color="primary" />
        <Typography variant="subtitle1">{data.label}</Typography>
      </Box>
      <List dense>
        {data.conditions?.map((condition: Condition, index: number) => (
          <ListItem 
            key={index}
            secondaryAction={
              <Chip
                size="small"
                variant="outlined"
                label={`→ ${condition.nextNodeId}`}
              />
            }
          >
            <ListItemText
              primary={`${condition.type} ${condition.operator} ${condition.value}`}
            />
          </ListItem>
        ))}
      </List>
    </CardContent>
    {/* Dynamic output handles for each condition */}
    {data.conditions?.map((condition: Condition, index: number) => (
      <Handle
        key={condition.nextNodeId}
        type="source"
        position={Position.Bottom}
        id={`condition-${index}`}
        style={{
          left: `${((index + 1) / ((data.conditions?.length || 1) + 1)) * 100}%`,
        }}
      />
    ))}
  </Card>
);

// End Node
export const EndNode: React.FC<NodeProps> = ({ data, selected }) => (
  <Card sx={{ ...nodeStyles, ...(selected ? selectedStyles : {}) }}>
    <Handle type="target" position={Position.Top} />
    <CardContent>
      <Box display="flex" alignItems="center" gap={1}>
        <StopIcon color="error" />
        <Typography variant="subtitle1">{data.label}</Typography>
      </Box>
    </CardContent>
  </Card>
);
