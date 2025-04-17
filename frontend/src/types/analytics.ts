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
  totalCount: string;
  responseTime: string;
  deliveryRate: number;
  optOutRate: number;
  aiConfidence: number;
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
  sms: SMSMetrics;
  voice: VoiceMetrics;
  email: EmailMetrics;
  overview: {
    totalInteractions: number;
    totalCost: number;
    averageResponseTime: number;
    successRate: number;
  };
  dateRange: {
    start: string;
    end: string;
  };
}
