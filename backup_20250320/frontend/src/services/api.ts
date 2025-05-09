import axios from 'axios';

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
