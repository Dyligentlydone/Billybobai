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
import { VoiceNodeData } from '../../../types/voice';

interface NodeProps {
  data: VoiceNodeData;
  selected: boolean;
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
export const MenuNode: React.FC<NodeProps> = ({ data, selected }) => (
  <Card sx={{ ...nodeStyles, ...(selected ? selectedStyles : {}) }}>
    <Handle type="target" position={Position.Top} />
    <CardContent>
      <Box display="flex" alignItems="center" gap={1} mb={1}>
        <MenuIcon color="primary" />
        <Typography variant="subtitle1">{data.label}</Typography>
      </Box>
      <Typography variant="body2" color="textSecondary" mb={1}>
        {data.prompt}
      </Typography>
      <List dense>
        {data.options?.map((option) => (
          <ListItem key={option.digit}>
            <ListItemText
              primary={`${option.digit}: ${option.description}`}
            />
          </ListItem>
        ))}
      </List>
    </CardContent>
    <Handle type="source" position={Position.Bottom} />
  </Card>
);

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
        {data.schedule && Object.entries(data.schedule).map(([day, hours]) => (
          <ListItem key={day}>
            <ListItemText
              primary={`${day}: ${hours.start} - ${hours.end}`}
            />
          </ListItem>
        ))}
      </List>
    </CardContent>
    <Handle type="source" position={Position.Bottom} />
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
        {data.conditions?.map((condition, index) => (
          <ListItem key={index}>
            <ListItemText
              primary={`${condition.type} ${condition.operator} ${condition.value}`}
            />
          </ListItem>
        ))}
      </List>
    </CardContent>
    <Handle type="source" position={Position.Bottom} />
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
