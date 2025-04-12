import React from 'react';
import { 
  Grid,
  TextField, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Button, 
  Box, 
  Typography, 
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  styled
} from '@mui/material';
import { GridProps, Theme } from '@mui/material';
import { SxProps } from '@mui/system';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';

// Create properly typed Grid components
interface ExtendedGridProps extends GridProps {
  item?: boolean;
  container?: boolean;
  xs?: number;
  spacing?: number;
  sx?: SxProps<Theme>;
}

const StyledGrid = styled(Grid)<ExtendedGridProps>({});

interface MenuOption {
  key: string;
  description: string;
  nextNodeId: string;
}

interface NodeData {
  type: string;
  label: string;
  prompt?: string;
  options?: MenuOption[];
  inputLength?: number;
  inputTimeout?: number;
  invalidInputMessage?: string;
  invalidInputAction?: 'repeat' | 'default';
  defaultRouteNodeId?: string;
}

interface NodeConfigDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: NodeData) => void;
  node: NodeData;
}

export const NodeConfigDialog: React.FC<NodeConfigDialogProps> = ({ 
  open, 
  onClose, 
  onSave, 
  node 
}) => {
  const [data, setData] = React.useState<NodeData>(node);

  React.useEffect(() => {
    if (node.type === 'menu') {
      setData({
        ...node,
        prompt: node.prompt || 'Welcome to our menu. Please select from the following options:',
        options: node.options || [],
        inputLength: node.inputLength || 1,
        inputTimeout: node.inputTimeout || 5,
        invalidInputMessage: node.invalidInputMessage || 'Sorry, that was not a valid option.',
        invalidInputAction: node.invalidInputAction || 'repeat',
      });
    } else {
      setData(node);
    }
  }, [node]);

  const handleAddMenuOption = () => {
    setData({
      ...data,
      options: [
        ...(data.options || []),
        { key: '', description: '', nextNodeId: '' }
      ]
    });
  };

  const handleRemoveMenuOption = (index: number) => {
    const newOptions = [...(data.options || [])];
    newOptions.splice(index, 1);
    setData({ ...data, options: newOptions });
  };

  const handleSave = () => {
    onSave(data);
    onClose();
  };

  const renderFields = () => {
    switch (data.type) {
      case 'menu':
        return (
          <StyledGrid container spacing={2}>
            <StyledGrid item xs={12}>
              <StyledGrid container spacing={2}>
                <StyledGrid item xs={12}>
                  <TextField
                    fullWidth
                    label="Menu Prompt"
                    value={data.prompt || ''}
                    onChange={(e) => setData({ ...data, prompt: e.target.value })}
                    margin="normal"
                    multiline
                    rows={2}
                  />
                </StyledGrid>
              </StyledGrid>

              {/* Input Settings */}
              <StyledGrid container spacing={2} sx={{ mt: 1 }}>
                <StyledGrid item xs={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Input Length"
                    value={data.inputLength || 1}
                    onChange={(e) => setData({ ...data, inputLength: Number(e.target.value) })}
                    size="small"
                  />
                </StyledGrid>
                <StyledGrid item xs={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Input Timeout"
                    value={data.inputTimeout || 5}
                    onChange={(e) => setData({ ...data, inputTimeout: Number(e.target.value) })}
                    size="small"
                  />
                </StyledGrid>
                <StyledGrid item xs={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Invalid Input Action</InputLabel>
                    <Select
                      value={data.invalidInputAction || 'repeat'}
                      onChange={(e) => setData({ ...data, invalidInputAction: e.target.value as 'repeat' | 'default' })}
                      label="Invalid Input Action"
                    >
                      <MenuItem value="repeat">Repeat</MenuItem>
                      <MenuItem value="default">Default Route</MenuItem>
                    </Select>
                  </FormControl>
                </StyledGrid>
              </StyledGrid>
            </StyledGrid>

            {/* Error Messages */}
            <StyledGrid container spacing={2} sx={{ mt: 1 }}>
              <StyledGrid item xs={12}>
                <TextField
                  fullWidth
                  label="Invalid Input Message"
                  value={data.invalidInputMessage || ''}
                  onChange={(e) => setData({ ...data, invalidInputMessage: e.target.value })}
                  size="small"
                />
              </StyledGrid>
            </StyledGrid>

            {/* Menu Options */}
            <StyledGrid container spacing={2}>
              <StyledGrid item xs={12}>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Menu Options
                  </Typography>
                  {data.options?.map((option, index) => (
                    <StyledGrid container spacing={2} sx={{ mb: 1 }} key={index}>
                      <StyledGrid item xs={2}>
                        <TextField
                          fullWidth
                          label="Key"
                          value={option.key}
                          onChange={(e) => {
                            const newOptions = [...(data.options || [])];
                            newOptions[index] = { ...option, key: e.target.value };
                            setData({ ...data, options: newOptions });
                          }}
                          size="small"
                        />
                      </StyledGrid>
                      <StyledGrid item xs={7}>
                        <TextField
                          fullWidth
                          label="Description"
                          value={option.description}
                          onChange={(e) => {
                            const newOptions = [...(data.options || [])];
                            newOptions[index] = { ...option, description: e.target.value };
                            setData({ ...data, options: newOptions });
                          }}
                          size="small"
                        />
                      </StyledGrid>
                      <StyledGrid item xs={2}>
                        <TextField
                          fullWidth
                          label="Next Node"
                          value={option.nextNodeId}
                          onChange={(e) => {
                            const newOptions = [...(data.options || [])];
                            newOptions[index] = { ...option, nextNodeId: e.target.value };
                            setData({ ...data, options: newOptions });
                          }}
                          size="small"
                        />
                      </StyledGrid>
                      <StyledGrid item xs={1}>
                        <IconButton
                          onClick={() => handleRemoveMenuOption(index)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </StyledGrid>
                    </StyledGrid>
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
              </StyledGrid>
            </StyledGrid>

            {/* Default Route */}
            {data.invalidInputAction === 'default' && (
              <StyledGrid container spacing={2}>
                <StyledGrid item xs={12}>
                  <TextField
                    fullWidth
                    label="Default Route Node ID"
                    value={data.defaultRouteNodeId || ''}
                    onChange={(e) => setData({ ...data, defaultRouteNodeId: e.target.value })}
                    margin="normal"
                    size="small"
                  />
                </StyledGrid>
              </StyledGrid>
            )}
          </StyledGrid>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Configure {data.type.charAt(0).toUpperCase() + data.type.slice(1)} Node</DialogTitle>
      <DialogContent>
        <StyledGrid container spacing={2}>
          <StyledGrid item xs={12}>
            <TextField
              fullWidth
              label="Node Label"
              value={data.label}
              onChange={(e) => setData({ ...data, label: e.target.value })}
              margin="normal"
            />
          </StyledGrid>
          {renderFields()}
        </StyledGrid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};
