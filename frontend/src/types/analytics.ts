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
  createdAt: string;
  direction: 'inbound' | 'outbound';
  status: string;
  phoneNumber: string;
  aiConfidence?: number;
  templateUsed?: string;
}

export interface Conversation {
  id: string;
  startedAt: string;
  topic: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  messageCount: number;
  avgResponseTime: number;
  phoneNumber: string;
  messages: Message[];
}

export interface SMSMetrics {
  totalCount: string;
  responseTime: string;
  deliveryRate: number;
  optOutRate: number;
  aiCost: number;
  serviceCost: number;
  qualityMetrics: Array<{
    date: string;
    sentiment: number;
    quality: number;
  }>;
  responseTypes: Array<{
    type: string;
    count: number;
  }>;
  dailyCosts: Array<{
    date: string;
    ai: number;
    service: number;
    total: number;
  }>;
  hourlyActivity: Array<{
    hour: number;
    count: number;
  }>;
  conversations: Conversation[];
}

export interface VoiceMetrics {
  totalCount: string;
  inboundCalls: number;
  outboundCalls: number;
  averageDuration: number;
  successRate: number;
  hourlyActivity: { hour: number; count: number }[];
}

export interface EmailMetrics {
  totalCount: string;
  responseTime: string;
  openRate: number;
  clickRate: number;
  bounceRate: number;
  hourlyActivity: { hour: number; count: number }[];
}

export interface AnalyticsData {
  sms: SMSMetrics;
  voice: VoiceMetrics;
  email: EmailMetrics;
  overview: {
    totalInteractions: string;
    totalCost: number;
    averageResponseTime: string;
    successRate: number;
  };
  dateRange: {
    start: string;
    end: string;
  };
}
