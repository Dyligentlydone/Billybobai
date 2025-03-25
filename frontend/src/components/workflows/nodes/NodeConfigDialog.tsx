import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Grid,
  IconButton,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { VoiceNodeData } from '../../../types/voice';

interface NodeConfigDialogProps {
  open: boolean;
  node: VoiceNodeData | null;
  onClose: () => void;
  onSave: (nodeData: VoiceNodeData) => void;
}

export const NodeConfigDialog: React.FC<NodeConfigDialogProps> = ({
  open,
  node,
  onClose,
  onSave,
}) => {
  const [data, setData] = React.useState<VoiceNodeData | null>(null);

  React.useEffect(() => {
    setData(node);
  }, [node]);

  if (!data) return null;

  const handleSave = () => {
    if (data) {
      onSave(data);
      onClose();
    }
  };

  const handleAddMenuOption = () => {
    if (data.options) {
      setData({
        ...data,
        options: [
          ...data.options,
          {
            digit: String(data.options.length + 1),
            description: '',
            nextNodeId: '',
          },
        ],
      });
    }
  };

  const handleRemoveMenuOption = (index: number) => {
    if (data.options) {
      setData({
        ...data,
        options: data.options.filter((_, i) => i !== index),
      });
    }
  };

  const renderFields = () => {
    switch (data.type) {
      case 'menu':
        return (
          <>
            <TextField
              fullWidth
              label="Menu Prompt"
              value={data.prompt || ''}
              onChange={(e) => setData({ ...data, prompt: e.target.value })}
              margin="normal"
              multiline
              rows={2}
            />
            <Box sx={{ mt: 2 }}>
              {data.options?.map((option, index) => (
                <Grid container spacing={2} key={index} sx={{ mb: 1 }}>
                  <Grid item xs={2}>
                    <TextField
                      fullWidth
                      label="Key"
                      value={option.digit}
                      onChange={(e) =>
                        setData({
                          ...data,
                          options: data.options?.map((opt, i) =>
                            i === index ? { ...opt, digit: e.target.value } : opt
                          ),
                        })
                      }
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={8}>
                    <TextField
                      fullWidth
                      label="Description"
                      value={option.description}
                      onChange={(e) =>
                        setData({
                          ...data,
                          options: data.options?.map((opt, i) =>
                            i === index ? { ...opt, description: e.target.value } : opt
                          ),
                        })
                      }
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={2}>
                    <IconButton
                      onClick={() => handleRemoveMenuOption(index)}
                      color="error"
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Grid>
                </Grid>
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
            </Box>
          </>
        );

      case 'message':
        return (
          <>
            <FormControl fullWidth margin="normal">
              <InputLabel>AI Model</InputLabel>
              <Select
                value={data.aiModel || 'gpt-4'}
                onChange={(e) => setData({ ...data, aiModel: e.target.value })}
                label="AI Model"
              >
                <MenuItem value="gpt-4">GPT-4</MenuItem>
                <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Max Tokens"
              type="number"
              value={data.maxTokens || 100}
              onChange={(e) => setData({ ...data, maxTokens: Number(e.target.value) })}
              margin="normal"
            />
          </>
        );

      case 'transfer':
        return (
          <TextField
            fullWidth
            label="Transfer Number"
            value={data.transferNumber || ''}
            onChange={(e) => setData({ ...data, transferNumber: e.target.value })}
            margin="normal"
          />
        );

      case 'voicemail':
        return (
          <>
            <TextField
              fullWidth
              label="Max Duration (seconds)"
              type="number"
              value={data.maxDuration || 300}
              onChange={(e) => setData({ ...data, maxDuration: Number(e.target.value) })}
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Transcribe</InputLabel>
              <Select
                value={data.transcribe || false}
                onChange={(e) => setData({ ...data, transcribe: Boolean(e.target.value) })}
                label="Transcribe"
              >
                <MenuItem value="true">Yes</MenuItem>
                <MenuItem value="false">No</MenuItem>
              </Select>
            </FormControl>
          </>
        );

      case 'hours':
        return (
          <>
            <FormControl fullWidth margin="normal">
              <InputLabel>Timezone</InputLabel>
              <Select
                value={data.timezone || 'America/New_York'}
                onChange={(e) => setData({ ...data, timezone: e.target.value })}
                label="Timezone"
              >
                <MenuItem value="America/New_York">Eastern Time</MenuItem>
                <MenuItem value="America/Chicago">Central Time</MenuItem>
                <MenuItem value="America/Denver">Mountain Time</MenuItem>
                <MenuItem value="America/Los_Angeles">Pacific Time</MenuItem>
              </Select>
            </FormControl>
          </>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Configure {data.type.charAt(0).toUpperCase() + data.type.slice(1)} Node</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Node Label"
          value={data.label}
          onChange={(e) => setData({ ...data, label: e.target.value })}
          margin="normal"
        />
        {renderFields()}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};
