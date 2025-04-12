import axios from 'axios';
import { EmailConfig as ImportedEmailConfig } from '../types/email';
import { VoiceConfig } from '../types/voice';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API interfaces
export interface MessageRequest {
  to: string;
  message: string;
  type: 'sms' | 'whatsapp' | 'voice' | 'flex';
  mediaUrl?: string;
  aiModel?: string;
  prompt?: string;
}

export interface EmailRequest {
  to: string;
  subject: string;
  templateId?: string;
  templateData?: Record<string, any>;
  content?: string;
  type: 'template' | 'custom' | 'dynamic';
  attachments?: Array<Record<string, any>>;
}

export interface TicketRequest {
  subject: string;
  description: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  type: 'question' | 'incident' | 'problem' | 'task';
  tags?: string[];
  customFields?: Record<string, any>;
  assigneeEmail?: string;
  requesterEmail?: string;
}

export interface WorkflowConfig {
  twilio: Record<string, string>;
  sendgrid: Record<string, string>;
  zendesk: Record<string, string>;
  instructions: string[];
}

export interface EmailTemplate {
  subject: string;
  content: string;
}

export interface EmailConfig {
  integration: {
    sendgridApiKey: string;
    openaiApiKey: string;
    fromEmail: string;
    fromName: string;
  };
  brandTone: {
    voiceType: string;
    greetings: string[];
    wordsToAvoid: string[];
  };
  templates: {
    support: Record<string, EmailTemplate>;
    marketing: Record<string, EmailTemplate>;
    transactional: Record<string, EmailTemplate>;
  };
}

// AI Service
export const analyzeRequirements = async (description: string): Promise<WorkflowConfig> => {
  const { data } = await api.post('/api/ai/analyze', { description });
  return data;
};

// Twilio Service
export const sendTwilioMessage = async (request: MessageRequest) => {
  const { data } = await api.post('/api/twilio/send', request);
  return data;
};

// SendGrid Service
export const sendEmail = async (request: EmailRequest) => {
  const { data } = await api.post('/api/sendgrid/send', request);
  return data;
};

// Zendesk Service
export const createTicket = async (request: TicketRequest) => {
  const { data } = await api.post('/api/zendesk/ticket', request);
  return data;
};

export const updateTicket = async (ticketId: number, updates: Partial<TicketRequest>) => {
  const { data } = await api.put(`/api/zendesk/ticket/${ticketId}`, updates);
  return data;
};

export const addTicketComment = async (ticketId: number, comment: string, isPublic = true) => {
  const { data } = await api.post(`/api/zendesk/ticket/${ticketId}/comment`, { comment, public: isPublic });
  return data;
};

// API Configuration
export const configureEmailAutomation = async (config: ImportedEmailConfig) => {
  const { data } = await api.post('/api/config/email', config);
  return data;
};

// Voice configuration endpoints
export const saveVoiceConfig = async (businessId: string, config: VoiceConfig): Promise<void> => {
  await api.post('/voice/config', {
    businessId,
    config,
  });
};

export const getVoiceConfigs = async (businessId: string): Promise<VoiceConfig[]> => {
  const response = await api.get(`/voice/config/${businessId}`);
  return response.data;
};

export const deleteVoiceConfig = async (phoneNumber: string): Promise<void> => {
  await api.delete(`/voice/config/${phoneNumber}`);
};

// Webhook Configuration
export interface WebhookUrls {
  twilio: string;
  sendgrid: string;
  zendesk: string;
}

export const getWebhookUrls = (): WebhookUrls => {
  return {
    twilio: `${API_URL}/webhooks/twilio/webhook`,
    sendgrid: `${API_URL}/webhooks/sendgrid/webhook`,
    zendesk: `${API_URL}/webhooks/zendesk/webhook`,
  };
};
