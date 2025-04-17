export interface MetricCategory {
  enabled: boolean;
  name: string;
  description: string;
  metrics: {
    [key: string]: number | string;
  };
  charts?: {
    type: 'line' | 'bar' | 'pie';
    data: any[];
  }[];
}

export interface Message {
  id: string;
  content: string;
  timestamp: string;
  direction: 'inbound' | 'outbound';
  status: string;
  phoneNumber: string;
}

export interface Conversation {
  id: string;
  messages: Message[];
  phoneNumber: string;
  lastMessageAt: string;
  status: string;
}

export interface SMSMetrics {
  totalMessages: number;
  inboundMessages: number;
  outboundMessages: number;
  averageResponseTime: number;
  deliveryRate: number;
  conversations: Conversation[];
  hourlyActivity: { hour: number; count: number }[];
}

export interface VoiceMetrics {
  totalCalls: number;
  inboundCalls: number;
  outboundCalls: number;
  averageDuration: number;
  successRate: number;
  hourlyActivity: { hour: number; count: number }[];
}

export interface EmailMetrics {
  totalCount: number;
  openRate: number;
  clickRate: number;
  bounceRate: number;
  hourlyActivity: { hour: number; count: number }[];
}

export interface AnalyticsData {
  smsMetrics: SMSMetrics;
  voiceMetrics: VoiceMetrics;
  emailMetrics: EmailMetrics;
  totalInteractions: number;
  customerSatisfaction: number;
  responseTime: number;
  resolutionRate: number;
}
