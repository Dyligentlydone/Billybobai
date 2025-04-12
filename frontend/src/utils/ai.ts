import axios from 'axios';

export interface WorkflowConfig {
  twilio?: {
    type?: string;
    aiEnabled?: boolean;
    templateId?: string;
    subject?: string;
  };
  sendgrid?: {
    type?: string;
    templateId?: string;
    subject?: string;
  };
}

export const analyzeRequirements = async (description: string): Promise<WorkflowConfig> => {
  const { data } = await axios.post('/api/analyze', { description });
  return data;
};
